#!/bin/bash

#SBATCH --partition=cpu
#SBATCH --job-name=dio.75
#SBATCH --output=job.o
#SBATCH --nodelist=compute-0-[2,3,6]
#SBATCH --exclusive
#SBATCH --ntasks-per-node=56

module purge
module load intel/2023.1.0
module load impi/2021.9.0

export LD_LIBRARY_PATH=/home/xchenhe/local_gcc11/lib64:$LD_LIBRARY_PATH
source /home/xchenhe/software2/gromacs/gromacs-2024.1-mpi/bin/GMXRC

gmx_mpi grompp -f em_SD.mdp -c T400P075ini.gro -p DIO_GMX.top -o em_SD.tpr
# mdrun is distributed across all allocated cores using mpirun
mpirun gmx_mpi mdrun -v -deffnm em_SD

gmx_mpi grompp -f npt_eq_E.mdp -c em_SD.gro -p DIO_GMX.top -o npt_eq_E.tpr
mpirun gmx_mpi mdrun -v -deffnm npt_eq_E

gmx_mpi grompp -f npt_eq.mdp -c npt_eq_E.gro -t npt_eq_E.cpt -p DIO_GMX.top -o npt_eq.tpr
mpirun gmx_mpi mdrun -v -deffnm npt_eq

gmx_mpi grompp -f npt_prod.mdp -c npt_eq.gro -t npt_eq.cpt -p DIO_GMX.top -o npt_prod.tpr
mpirun gmx_mpi mdrun -v -deffnm npt_prod


# 1 node 56 cores  2-112 3-168  4-224 5-280 6-336
# [2,7,9,11,13,14]
# cd /home/xchenhe/x_slow_timing/2
# mpirun /home/xchenhe/software/lammps-2Aug2023/src/lmp_intel_cpu_intelmpi -in lammps_phase.in