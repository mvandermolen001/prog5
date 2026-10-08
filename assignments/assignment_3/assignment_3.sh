#!/bin/bash
#SBATCH --job-name=sql_exercise
#SBATCH --output=sql_exercise
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:08:00
#SBATCH --partition=workstations
# Dataset: "/commons/data/NCBI/refseq/ftp.ncbi.nlm.nih.gov/refseq/release/archaea/archaea.2.genomic.gbff"

python3 ./assignment_3.py -g "" -c ""