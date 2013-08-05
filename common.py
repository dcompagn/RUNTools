'''
Created on 25/lug/2013

@author: Davide Compagnin
'''

import re
from heuristics import worst_fit, best_fit, next_fit, first_fit

DEFAULTS = {'cpus'        : '8',
            'prog'        : 'rtspin',
            'heuristic'   : 'worst-fit',
            'in'          : 'sched.py',
            'out'         : 'tree.json'
}

HEURISTICS = {
              'worst-fit' : worst_fit,
              'best-fit'  : best_fit,
              'next-fit'  : next_fit,
              'first-fit' : first_fit,
}

def convert_data(data):
    '''Convert a non-python schedule file into the python format'''
    regex = re.compile(
        r"(?P<PROC>^"
            r"(?P<HEADER>/proc/[\w\-]+?/)?"
            r"(?P<ENTRY>[\w\-\/]+)"
              r"\s*{\s*(?P<CONTENT>.*?)\s*?}$)|"
        r"(?P<TASK>^"
            r"(?:(?P<PROG>[^\d\-\s][\w\.]*?) )?\s*"
            r"(?P<ARGS>[\w\-_\d\. \=]+)\s*$)",
        re.S|re.I|re.M)

    procs = []
    tasks = []

    for match in regex.finditer(data):
        if match.group("PROC"):
            header = match.group("HEADER") or "/proc/litmus/"
            loc  = "{}{}".format(header, match.group("ENTRY"))
            proc = (loc, match.group("CONTENT"))
            procs.append(proc)
        else:
            prog = match.group("PROG") or DEFAULTS['prog']
            spin = (prog, match.group("ARGS"))
            tasks.append(spin)

    return {'proc' : procs, 'task' : tasks}