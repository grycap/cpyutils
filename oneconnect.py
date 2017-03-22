# coding: utf-8
#
# CLUES Python utils - Utils and General classes that spin off from CLUES
# Copyright (C) 2015 - GRyCAP - Universitat Politecnica de Valencia
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import os
from xmlobject import XMLObject, XMLObject_KW
import logging
import socket

_LOGGER = logging.getLogger("[ONE]")

class VMS_HOST(XMLObject):
    values_list = [ 'ID' ]

class TEMPLATE(XMLObject_KW):
    values = [ 'ARCH', 'CPUSPEED', 'ERROR', 'HOSTNAME', 'HYPERVISOR', 'MODELNAME', 'NETRX', 'NETTX', 'RESERVED_CPU', 'RESERVED_MEM', 'VERSION']
    numeric = [ 'CPUSPEED', 'NETRX', 'NETTX' ]

class HOST_SHARE(XMLObject_KW):
    values = [ 'DISK_USAGE', 'MEM_USAGE', 'CPU_USAGE', 'MAX_DISK', 'MAX_MEM', 'MAX_CPU', 'FREE_DISK', 'FREE_MEM', 'FREE_CPU', 'USED_DISK', 'USED_MEM', 'USED_CPU', 'RUNNING_VMS' ]
    numeric = [ 'DISK_USAGE', 'MEM_USAGE', 'CPU_USAGE', 'MAX_DISK', 'MAX_MEM', 'MAX_CPU', 'FREE_DISK', 'FREE_MEM', 'FREE_CPU', 'USED_DISK', 'USED_MEM', 'USED_CPU', 'RUNNING_VMS' ]

class HOST(XMLObject):

    INIT = 0 # Initial state for enabled hosts.
    MONITORING_MONITORED = 1 # Monitoring the host (from monitored).
    MONITORED = 2 # The host has been successfully monitored.
    ERROR = 3 # An error ocurrer while monitoring the host.
    DISABLED = 4 # The host is disabled won't be monitored.
    MONITORING_ERROR = 5 # Monitoring the host (from error).
    MONITORING_INIT = 6 # Monitoring the host (from init).
    MONITORING_DISABLED = 7 # Monitoring the host (from disabled).
    OFFLINE = 8 # The host is offline

    ONESTATE_2_STR = {
        INIT : 'down',
        MONITORING_MONITORED: 'free',
        MONITORED: 'free',
        ERROR: 'error',
        DISABLED:'down',
        MONITORING_ERROR: 'down',
        MONITORING_INIT: 'down',
        MONITORING_DISABLED: 'down',
        OFFLINE: 'off'
    }
    
    values = [ 'ID', 'NAME', 'STATE', 'IM_MAD', 'VM_MAD', 'VN_MAD', 'CLUSTER_ID' ]
    numeric = [ 'ID', 'STATE', 'CLUSTER_ID' ]
    tuples = { 'HOST_SHARE': HOST_SHARE, 'VMS': VMS_HOST, 'TEMPLATE': TEMPLATE }
    
    # TEMPLATE_PREDEFINED = { 'NAME':'NAME', 'TOTALCPU':'HOST_SHARE.MAX_CPU', 'TOTALMEMORY':'HOST_SHARE.MAX_MEM', 'FREEMEMORY':'HOST_SHARE.FREE_MEM', 'FREECPU':'HOST_SHARE.FREE_CPU', 'USEDMEMORY':'HOST_SHARE.USED_MEM', 'USEDCPU':'HOST_SHARE.USED_CPU', 'HYPERVISOR':'TEMPLATE.HYPERVISOR' }
    def __init__(self, _str):
        XMLObject.__init__(self, _str)
        self.total_slots = 0
        self.free_slots = 0
        self.memory_total = 0
        self.memory_free = 0
        self.keywords = {}
        self.state = self.ONESTATE_2_STR[self.STATE]
        if self.HOST_SHARE:
            self.total_slots = self.HOST_SHARE.MAX_CPU
            self.free_slots = self.total_slots - self.HOST_SHARE.CPU_USAGE
            self.memory_free = self.HOST_SHARE.MAX_MEM - self.HOST_SHARE.MEM_USAGE
            self.memory_total = self.HOST_SHARE.MAX_MEM
            if (self.state == 'free') and (self.free_slots < self.total_slots):
                    self.state = 'busy'
            self.keywordstr = self.HOST_SHARE.get_kws_string() + self.TEMPLATE.get_kws_string()
        self.keywords = self.HOST_SHARE.get_kws_dict()
        self.keywords.update(self.TEMPLATE.get_kws_dict())

    def __str__(self):
        return "clues_name=\"%s\";clues_state=\"%s\";clues_total_slots=%d;clues_free_slots=%d;clues_memory_free=%d;clues_memory_total=%d;%s" % (self.NAME, self.state, self.total_slots, self.free_slots, self.memory_free, self.memory_total, self.keywordstr)

class HOST_POOL(XMLObject):
    tuples_lists = {'HOST': HOST }

class NIC(XMLObject):
    values = [ 'IP' ]

class TEMPLATE(XMLObject):
    values = [ 'CPU', 'MEMORY', 'TEMPLATE_ID' ]
    numeric = [ 'CPU', 'MEMORY', 'TEMPLATE_ID' ]
    tuples_lists = { 'NIC': NIC }
    numeric_accept_none = [ 'TEMPLATE_ID' ]

class HISTORY(XMLObject):
    values = [ 'SEQ', 'HOSTNAME', 'HID', 'STIME', 'ETIME', 'PSTIME', 'PETIME', 'RSTIME', 'RETIME' ,'ESTIME', 'EETIME', 'REASON' ]

class HISTORY_RECORDS(XMLObject):
    tuples_lists = { 'HISTORY': HISTORY }
    
    def __init__(self, _str):
        XMLObject.__init__(self, _str)
        if self.HISTORY is None:
            self.HISTORY = []

        self.HISTORY.sort(key=lambda x: x.SEQ)

class VM(XMLObject):
    # STATE
    STATE_INIT      = 0
    STATE_PENDING   = 1
    STATE_HOLD      = 2
    STATE_ACTIVE    = 3   # In this state, the Life Cycle Manager state is relevant
    STATE_STOPPED   = 4
    STATE_SUSPENDED = 5
    STATE_DONE      = 6
    STATE_FAILED    = 7
    STATE_POWEROFF  = 8
    STATE_UNDEPLOYED = 9
    STATE_CLONING = 10
    STATE_CLONING_FAILURE = 11    

    # LCM_STATES
    LCM_INIT                = 0
    LCM_PROLOG              = 1
    LCM_BOOT                = 2
    LCM_RUNNING             = 3
    LCM_MIGRATE             = 4
    LCM_SAVE_STOP           = 5
    LCM_SAVE_SUSPEND        = 6
    LCM_SAVE_MIGRATE        = 7
    LCM_PROLOG_MIGRATE      = 8
    LCM_PROLOG_RESUME       = 9
    LCM_EPILOG_STOP         = 10
    LCM_EPILOG              = 11
    LCM_SHUTDOWN            = 12
    LCM_CANCEL              = 13
    LCM_FAILURE             = 14
    LCM_CLEANUP_RESUBMIT    = 15
    LCM_UNKNOWN             = 16
    LCM_HOTPLUG             = 17
    LCM_SHUTDOWN_POWEROFF   = 18
    LCM_BOOT_UNKNOWN        = 19
    LCM_BOOT_POWEROFF       = 20
    LCM_BOOT_SUSPENDED      = 21
    LCM_BOOT_STOPPED        = 22
    LCM_CLEANUP_DELETE      = 23
    LCM_HOTPLUG_SNAPSHOT    = 24
    LCM_HOTPLUG_NIC         = 25
    LCM_HOTPLUG_SAVEAS           = 26
    LCM_HOTPLUG_SAVEAS_POWEROFF  = 27
    LCM_HOTPLUG_SAVEAS_SUSPENDED = 28
    LCM_SHUTDOWN_UNDEPLOY   = 29
    LCM_EPILOG_UNDEPLOY     = 30
    LCM_PROLOG_UNDEPLOY     = 31
    LCM_BOOT_UNDEPLOY       = 32

    values = [ 'ID', 'STATE', 'LCM_STATE', 'UID', 'GID' ]
    numeric = [ 'ID', 'STATE', 'LCM_STATE', 'UID', 'GID' ]
    tuples = { 'TEMPLATE': TEMPLATE, 'HISTORY_RECORDS': HISTORY_RECORDS }

    def get_ips(self):
        ips = []
        if self.TEMPLATE and self.TEMPLATE.NIC:
            for nic in self.TEMPLATE.NIC:
                ips.append(nic.IP)
        return ips

class VM_POOL(XMLObject):
    tuples_lists = { 'VM': VM}

class VMTEMPLATE(XMLObject):
    values = [ 'ID', 'NAME' ] 

class VMTEMPLATE_POOL(XMLObject):
    tuples_lists = { 'VMTEMPLATE': VMTEMPLATE}

class ONEConnect():
    def __init__(self, ONE_XMLRPC, ONE_AUTH, timeout = None):
        self._ONE_XMLRPC = ONE_XMLRPC
        self._ONE_AUTH = ONE_AUTH
        self._server = None
        self._version = None
        self._version_num = [ 0, 0 ]
        self._timeout = timeout

    def migrate_vm(self, vmid, hostid, live):
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.vm.migrate(self._ONE_AUTH, vmid, hostid, live, True)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False
            except:
                errno = -1
                result = False

            if not result:
                _LOGGER.debug("could not migrate VM %s to host %s (errno: %s)" % (vmid, hostid, errno))
                return False
            return True
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return False
    
    def get_hosts(self):
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.hostpool.info(self._ONE_AUTH)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return None
            except:
                errno = -1
                result = False
            
            if not result:
                _LOGGER.debug("could not obtain hosts from ONE (errno: %s)" % errno)
                return None
            return HOST_POOL(str_out).HOST
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return None

    def get_vms(self, get_only_owned_vms = False):
        if self.get_server_ref():
            try:
                retrieval_val = -2
                if get_only_owned_vms:
                    retrieval_val = -3
                result, str_out, errno = self._server.one.vmpool.info(self._ONE_AUTH, retrieval_val, -1, -1, -1)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return None
            except:
                errno = -1
                result = False
            
            if not result:
                _LOGGER.debug("could not obtain vms from ONE (errno: %s)" % errno)
                return None
            
            return VM_POOL(str_out).VM
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return None
        
    def get_templates(self):
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.templatepool.info(self._ONE_AUTH, -2, -1, -1)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return None
            except:
                errno = -1
                result = False
            
            if not result:
                _LOGGER.debug("could not obtain templates from ONE (errno: %s)" % errno)
                return None
            return VMTEMPLATE_POOL(str_out).VMTEMPLATE
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return None
        
    def create_vm_by_template(self, template_str):
        if self.get_server_ref():
            try:
                if int(self._version[0]) < 4:
                    result, str_out, errno = self._server.one.vm.allocate(self._ONE_AUTH, template_str)
                else:
                    result, str_out, errno = self._server.one.vm.allocate(self._ONE_AUTH, template_str, False)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False, "call to ONE timed out"
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False
            
            if not result:
                _LOGGER.debug("could not create VM (errno: %s [%s])" % (errno, str_out))
                return False, "could not create VM (errno: %s [%s])" % (errno, str_out)

            try:
                vm_id = int(str_out)
            except:
                _LOGGER.error("an error happened during the interaction with ONE (could not get the new VM id)")
                vm_id = None
                return False, "an error happened during the interaction with ONE (could not get the new VM id)"

            try:
                result, str_out, errno = self._server.one.vm.info(self._ONE_AUTH, vm_id)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False, "call to ONE timed out"
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False

            if not result:
                _LOGGER.debug("could not get info about recently created VM (%s) (errno: %s)" % (str_out, errno))
                return False, "could not get info about recently created VM (%s) (errno: %s)" % (str_out, errno)
            
            return True, VM(str_out)
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return False, "could not connect ONE server"
        
    def create_vm(self, template):
        if self.get_server_ref():
            templates = self.get_templates()
            if templates is None: return False, "User does not have access to ONE templates"

            t_id = None
            for t in templates:
                if (str(t.ID) == str(template)) or (t.NAME == str(template)):
                    t_id = t.ID
                    break
            try:
                if t_id is not None: t_id = int(t_id)
            except:
                pass

            if t_id is None:
                _LOGGER.debug("user does not have access to template %s" % template)
                return False, "user does not have access to template %s" % template

            try:                
                result, str_out, errno = self._server.one.template.instantiate(self._ONE_AUTH, t_id, "", False, "")
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False, "call to ONE timed out"
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False
                
            if not result:
                _LOGGER.debug("could not instantiate VM (errno: %s [%s])" % (errno, str_out))
                return False, "could not instantiate VM (errno: %s [%s])" % (errno, str_out)

            try:
                vm_id = int(str_out)
            except:
                _LOGGER.error("an error happened during the interaction with ONE (could not get the new VM id)")
                vm_id = None
                return False, "an error happened during the interaction with ONE (could not get the new VM id)"

            try:
                result, str_out, errno = self._server.one.vm.info(self._ONE_AUTH, vm_id)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False, "call to ONE timed out"
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False

            if not result:
                _LOGGER.debug("could not get info about recently created VM (%s) (errno: %s)" % (str_out, errno))
                return False, "could not get info about recently created VM (%s) (errno: %s)" % (str_out, errno)
            
            return True, VM(str_out)
        else:
            _LOGGER.debug("could not contact to the ONE server")
            return False, "could not connect ONE server"

    def vm_delete(self, vm_id):
        return self._action_on_vm(vm_id, "delete")

    def vm_shutdown(self, vm_id):
        return self._action_on_vm(vm_id, "shutdown")

    def vm_hold(self, vm_id):
        return self._action_on_vm(vm_id, "hold")

    def vm_release(self, vm_id):
        return self._action_on_vm(vm_id, "release")

    def vm_reboot(self, vm_id):
        return self._action_on_vm(vm_id, "reboot")

    def vm_reboot_hard(self, vm_id):
        if int(self._version[0]) < 4:
            return self.vm_reboot(vm_id)
        return self._action_on_vm(vm_id, "reboot-hard")

    def vm_poweroff(self, vm_id):
        return self._action_on_vm(vm_id, "poweroff")

    def vm_poweroff_hard(self, vm_id):
        if int(self._version[0]) < 4:
            return self.vm_poweroff(vm_id)
        return self._action_on_vm(vm_id, "poweroff-hard")

    def host_enable(self, host_id):
        return self._enable_host(host_id, True)

    def host_disable(self, host_id):
        return self._enable_host(host_id, False)

    def _enable_host(self, host_id, enable = True):
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.host.enable(self._ONE_AUTH, host_id, enable)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False
            
            if not result:
                _LOGGER.debug("could not enable or disable Host %d (errno: %s [%s])" % (host_id, errno, str_out))
                return False
            return True
        else:
            return False

    def _action_on_vm(self, vm_id, action):
        if action not in [ "delete", "shutdown", "hold", "release", "reboot", "reboot-hard", "poweroff", "poweroff-hard" ]:
            _LOGGER.warning("called unkonwn action %s for vm %d" % (action, vm_id))
            return False
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.vm.action(self._ONE_AUTH, action, vm_id)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False
            
            if not result:
                _LOGGER.debug("could not actuate over VM %d (errno: %s [%s])" % (vm_id, errno, str_out))
                return False
            return True
        else:
            return False

    def migrate_vm(self, vm_id, hid, live = True):
        if self.get_server_ref():
            try:
                result, str_out, errno = self._server.one.vm.migrate(self._ONE_AUTH, vm_id, hid, live, True)
            except socket.timeout:
                result = False
                _LOGGER.debug("call to ONE timed out")
                return False
            except:
                errno = -1
                str_out = "error obtaining info from ONE"
                result = False
            
            if not result:
                _LOGGER.debug("could not migrate VM %d to host %d (errno: %s [%s])" % (vm_id, hid, errno, str_out))
                return False
            return True
        else:
            return False

    def get_server_ref(self):
        if (self._server is not None):
            return True
        try:
            if self._timeout is None:
                import xmlrpclib
                self._server = xmlrpclib.ServerProxy(self._ONE_XMLRPC)
            else:
                import timeoutxmlrpccli
                self._server = timeoutxmlrpccli.ServerProxy(self._ONE_XMLRPC, timeout = self._timeout)
                
            try:
                methods = self._server.system.listMethods()
            except socket.timeout:
                methods = []

            # Trying to
            if "one.system.version" in methods:
                # version is ONE 3.8 or later
                self._version = "3.8"
                try:
                    (success, self._version, _) = self._server.one.system.version(self._ONE_AUTH)
                except socket.timeout:
                    success = False
                    if "one.vm.attachnic" in methods:
                        self._version = "4.0"
                except:
                    success = False
                    
                if not success:
                    _LOGGER.error("could not get ONE version... perhaps the user is not valid?")
                    return False
            else:
                if "one.template.clone" in methods:
                    self._version = "3.6"
                elif "one.cluster.info" in methods:
                    self._version = "3.4"
                elif "one.vm.chmod" in methods:
                    self._version = "3.2"
                elif "one.acl.info" in methods:
                    self._version = "3.0"
                else:
                    self._version = "2.0"
                    
            self._version = self._version.split(".")
            _LOGGER.debug("OpenNebula version: %s" % ".".join(self._version))
            return True
        except Exception, e:
            self._server = None
            self._version = None
            return False