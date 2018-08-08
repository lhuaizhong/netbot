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

import argparse

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

def check(ip, device_type, username, password, commands=None, cmd_file=None, verbose=True):

    #logging.basicConfig(filename='logging.txt', format="%(asctime)s;%(levelname)s;%(message)s", level=logging.DEBUG)
    rt = 'success'
    try:
        if commands:
            commands = [commands]
        else:
            commands = []
        
        outputs = []
        if cmd_file:
            with open(cmd_file,'r') as f:
                #for line in f:
                #    commands.append(line.strip())
                commands = f.readlines()
            #print('commands:{}'.format(commands))

        # Connect to device.
        net_connect = ConnectHandler(device_type=device_type, ip=ip, username=username, password=password)
        for cmd in commands: ###
            cmd = cmd.strip().replace('\\n','\n')
            if verbose:
                print('command>>' + cmd)
            #output = net_connect.send_command(cmd)
            output = net_connect.send_command(cmd, max_loops=10000, auto_find_prompt=False, strip_prompt=False, strip_command=False)
            if verbose:
                if len(output)>60:
                    print('output>>' + output[:60]+'...')
                else:
                    print('output>>' + output)
            outputs += [output]
        net_connect.disconnect()

    except Exception as e:
        #if cmd:
        #    logging.error('Error in running command %s.' % cmd)
        #    print('Error in running command %s.' % cmd)
        #logging.error('Error:%s' % e)
        print('Error:%s' % e)
        #traceback.print_exc()
        rt = 'failed'
    return rt

if __name__ == '__main__':
    #start_time = time.clock()
    parser = argparse.ArgumentParser(description='Test connect to device.')
    parser.add_argument('ip')
    parser.add_argument('device_type')
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('-c', help='Commands sent to device.')
    parser.add_argument('-f', help='Commands file sent to device.')
    args = parser.parse_args()
    #print(args)
    #print(args.ip)

    rt = check(args.ip, args.device_type, args.username, args.password, args.c, args.f)
    print(rt)
    #print('Completed in', time.clock() - start_time, 'seconds')
