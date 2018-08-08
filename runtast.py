'''
    Run commands, base on Python 3.X
    Developer: lhuaizhong@gmail.com
'''

import os,sys
import shutil

import csv

import time

from netmiko import ConnectHandler

from difflib import context_diff, unified_diff
import datetime

import logging
import traceback

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
        cmd = ''
        try:
            isoutput = False
            if 'y' in task[6].lower():
                isoutput = True
            cmd_file = 'commands%s%s.txt' % (os.sep, task[5])
            out_file = 'output%s%s.txt' % (os.sep, task[0])
            out_file_pre = 'output%s%s_pre.txt' % (os.sep, task[0])
            out_file_diff = 'output%s%s_diff.txt' % (os.sep, task[0])
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
            for cmd in commands: ###
                cmd = cmd.strip().replace('\\n','\n')
                print('command>>' + cmd)
                #output = net_connect.send_command(cmd)
                output = net_connect.send_command(cmd, max_loops=10000, auto_find_prompt=False, strip_prompt=False, strip_command=False)
                if len(output)>60:
                    print('output>>' + output[:60]+'...')
                else:
                    print('output>>' + output)
                outputs += [output]
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
