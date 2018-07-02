#!/usr/bin/python2.7

import subprocess

# Maas-specific libraries
from maas_common import metric
from maas_common import metric_bool
from maas_common import print_output
from maas_common import status_ok
from maas_common import status
from maas_common import status_err
from maas_common import MaaSException
import libvirt

def main():
   # Check if there are instances on this host. If not, we don't care and just pass the check
   lvConn = libvirt.openReadOnly("qemu:///system")
   if lvConn is None:
      msg = "Cannot connect to libvirt!"
      raise MaasException(msg)
   else:
      domainIDs = lvConn.listDomainsID()
      iptables_exist = False
      bridge_params = ["bridge-nf-call-arptables","bridge-nf-call-ip6tables","bridge-nf-call-iptables"]
      bridge_sysctl = True
      bridge_param_metrics = {}
       
      if domainIDs is not None:
         # Check that bridge sysctl parameters are set
     #    bridge_params = ["bridge-nf-call-arptables","bridge-nf-call-ip6tables","bridge-nf-call-iptables"]
     #    bridge_sysctl = True
     #    bridge_param_metrics = {}
         try:
            for param in bridge_params:
               bridge_param_metrics[param] = str(subprocess.check_output(['cat','/proc/sys/net/bridge/' + param])).rstrip('\n')
               if bridge_param_metrics[param] != "1":
                  bridge_sysctl = False
         except Exception as e:
            status('error',str(e),force_print=False)

         # Check that iptables rules are in place
         iptables_rules = ''
         try:
            iptables_rules = str(subprocess.check_output(['iptables-save'])).split('\n')
         except Exception as e:
            status('error',str(e),force_print=False)

         iptables_exist = False
         for rule in iptables_rules:
            if "DROP" in rule:
               iptables_exist = True
      else:
         # Forcing check to return true since there are no instances on this host.
         for param in bridge_params:
            bridge_param_metrics[param] = "1"
         bridge_sysctl = True
         iptables_exist = True

   if bridge_sysctl == True and iptables_exist == True:
      metric_bool('iptables_status', True, m_name='iptables_active')
      status_ok(m_name='iptables_active')
   else:
      metric_bool('iptables_status', False, m_name='iptables_active')

   metric('bridge-nf-call-arptables', 'int64',
           bridge_param_metrics.get('bridge-nf-call-arptables',0))
   metric('bridge-nf-call-iptables', 'int64',
           bridge_param_metrics.get('bridge-nf-call-iptables',0))
   metric('bridge-nf-call-ip6tables', 'int64',
           bridge_param_metrics.get('bridge-nf-call-ip6tables',0))


if __name__ == '__main__':
    with print_output(print_telegraf=False):
        main()

