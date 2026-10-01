#!/bin/bash
#SBATCH --job-name=trapezoid_exercise
#SBATCH --output=estimates_cosine
#SBATCH --error=assignment_2_errors
#SBATCH --nodes=1
#SBATCH --ntasks=33
#SBATCH --time=00:05:00
#SBATCH --partition=assemblix

step_sizes=(1 100 1000 10000 100000)
n_tasks=(2 33)

for n_task in ${n_tasks[@]};
do
for step_size in ${step_sizes[@]} ; do /usr/bin/time -a -o results.txt -f "${n_task}, %e" srun -n ${n_task} python3 assignment_2.py -a 0 -b 10 -n ${step_size} -t "broadcast"; done; 
done