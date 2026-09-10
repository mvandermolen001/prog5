#!/bin/bash
#SBATCH --job-name=trapezoid_exercise
#SBATCH --output=estimates_cosine
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:05:00
#SBATCH --partition=workstations

step_sizes=(1 10 100 1000 10000 100000)

for step_size in ${step_sizes[@]} ; do python3 ./assignment1.py -a 0 -b 1 -n ${step_size}; done