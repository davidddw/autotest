#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Created on 2014-4-3
# @author: david_dong

import os
import utils
import sys
import re
import paramiko
import traceback
import select
from string import Template 

def execute_remote_cmd(hostname, password, cmd, username='root',
        port=22, bufsize=-1,timeout = 1200):
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)
        print('*** Connecting %s ...' % hostname)
        #stdin, stdout, stderr = client.exec_command(cmd)
        channel = client.get_transport().open_session()
        channel.set_combine_stderr(True)
        channel.setblocking(0)
        channel.settimeout(timeout)
        channel.get_pty()     
        channel.invoke_shell()
        print('Execute command: %s ...' % cmd)
        channel.send(cmd+'\n')
        while True:
            try:
                rl, wl, xl = select.select([channel],[],[],0.0)
                if len(rl) > 0:
                    x = channel.recv(1024)
                    if len(x) == 0:
                        sys.stdout.write('*** Command Completed ! ***\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                    
            except KeyboardInterrupt:
                print("Caught control-C")
                channel.close()    
                client.close()
                exit(0)
                
    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        traceback.print_exc()
        try:
            client.close()
        except:
            pass
        sys.exit(1)
        
def upload_file_cmd(hostname, password, local, remote, username='root',
        port=22, verbose=False):
    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        print("Upload file: %s " % local)
        sftp.put(local, remote)
        t.close()

    except Exception as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)

def download_file_cmd(hostname, password, remote, local, username='root',
        port=22, verbose=False):
    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        print("Download file: %s " % local)
        sftp.get(remote, local)
        t.close()

    except Exception as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)
    
def execute_single_cmd(hostname, password, cmd, username='root',
        port=22, verbose=False):

    result = {
        'stdout': [],
        'stderr': [],
    }
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password)

        chan = client.get_transport().open_session()
        chan.settimeout(5)
        #stdin = chan.makefile('wb')
        stdout = chan.makefile('rb')
        stderr = chan.makefile_stderr('rb')
        chan.exec_command(cmd)
        result['exit_status'] = chan.recv_exit_status()

        def get_output():
            for line in stdout:
                result['stdout'].append(line)
                if verbose:
                    print line,
            for line in stderr:
                result['stderr'].append(line)
                if verbose:
                    print line,

        if verbose:
            print cmd
        get_output()

    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        traceback.print_exc()
        try:
            client.close()
        except:
            pass
        sys.exit(1)
    return result

def read_ssh_config(filename):
    filename = os.path.join(utils.check_dir_exist('conf'), filename)
    ssh = {}
    ssh['host'] = utils.read_conf_from_conf(filename, 'ssh', 'ssh_host')
    ssh['pass'] = utils.read_conf_from_conf(filename, 'ssh', 'ssh_pass')
    ssh['cmd'] = utils.read_conf_from_conf(filename, 'ssh', 'ssh_cmd')
    ssh['url'] = utils.read_conf_from_conf(filename, 'ssh', 'url')
    return ssh

def operate_exec():
    ssh = read_ssh_config('system.conf')
    execute_remote_cmd(ssh['host'], ssh['pass'], ssh['cmd'])
    
def operate_upload(local, remote):
    ssh = read_ssh_config('system.conf')
    localfile = os.path.join(utils.check_dir_exist('conf'), local)
    upload_file_cmd(ssh['host'], ssh['pass'], localfile, remote)

def operate_download(remote, local):
    ssh = read_ssh_config('system.conf')
    localfile = os.path.join(utils.check_dir_exist('download'), local)
    download_file_cmd(ssh['host'], ssh['pass'], remote, localfile)
    
def get_tar_log_from_url(url=None):
    ssh = read_ssh_config('system.conf')
    if url == None:
        url = ssh['url']
    returnvalue = {}
    returnvalue['url'] = url
    returnvalue['tarfile'] = re.split(r"/",url)[-1]
    pattern = re.compile(r'(?P<sign>.*).tar.gz', re.DOTALL)
    returnvalue['logfile'] = re.findall(pattern, returnvalue['tarfile'])[0]+'.log'
    return returnvalue
    
def generate_install(**karg):
    filename = os.path.join(utils.check_dir_exist('conf'), 'install.sh.in')
    newfilename = os.path.join(utils.check_dir_exist('conf'), 'install.sh')
    with open(filename) as tempfile:
        content = Template(tempfile.read())
    with open(newfilename, 'w') as newfile:
        newfile.write(content.substitute(**karg))
    
if __name__ == "__main__":
    tar_log = get_tar_log_from_url()
    generate_install(**tar_log)
    operate_upload('install.sh','/root/install.sh')
    operate_exec()
    operate_download('/tmp/'+tar_log['logfile'], tar_log['logfile'])
