'''
    Run commands, base on Python 3.X
    Developer: lhuaizhong@gmail.com
'''

import os,sys
import shutil

import csv
import json

import time

from netmiko import ConnectHandler

from difflib import context_diff, unified_diff
import datetime

import logging
import traceback

from custom.custom1 import Custom1SSH
#import netmiko

def comparefile(out_file, out_file_pre, out_file_diff):
    fa = open(out_file,'r')
    fb = open(out_file_pre,'r')
    linesa = fa.readlines()
    linesb = fb.readlines()
    linesc = []
    for line in unified_diff(linesb, linesa, fromfile='Before', tofile='Current'):
        #if line.startswith('---') or line.startswith('+++') or line.startswith('@@ '):
        #    continue
        linesc.append(line)
    if linesc:
        linesc = ['\n%s\n@@@ Updated at %s @@@\n' % ('='*40, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))] + linesc
        fc = open(out_file_diff,'a')
        fc.writelines(linesc)
        fc.close()
    fb.close()
    fa.close()

def main():
    start_time = time.clock()
    #print(netmiko.ssh_dispatcher.CLASS_MAPPER)
    #print(ssh_dispatcher.platforms)

    logging.basicConfig(filename='logging.txt', format="%(asctime)s;%(levelname)s;%(message)s", level=logging.DEBUG)

    list_filename = 'tasklist.csv'
    argv = sys.argv
    if len(argv)>1:
        list_filename = argv[1]
    tasks = []
    with open(list_filename,'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            tasks.append(row)
    print('There are %d tasks to run.' % len(tasks))

    for task in tasks: ###
        if not task[0].strip() or not task[2].strip():
            continue
        cmd = ''
        try:
            para = {
                'hostname':task[0],
                'ip':task[2],
                'username':task[3],
            }
            if task[8]:
                #j = json.loads(task[8])
                j = eval(task[8])
                para.update(j)
            isoutput = False
            if 'y' in task[6].lower():
                isoutput = True

            path = task[7].strip() or 'output'
            if not os.path.exists(path):
                os.makedirs(path)
            cmd_file = os.path.join('commands', task[5]+'.txt')
            out_file = os.path.join(path, task[0]+'.txt')
            out_file_pre = os.path.join(path, task[0]+'_pre.txt')
            out_file_diff = os.path.join(path, task[0]+'_diff.txt')
            logging.debug('Run %s to %s using file %s' % (task[0], task[2], cmd_file))
            print('Run %s to %s using file %s' % (task[0], task[2], cmd_file))
            commands = []
            outputs = []
            with open(cmd_file,'r') as f:
                #for line in f:
                #    commands.append(line.strip())
                commands = f.readlines()
            #print('commands:{}'.format(commands))

            # Connect to device.
            net_connect = ConnectHandler(device_type=task[1], ip=task[2], username=task[3], password=task[4])
            #net_connect.set_base_prompt(pri_prompt_terminator=':')
            more = ''
            for cmd in commands: ###
                cmd = cmd.format(**para)
                cmd = cmd.strip().replace('\\n','\n')
                expect_string=''
                if '@@' in cmd:
                    ss = cmd.split('@@')
                    cmd = ss[0]
                    expect_string = ss[1].strip()
                if cmd[:2]=='##':
                    more = cmd[2:].strip()
                    print('Paging string: '+more)
                    continue
                if not expect_string:
                    print('command>>' + cmd)
                else:
                    print('command>> %s  =>%s' % (cmd, expect_string))
                #output = net_connect.send_command(cmd)
                #output = net_connect.send_command(cmd, max_loops=10000, auto_find_prompt=False, strip_prompt=False, strip_command=False, expect_string=expect_string)
                output = net_connect.send_command(cmd, max_loops=100, auto_find_prompt=False, strip_prompt=False, strip_command=False, expect_string=expect_string)
                if len(output)>60:
                    print('output>>' + output[:60]+'...')
                else:
                    print('output>>' + output)
                if not more:
                    outputs += [output]
                else:
                    outputs += [output.replace(more, '')]
                    #outputs += [output]
            net_connect.disconnect()

            # Storing output
            if outputs and isoutput:
                if os.path.exists(out_file):
                    shutil.copy(out_file, out_file_pre)
                with open(out_file, 'w') as f:
                    f.writelines([s+'\n' for s in outputs])
                if os.path.exists(out_file) and os.path.exists(out_file_pre):
                    comparefile(out_file, out_file_pre, out_file_diff)

        except Exception as e:
            if cmd:
                logging.error('Error in running command %s.' % cmd)
                print('Error in running command %s.' % cmd)
            logging.error('Error:%s' % e)
            print('Error:%s' % e)
            traceback.print_exc()

    print('Completed in', time.clock() - start_time, 'seconds')

if __name__ == '__main__':
    main()
