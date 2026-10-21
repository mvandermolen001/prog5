#!/bin/bash
#SBATCH --job-name=pysparkexercise
#SBATCH --output=pyspark_exercise
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:30:00
#SBATCH --partition=assemblix
#SBATCH --mem=128gb
# Dataset: "/commons/data/NCBI/refseq/ftp.ncbi.nlm.nih.gov/refseq/release/archaea/archaea.1.genomic.gbff"

python3 ./assignment5.py -g "/commons/data/NCBI/refseq/ftp.ncbi.nlm.nih.gov/refseq/release/archaea/archaea.1.genomic.gbff"