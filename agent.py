from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from agent_tools import ALL_TOOLS, hpc  # Import tools and the connection

# Initialize the DeepSeek Model
llm = ChatDeepSeek(model="deepseek-v4-pro", temperature=0.1)

# Define the System Prompt
system_message = """
You are an autonomous computational chemistry AI agent capable of managing molecular dynamics simulations and local data analysis.

The general workflow involves:
1. Creating the necessary input files for molecular dynamics simulations in a local computer.
2. Transferring these input files to a remote HPC cluster for execution.
3. Analyzing the results and generating reports.

You may ask to go through the whole workflow or just a part of it. 
"""

# Build the Agent
agent_executor = create_agent(
    model=llm, 
    tools=ALL_TOOLS, 
    system_prompt=system_message
)


# Test the End-to-End System
try:
    user_prompt = f"""
        1.	Working directory in HPC: “/home/xchenhe/polar_project/a_DIO/”. Working directory in local computer: “D:\OneDrive\OneDrive2\OneDrive\polar_project\a_DIO\”. You can access HPC with HPC tool and access local computer with local tool.
2.	In local computer. Copy the a_DIO\b_test1\4.2_P1ini0.5_T400\topo\pack.inp file together with the two required pdb input files to a_DIO\b_test1\4.5_P1ini0.75_T400\topo. The pack.inp  file in 4.2_P1ini0.5_T400 generates an initial packing with polar order 0.5. You should modify the pack.inp file in 4.5_P1ini0.75_T400 so that it can generate an initial packing with polar order 0.75.
3.	Upload the pack.inp file together with the two required initial pdb file to the HPC to the corresponding directory. If the corresponding directory does not exit, you should create it. 
4.	In HPC. Use "packmol -i pack.inp" to run the pack.inp file to generate a pdb file.
5.	In HPC. Use gmx_mpi editconf command to convert the pdb file into .gro file with proper name. You should run "export LD_LIBRARY_PATH=/home/xchenhe/local_gcc11/lib64:$LD_LIBRARY_PATH
source /home/xchenhe/software2/gromacs/gromacs-2024.1-mpi/bin/GMXRC" before running the gmx_mpi command.
6.	Download the resulted .gro file to the corresponding local folder.
7.	Write a python code in the local folder to verify the initial polar order of the .gro file is 0.75.
8.	Copy the required MD initial files in the “md” directory in the 4.2_P1ini0.5_T400 folder to the md directory of 4.5_P1ini0.75_T400 folder. 
9.	Copy the .gro file from the topo folder to the md folder. 
10.	 Modify the sub file in the md folder. Set the job name to be DIO0.75. 
11.	Go to the HPC. Use squeue command to find and record the node list for the job named “test”. Save the node list to a file in topo folder of 4.5_P1ini0.75_T400. The node list should contain at least three node ids.
12.	Go to the local computer. Go to the md folder of 4.5_P1ini0.75_T400 and open the sub file. Set the node id in this sub file to be the first three node id in the node list of the job “test” in HPC.
13.	Verify that md folder in 4.5_P1ini0.75_T4 contains all the necessary files required for a full MD simulation project.
14.	Upload the file in the local md folder in 4.5_P1ini0.75_T4 to the corresponding place in HPC.
15.	Submit the job with sbatch command in HPC. Then, kill the “test” job with scancel command. Verify that the job in 4.5_P1ini0.75_T4 is running.
16.	You have finish the simulation job where the initial configuration has a polar order of 0.75.

        """
        
    print(f"🚀 Starting agent task \n")

    response = agent_executor.invoke(
        {"messages": [("user", user_prompt)]},
        )
    result = response['output_text']
    error = response.get('error', None)
    if error:
        print(f"\n❌ Agent task failed. Error: {str(error)}")
    else:
        print(f"\n✅ Agent task completed. Result:\n{result}")

finally:
    hpc.close()