#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Created on 2014-4-3
# @author: david_dong

import XenAPI
import utils
import pprint
import xen_utils

__all__ = ['ApiCaller']

class XenController(object):
    def __init__(self, url=None, username=None, password=None):
        self._logger = utils.CloudLog(__name__, 'api.log', utils.DEBUG)
        self.session = XenAPI.Session(url)
        self.session.xenapi.login_with_password(username, password)
        self._logger.debug('Connect %s...' % url)
        
    def get_all_vms(self):
        return self.session.xenapi.VM.get_all()
    
    def get_vm_by_name_label(self, name):
        return self.session.xenapi.VM.get_by_name_label(name)
    
    def reboot_vm(self, vm_name):
        xen_utils.shutdown_vm(self.session, vm_name)
        return xen_utils.start_vm(self.session, vm_name)

    def start_vm(self, vm_name):
        return xen_utils.start_vm(self.session, vm_name)
        
    def shutdown_vm(self, vm_name):
        return xen_utils.shutdown_vm(self.session, vm_name)
        
    def list_all_vms(self):
        return xen_utils.list_all_vms(self.session)
    
    def list_running_vms(self):
        return xen_utils.list_running_vms(self.session)
        
    def list_stopped_vms(self):
        return xen_utils.list_stopped_vms(self.session)
    
    def list_template_by_name(self, template_name):
        return xen_utils.list_template_by_name(self.session, template_name)      
    
    def list_all_templates(self):
        return xen_utils.list_all_templates(self.session)
    
    def list_default_sr(self):
        return xen_utils.list_default_sr(self.session)
        
    def create_vm(self, template_name, vm_name):
        return xen_utils.start_vm(self.session, vm_name)
                    
    def list_snapshot(self, vm_name):
        return xen_utils.list_snapshot(self.session, vm_name)
     
    def take_snapshot(self, vm_name, snapshot_name):
        return xen_utils.take_snapshot(self.session, vm_name, snapshot_name)
        
    def revert_snapshot(self, vm_name, snapshot_name):
        return xen_utils.revert_snapshot(self.session, vm_name, snapshot_name)
    
def read_xen_config(filename):
    import os
    filename = os.path.join(utils.get_parent_path(), 'conf', filename)
    xen = {}
    xen['host'] = utils.read_conf_from_conf(filename, 'xen', 'xen_host')
    xen['user'] = utils.read_conf_from_conf(filename, 'xen', 'xen_user')
    xen['pass'] = utils.read_conf_from_conf(filename, 'xen', 'xen_pass')
    xen['vm'] = utils.read_conf_from_conf(filename, 'xen', 'xen_vm')
    xen['snap'] = utils.read_conf_from_conf(filename, 'xen', 'xen_snap')
    return xen

def revert_and_boot():
    xen = read_xen_config('system.conf')
    api_controller = XenController(xen['host'],xen['user'],xen['pass'])
    vm_name = xen['vm']
    snapshot_name = xen['snap']
    pprint.pprint(api_controller.revert_snapshot(vm_name, snapshot_name))
    pprint.pprint(api_controller.start_vm(vm_name))
    
def take_snapshot():
    xen = read_xen_config('system.conf')
    api_controller = XenController(xen['host'],xen['user'],xen['pass'])
    vm_name = xen['vm']
    snapshot_name = xen['snap']
    pprint.pprint(api_controller.take_snapshot(vm_name, snapshot_name))

if __name__ == "__main__":
    revert_and_boot()
    #take_snapshot()
