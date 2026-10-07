#!/bin/bash
#SBATCH --job-name=trapezoid_exercise
#SBATCH --output=estimates_cosine
#SBATCH --error=assignment_2_errors
#SBATCH --nodes=33
#SBATCH --ntasks=33
#SBATCH --time=00:05:00
#SBATCH --partition=workstations

for n_task in {2..33};
do
 /usr/bin/time -a -o results.txt -f "${n_task}, %e" srun -n ${n_task} python3 assignment_2.py -a 0 -b 10 -n 10000 -t "reduce";
done