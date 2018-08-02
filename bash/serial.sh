#!/bin/bash

## Declare a name for this job
#PBS -N propensity_for_motion
## Request the queue for this job (e.g. morganshort, morganeth, izabelaeth)
#PBS -q morganshort
## Request a total of 1 processor for this job (1 node and 1 processor per node)
#PBS -l nodes=1:ppn=1,pvmem=2000mb
## Request walltime. Max walltime for morganshort is 4:00:00
#PBS -l walltime=4:00:00
## These are PBS standard output and error files.  Uncomment only if you don't want the defaults.
#PBS -o output.$PBS_JOBID
#PBS -e error.$PBS_JOBID

## How many procs do I have?
NN=`cat $PBS_NODEFILE | wc -l`
echo "Processors received = "$NN
echo "script running on host `hostname`"

## cd into the directory where I typed qsub
cd $PBS_O_WORKDIR
echo "PBS_NODEFILE"
cat $PBS_NODEFILE

## Put the commands you want to run, one per line
bash input_file_generator.sh 10 100 2000 100000 15000 36000 1500
bash input_file_generator.sh 10 100 2000 100000 21000 36000 1300
bash input_file_generator.sh 10 100 2000 100000 27000 36000 1100
bash input_file_generator.sh 10 100 2000 100000 33000 36000 900
bash lammps_looper.sh lmp_bardeeneth
cd ../python
python3 -c 'from control import control; control.analyze(1000); control.plot_analysis(180, 1000); control.plot_system()'
