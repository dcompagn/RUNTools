'''
Created on 25/lug/2013

@author: Davide Compagnin
'''

from decimal import Decimal

class PeriodicTask(object):
    def __init__(self, exec_cost, period, id=None):
        self.cost = exec_cost
        self.period = period
        self.id = id
        
    def utilization(self):
        return Decimal(self.cost) / Decimal(self.period)

class FixedRateTask(PeriodicTask):
    
    def __init__(self, exec_cost, period, id=None, server=None, level=-1):
        super(FixedRateTask,self).__init__(exec_cost, period, id)
        self.server = server
        self.level = level
        self.children = []
        self.parent = None
        
    def dual_utilization(self):
        return Decimal(1) - self.utilization()
    
    def get_children(self):
        return self.children