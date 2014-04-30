#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
# Created on 2014-4-3
# @author: david_dong

import sys
import time
import utils

logger = utils.CloudLog(__name__, 'api.log', utils.DEBUG)

def get_all_vms(session):
    return session.xenapi.VM.get_all()
    
def get_vm_by_name_label(session, name):
    return session.xenapi.VM.get_by_name_label(name)

def start_vm(session, vm_name):
    vm_ref = session.xenapi.VM.get_by_name_label(vm_name)
    if vm_ref is None:
        logger.error('Could not find Resource. Exitting')
        sys.exit(1)
    vm_ref = vm_ref[0]
    logger.debug('Starting VM %s ...' % vm_name)
    record = session.xenapi.VM.get_record(vm_ref)
    if record["power_state"] == "Running":
        logger.error('VM is already running. Exitting')
        sys.exit(1)
    task = session.xenapi.Async.VM.start(vm_ref, False, True)
    task_record = session.xenapi.task.get_record(task)
    returnvalue = task_record['uuid']
    while session.xenapi.task.get_status(task) == "pending":
        time.sleep(1)
    logger.debug('Running VM %s ...' % vm_name)
    session.xenapi.task.destroy(task)
    logger.debug('task uuid is %s' % returnvalue)
    return returnvalue
        
def shutdown_vm(session, vm_name):
    vm_ref = session.xenapi.VM.get_by_name_label(vm_name)
    if vm_ref is None:
        logger.error('Could not find Resource. Exitting')
        sys.exit(1)
    vm_ref = vm_ref[0]
    logger.debug('Stopping VM %s ...' % vm_name)
    record = session.xenapi.VM.get_record(vm_ref)
    if record["power_state"] == "Halted":
        logger.error('VM is already running. Exitting')
        sys.exit(1)
    task = session.xenapi.Async.VM.clean_shutdown(vm_ref)
    task_record = session.xenapi.task.get_record(task)
    returnvalue = task_record['uuid']
    while session.xenapi.task.get_status(task) == "pending":
        time.sleep(1)
    logger.debug('Stopped VM %s ...' % vm_name)
    session.xenapi.task.destroy(task)
    logger.debug('task uuid is %s' % returnvalue)
    return returnvalue
        
def list_all_vms(session):
    vms_ref = session.xenapi.VM.get_all()
    vms = []
    for vm_ref in vms_ref:
        record = session.xenapi.VM.get_record(vm_ref)
        if not(record["is_a_template"]) and \
            not(record["is_control_domain"]):
            vm_dict = {}
            vm_dict['uuid'] = record['uuid']
            vm_dict['name_label'] = record['name_label']
            vm_dict['power_state'] = record["power_state"] 
            vm_dict['resident_on'] = record['resident_on']
            vm_dict['vm_ref'] = vm_ref
            vms.append(vm_dict)
    return vms  
    
def list_running_vms(session):
    vms_ref = session.xenapi.VM.get_all()
    vms = []
    for vm_ref in vms_ref:
        record = session.xenapi.VM.get_record(vm_ref)
        if not(record["is_a_template"]) and \
            not(record["is_control_domain"]) and \
            record["power_state"] == "Running":
            vm_dict = {}
            vm_dict['uuid'] = record['uuid']
            vm_dict['name_label'] = record['name_label']
            vm_dict['power_state'] = record["power_state"] 
            vm_dict['resident_on'] = record['resident_on']
            vm_dict['vm_ref'] = vm_ref
            vms.append(vm_dict)
    return vms    
        
def list_stopped_vms(session):
    vms_ref = session.xenapi.VM.get_all()
    vms = []
    for vm_ref in vms_ref:
        record = session.xenapi.VM.get_record(vm_ref)
        if not(record["is_a_template"]) and \
            not(record["is_control_domain"]) and \
            record["power_state"] == "Halted":
            vm_dict = {}
            vm_dict['uuid'] = record['uuid']
            vm_dict['name_label'] = record['name_label']
            vm_dict['power_state'] = record["power_state"] 
            vm_dict['vm_ref'] = vm_ref
            vms.append(vm_dict)
    return vms
    
def list_template_by_name(session, template_name):
    vms_ref = session.xenapi.VM.get_all()
    vms = []
    for vm_ref in vms_ref:
        record = session.xenapi.VM.get_record(vm_ref)
        if record["is_a_template"] and \
            not(record["is_control_domain"]) and \
            record["name_label"] == template_name:
            vm_dict = {}
            vm_dict['uuid'] = record['uuid']
            vm_dict['name_label'] = record['name_label']
            vm_dict['vm_ref'] = vm_ref
            vms.append(vm_dict)
    return vms       
    
def list_all_templates(session):
    vms_ref = session.xenapi.VM.get_all()
    vms = []
    for vm_ref in vms_ref:
        record = session.xenapi.VM.get_record(vm_ref)
        if record["is_a_template"] and \
            not(record["is_control_domain"]):
            vm_dict = {}
            vm_dict['uuid'] = record['uuid']
            vm_dict['name_label'] = record['name_label']
            vm_dict['vm_ref'] = vm_ref
            vms.append(vm_dict)
    return vms   
    
def list_default_sr(session):
    pool = session.xenapi.pool.get_all()
    if pool == []:
        logger.error('Could not find default SR. Exitting')
        sys.exit(1)
    sr_dict = {}
    default_sr = session.xenapi.pool.get_default_SR(pool[0])
    sr_record = session.xenapi.SR.get_record(default_sr)
    sr_dict['uuid'] = sr_record['uuid']
    sr_dict['name_label'] = sr_record['name_label']
    sr_dict['sr_ref'] = default_sr
    return sr_dict
        
def create_vm_from_template(session, template_name, vm_name):
    pifs = session.xenapi.PIF.get_all_records()
    lowest = None
    for pifRef in pifs.keys():
        if (lowest is None) or \
            (pifs[pifRef]['device'] < pifs[lowest]['device']):
            lowest = pifRef
    logger.debug('Choosing PIF with device: %s' % pifs[lowest]['device'])  
        
    network = session.xenapi.PIF.get_network(lowest)
    logger.debug('Chosen PIF is connected to network: %s' %
                    session.xenapi.network.get_name_label(network))
        
    logger.debug('Choosing a template to clone')
        
    templates = list_template_by_name(template_name)
    if templates == []:
        logger.error('Could not find %s templates. Exitting' % template_name)
        sys.exit(1)
    template = templates[0]['vm_ref']
    logger.debug("Choosing an SR to instaniate the VM's disks")
    default_sr = list_default_sr(session)['sr_ref']   
    logger.debug("Installing new VM from the template")
    vm_ref = session.xenapi.VM.copy(template, vm_name, default_sr)
    
    logger.debug("New VM has name: %s" % vm_name)
    logger.debug("Creating VIF") 
        
    vif = { 'device': '0',
            'network': network,
            'VM': vm_ref,
            'MAC': "",
            'MTU': "1500",
            "qos_algorithm_type": "",
            "qos_algorithm_params": {},
            "other_config": {} }
    session.xenapi.VIF.create(vif)
    logger.debug('Adding noniteractive to the kernel commandline')
    session.xenapi.VM.set_PV_args(vm_ref, "noninteractive")
    session.xenapi.VM.provision(vm_ref)
    logger.debug("Starting VM")
    session.xenapi.VM.start(vm_ref, False, True)
    logger.debug("VM is booting")  
    print "Waiting for the installation to complete"
                   
def list_snapshot(session, vm_name):
    vm_ref = session.xenapi.VM.get_by_name_label(vm_name)[0]
    record = session.xenapi.VM.get_record(vm_ref)
    snapshots = []
    for snapshot in record["snapshots"]:
        snapshot_dict = {}
        snapshot_record = session.xenapi.VM.get_record(snapshot)
        snapshot_dict['name_label'] = snapshot_record['name_label']
        snapshot_dict['snapshot_time'] = snapshot_record["snapshot_time"]
        snapshot_dict['snapshot'] = snapshot
        snapshots.append(snapshot_dict)
    return snapshots
     
def take_snapshot(session, vm_name, snapshot_name):
    vm_ref = session.xenapi.VM.get_by_name_label(vm_name)[0]
    task = session.xenapi.Async.VM.snapshot(vm_ref, snapshot_name)
    task_record = session.xenapi.task.get_record(task)
    returnvalue = task_record['uuid']
    while session.xenapi.task.get_status(task) == "pending":
        time.sleep(1)
    logger.debug('VM %s snapshot is ok.' % snapshot_name)
    session.xenapi.task.destroy(task)
    logger.debug('task uuid is %s' % returnvalue)
    return returnvalue
        
def revert_snapshot(session, vm_name, snapshot_name):
    vm_ref = session.xenapi.VM.get_by_name_label(vm_name)[0]
    records = session.xenapi.VM.get_record(vm_ref)
    for snapshot in records["snapshots"]:
        snapshot_record = session.xenapi.VM.get_record(snapshot)
        if (snapshot_name == snapshot_record["name_label"]):
                my_snapshot = snapshot
    session.xenapi.VM.revert(my_snapshot)
    task = session.xenapi.Async.VM.revert(my_snapshot)
    task_record = session.xenapi.task.get_record(task)
    returnvalue = task_record['uuid']
    while session.xenapi.task.get_status(task) == "pending":
        time.sleep(1)
    logger.debug('VM %s revert snapshot is ok.' % snapshot_name)
    session.xenapi.task.destroy(task)
    logger.debug('task uuid is %s' % returnvalue)
    return returnvalue
        