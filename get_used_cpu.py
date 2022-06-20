import re
import libvirt
import time
import os
import sys
from prettytable import PrettyTable


def get_cpu_info():
    with libvirt.open('qemu:///system') as conn:
        if conn is None:
            print('Failed to open connection to qemu:///system')
            sys.exit(1)
        if len(conn.listDomainsID()) <= 0:
            print('No VM is running, exit')
            time.sleep(1)
            sys.exit()
        instance_cpu_info = {}
        try:
            for id in reversed(conn.listDomainsID()):
                domain = conn.lookupByID(id)
                instance_uuid = domain.UUIDString()
                cpulist = []
                cpus_info = domain.vcpus()
                for cpus in cpus_info[0]:
                    cpulist.append(cpus[3])
                instance_cpu_info[instance_uuid] = cpulist
        except libvirt.libvirtError as e:
            print(repr(e), file=sys.stderr)
            exit(1)
        return instance_cpu_info


def show_as_PT(instance_cpu_info):
    pt = PrettyTable()
    pt.field_names = ['UUID', 'CPUs']
    for uuid, cpus in instance_cpu_info.items():
        pt.add_row([uuid, ','.join(map(str, cpus))])
    print(pt)


if __name__ == '__main__':
    show_as_PT(get_cpu_info())
