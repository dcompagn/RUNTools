RUNTools
========

A script collection for the RUN algorithm.

#About

`ts_reduce.py` : Is the task set reduction tool. Reduction tree is generated both in the standard JSON format and the more human-readable HTML format. It can be used in conjunction with the LITMUS^RT experiment-script (`gen_exps.py`) but no dependencies must be fulfilled.

## ts_reduce.py
*Usage*: `ts_reduce.py -i SCHED_FILE -o OUTPUT_FILE -p PROCESSORS -e HEURISTIC` 

`HEURISTIC: [first-fit | next-fit | worst-fit | next-fit]`

*Defaults*: `SCHED_FILE = sched.py`, `OUTPUT_FILE = tree.json`, `PROCESSORS = 8`, `HEURISTICS = worst-fit`
