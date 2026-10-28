#!/bin/bash
#SBATCH --job-name=pysparkexercise
#SBATCH --output=pyspark_exercise
#SBATCH --error=pyspark_errors
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:05:00
#SBATCH --partition=assemblix
#SBATCH --mem=128gb

python3 ./assignment_5.py -g "/data/datasets/dbNSFP/snpEff_old/data/dbNSFP4.9a.txt.gz" -c "/data/datasets/dbNSFP/snpEff_old/data/dbNSFP4.3c.txt.gz.data_types"