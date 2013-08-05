#!/usr/bin/env python
'''
Created on 25/lug/2013

@author: Davide Compagnin
'''

import os
import json
import math
from decimal import Decimal
from fractions import gcd
from optparse import OptionParser

from tasks import FixedRateTask
from common import convert_data, DEFAULTS, HEURISTICS



def parse_args():
    parser = OptionParser("usage: %prog [options]")

    parser.add_option('-o', '--out-file', dest='out_file',
                      help='file for data output',
                      default=("%s/%s"% (os.getcwd(), DEFAULTS['out'])))
    parser.add_option('-i', '--in-file', dest='in_file',
                      help='file for data input',
                      default=("%s/%s"% (os.getcwd(), DEFAULTS['in'])))
    parser.add_option('-e', '--heuristic', dest='heuristic',
                      help='heuristic',
                      default=("%s"% DEFAULTS['heuristic']))
    parser.add_option('-p', '--processors', dest='cpus',
                      help='number of processors',
                      default=(DEFAULTS['cpus']))

    return parser.parse_args()

def aggregate(task_list, server, level):
    exec_cost = 0
    period = 1
    for t in task_list:
        exec_cost = (exec_cost * t.period) + (period * t.cost)
        period = period * t.period
    task_gcd = gcd(exec_cost, period)
    exec_cost /= task_gcd
    period /= task_gcd
    new_task = FixedRateTask(exec_cost, #period - exec_cost, 
                             period,
                             server, 
                             None, 
                             level)
    for t in task_list:
        t.parent = new_task
        t.server = server
        new_task.children.append(t)
    return new_task

def dual(taskset):
    for t in taskset:
        t.cost = t.period - t.cost
        


def distribuite_slack(ts, slack):
    ts.sort(key=lambda x: x.utilization(), reverse=True)
    i = 0
    unused_capacity = slack
    while (unused_capacity > Decimal(0)) and (i < len(ts) + 100):
        t = ts[i]
        if (t.dual_utilization() <= unused_capacity):
            unused_capacity -= t.dual_utilization() 
            t.cost = t.period
        else:
            tmp_util = t.utilization()
            t.cost += int(unused_capacity * Decimal(t.period))
            unused_capacity -= (t.utilization() - tmp_util)
        i += 1
        
    if (unused_capacity > Decimal(0)):
        raise Exception('Still capacity unused: ' + str(unused_capacity))



def serialize(task):
    obj = {
        'id': task.id,
        'cost': task.cost,
        'period': task.period,
        'level' : task.level,
        'children': []
    }
    for ch in task.get_children():
        obj['children'].append(serialize(ch))
        
    return obj



class Reductor(object):
    def __init__(self, cpus=8, heuristic='worst-fit', in_file='sched.py', out_file='tree.json'):
        self.ts = []
        self.cpus = cpus
        if heuristic in HEURISTICS:
            self.heuristic = HEURISTICS[heuristic]
        self.in_file = in_file
        self.out_file = out_file
        self.misfits = 0
        self.servers = 0
        self.unit_server = None
        self.level = 0
        
    def _misfit(self, x):
        #self.misfit += x.dual_utilization()
        self.misfits += 1
    
    def reduce(self):
        #parsing schedule.py file
        with open(self.in_file, 'r') as f:
            data = f.read().strip()
        
        try:
            schedule = eval(data)
        except:
            schedule = convert_data(data)
        
        for task_conf in schedule['task']:
            
            (task, args) = (task_conf[0], task_conf[1])
            real_args = args.split()
            #Get two last arguments as cost and period respectively
            index = len(real_args) - 2
            self.ts.append(FixedRateTask(int(real_args[index + 0]), int(real_args[index + 1])))
        
        n_tasks = len(self.ts)
        #n_tasks may be less than cpus
        if (n_tasks < self.cpus):
            print 'Info: cpus has changed from {0} to {1}'.format(unicode(self.cpus),unicode(n_tasks))
            self.cpus = n_tasks
        
        tot_util = sum([t.utilization() for t in self.ts])
        print 'Info: total utilization {0}'.format(tot_util)
        
        unused_capacity = Decimal(self.cpus) - tot_util
        if (unused_capacity < Decimal(0)):
            print 'Error: unfeasible taskset'.format(tot_util)
            raise Exception('Unfeasible Taskset')
        
        new_ts = self._pack(self.ts, self.cpus)
        new_ts.sort(key=lambda x: x.utilization(), reverse=True)
        distribuite_slack(new_ts, unused_capacity)
        dual(new_ts)
        self.level = 1
        unit_server = self._reduce(new_ts)
        
        if (len(unit_server) != 1):
            print 'Error: not correctly reduced'.format(tot_util)
            raise Exception('not correctly reduced')
    
        if (unit_server[0].utilization() != Decimal(0) and unit_server[0].utilization() != Decimal(1)):
            print 'Error: not correctly reduced'.format(tot_util)
            raise Exception('not correctly reduced')
        
        self.unit_server = unit_server[0]
        print 'Info: tree level {0}'.format(unicode(self.unit_server.level - self.unit_server.utilization()))
        
    def serialize(self):
        if (self.unit_server != None):
            serialized = serialize(self.unit_server)
            with open(self.out_file, 'wa') as f:
                json.dump(serialized, f, indent=4)
        else:
            print 'Error: no unit-server'
        
    def _pack(self, taskset, cpus):
        self.misfits = 0
        n_bins = cpus
        
        taskset.sort(key=lambda x: x.utilization(), reverse=True)
        
        bins = self.heuristic(taskset, 
                          n_bins, 
                          Decimal(1), 
                          lambda x: x.utilization(), 
                          self._misfit)
        while (self.misfits > 0):
            #n_bins += math.ceil(self.misfit)
            n_bins += 1 #self.misfit
            self.misfits = 0
            bins = self.heuristic(taskset, 
                              n_bins, 
                              Decimal(1), 
                              lambda x: x.utilization(), 
                              self._misfit)    
        servers = []
        for item in bins:
            tmp_server = aggregate(item, self.servers, self.level)
            servers.append(tmp_server)
            self.servers += 1
        
        self.misfits = 0
        return servers
    
    def _reduce(self, taskset):
        utilization = sum([t.utilization() for t in taskset])
        new_taskset = self._pack(taskset, int(math.ceil(utilization)))
        dual(new_taskset)
        if len(new_taskset) == 1:
        #if (utilization == Decimal(1) or utilization == Decimal(0)):
            return new_taskset
        else:
            self.level += 1
            return self._reduce(new_taskset)
        
def main():
    opts, args = parse_args()
    
    reductor = Reductor(int(opts.cpus.strip()), opts.heuristic, opts.in_file, opts.out_file)
    
    reductor.reduce()
    reductor.serialize()
    
if __name__ == '__main__':
    main()