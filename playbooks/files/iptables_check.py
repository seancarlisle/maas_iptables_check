#!/usr/bin/python2.7

import subprocess

# Maas-specific libraries
from maas_common import metric
from maas_common import metric_bool
from maas_common import print_output
from maas_common import status_ok
from maas_common import status
from maas_common import status_err

def main():
   # Check that bridge sysctl parameters are set
   bridge_params = ["bridge-nf-call-arptables","bridge-nf-call-ip6tables","bridge-nf-call-iptables"]
   bridge_sysctl = True
   bridge_param_metrics = {}
   try:
      for param in bridge_params:
         bridge_param_metrics[param] = str(subprocess.check_output(['cat','/proc/sys/net/bridge/' + param])).rstrip('\n')
         if bridge_param_metrics[param] != "1":
            bridge_sysctl = False
   except Exception as e:
      status_err(str(e))

   # Check that iptables rules are in place
   iptables_rules = ''
   try:
      iptables_rules = str(subprocess.check_output(['iptables','-wL'])).split('\n')
   except Exception as e:
      status_err(str(e))

   iptables_exist = False
   for rule in iptables_rules:
      if "DROP" in rule:
         iptables_exist = True

   if bridge_sysctl == True and iptables_exist == True:
      metric_bool('iptables_status', True, m_name='iptables_active')
      status_ok(m_name='iptables_active')
   else:
      metric_bool('iptables_status', False, m_name='iptables_active')

   metric('bridge-nf-call-arptables', 'int64',
           bridge_param_metrics['bridge-nf-call-arptables'])
   metric('bridge-nf-call-iptables', 'int64',
           bridge_param_metrics['bridge-nf-call-iptables'])
   metric('bridge-nf-call-ip6tables', 'int64',
           bridge_param_metrics['bridge-nf-call-ip6tables'])


if __name__ == '__main__':
    with print_output(print_telegraf=False):
        main()

