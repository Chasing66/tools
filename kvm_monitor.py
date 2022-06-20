#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author: Shawn Wang
# date: 2022/05/27

import libvirt
import time
import os
import sys
from prettytable import PrettyTable
import argparse

args = argparse.ArgumentParser(description='Libvirt Monitor Tool')
args.add_argument('-i', '--interval', type=int,
                  default=6, help='The query interval')
args = args.parse_args()


def get_instance_info():
    with libvirt.open('qemu:///system') as conn:
        if conn is None:
            print('Failed to open connection to qemu:///system')
            sys.exit(1)
        if len(conn.listDomainsID()) <= 0:
            print('\033[0;37;41m%s\033[0m' % 'No VM is running, exit')
            os.system('command')
            time.sleep(1)
            sys.exit()
        datas = []
        try:
            for id in reversed(conn.listDomainsID()):
                domain = conn.lookupByID(id)
                instance_name = f'\033[0;37;44m{domain.name()}\033[0m'
                power_status = f"\033[0;37;44m{'ON' if domain.isActive() else 'OFF'}\033[0m"
                max_memory = f'{domain.maxMemory()/1024}M'
                memory_info = domain.memoryStats()
                free_memory = int(memory_info['unused'])
                total_memory = int(memory_info['available'])
                memory_usage = f'{((total_memory - free_memory)/total_memory*100):.2f}%'
                vcpu_number = int(f'{domain.maxVcpus()}')
                cpu_time = time.strftime('%H:%M:%S', time.localtime(
                    domain.getCPUStats(True)[0]['cpu_time']))
                # get cpu usage
                t1 = time.time()
                c1 = domain.getCPUStats(True)[0]['cpu_time']
                time.sleep(1)
                t2 = time.time()
                c2 = domain.getCPUStats(True)[0]['cpu_time']
                cpu_usage = (c2 - c1) / ((t2 - t1) * vcpu_number * 1e9) * 100
                cpu_usage = f'{cpu_usage:.2f}%'
                data = [instance_name, power_status, max_memory,
                        memory_usage, vcpu_number, cpu_time, cpu_usage]
                datas.append(data)
        except Exception as e:
            print(e)
        return datas


def print_as_table(datas, header=None, title=None):
    """Print data as table."""
    if header is None:
        header = datas[0].keys()
    table = PrettyTable()
    if title is not None:
        table.title = title
    table.field_names = header
    for data in datas:
        table.add_row(data)
    os.system('clear')
    print(f'Press Ctrl+C to exit, refresh every {args.interval} seconds\n')
    sys.stdout.write("{0}".format(table))
    sys.stdout.flush()
    sys.stdout.write("\n")


def main():
    if args.interval <= 5:
        print('\033[0;37;41m%s\033[0m' % 'The interval must be greater than 6')
        sys.exit(1)
    while True:
        try:
            header = ['Instance Name', 'Power Status', 'Max Memory',
                      'Memory Usage', 'vCPU Number', 'CPU Time', 'CPU Usage']
            data = get_instance_info()
            title = 'Libvirt Monitor Tool'
            print_as_table(data, header, title)
            time.sleep(args.interval-1)
        except KeyboardInterrupt:
            print('\n')
            sys.exit()


if __name__ == '__main__':
    main()
