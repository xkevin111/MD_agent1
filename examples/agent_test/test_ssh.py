from dotenv import load_dotenv
from hpc_connection import HPCConnection
import os

load_dotenv() 

# --- FILL THESE IN WITH YOUR ACTUAL HPC DETAILS ---
HPC_HOST = "landau.phys.ust.hk" 
HPC_USER = "xchenhe"
# Fetch the password from the .env file
HPC_PASS = os.getenv("HPC_PASSWORD")

# print(f"Did Python load the password? : {'YES' if HPC_PASS else 'NO, it is None'}")

# 1. Establish connection using the password
hpc = HPCConnection(host=HPC_HOST, username=HPC_USER, password=HPC_PASS)

try:
    # 2. Test a basic Linux command
    print("Testing basic command (pwd)...")
    result = hpc.run_command("pwd")
    print(f"Current Directory: {result['stdout']}")

    # 3. Test checking GROMACS installation
    print("\nTesting GROMACS availability...")
    gmx_result = hpc.run_command("gmx_mpi -version")
    if gmx_result['exit_code'] == 0:
        print("GROMACS is accessible!")
        # Just print the first line of the output to verify
        print(gmx_result['stdout'].split('\n')[0]) 
    else:
        print("Failed to find GROMACS. You might need to load a module (e.g., 'module load gromacs') in the run_command method.")
        print(f"Error: {gmx_result['stderr']}")

finally:
    # 4. Always close the connection
    hpc.close()