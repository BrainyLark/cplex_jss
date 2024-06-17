from docplex.cp.model import *
import docplex.cp.utils_visu as visu
import logging
import os

filename = os.path.dirname(os.path.abspath(__file__)) + '/data/jobshop_ft06.data'

logging.basicConfig(filename="jss_experiment_001.log", filemode="a", level=logging.DEBUG)
logger = logging.getLogger("LoggingFacility01")

with open(filename, 'r') as file:
    NB_JOBS, NB_MACHINES = [int(v) for v in file.readline().split()]
    JOBS = [[int(v) for v in file.readline().split()] for i in range(NB_JOBS)]


MACHINES = [[JOBS[j][2*s] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]
DURATION = [[JOBS[j][2*s+1] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]

model = CpoModel()

job_operations = [[interval_var(size=DURATION[j][m], name='O{}-{}'.format(j, m)) for m in range(NB_MACHINES)] for j in range(NB_JOBS)]

for j in range(NB_JOBS):
    for s in range(1, NB_MACHINES):
        model.add(end_before_start(job_operations[j][s-1], job_operations[j][s]))

machine_operations = [[] for m in range(NB_MACHINES)]
for j in range(NB_JOBS):
    for s in range(NB_MACHINES):
        machine_operations[MACHINES[j][s]].append(job_operations[j][s])
        
for mops in machine_operations:
    model.add(no_overlap(mops))


model.add(minimize(max(end_of(job_operations[i][NB_MACHINES-1]) for i in range(NB_JOBS))))

print("Solving model...")
res = model.solve(TimeLimit=10)
print("Solution:")
res.print_solution()

if res and visu.is_visu_enabled():
    visu.timeline("Solution for job-shop " + filename)
    visu.panel("Jobs")
    for i in range(NB_JOBS):
        visu.sequence(name='J' + str(i),
                      intervals=[(res.get_var_solution(job_operations[i][j]), MACHINES[i][j], 'M' + str(MACHINES[i][j])) for j in
                                 range(NB_MACHINES)])
        
    visu.panel('Machines')
    for k in range(NB_MACHINES):
        visu.sequence(name='M' + str(k),
                      intervals=[(res.get_var_solution(machine_operations[k][i]), k, 'J' + str(i)) for i in range(NB_JOBS)])
            
    visu.show()