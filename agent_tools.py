import os
import json
import subprocess
from dotenv import load_dotenv, find_dotenv
from langchain_core.tools import tool
from hpc_connection import HPCConnection

# 1. Initialize HPC here so the tools can access it
load_dotenv(find_dotenv())
hpc = HPCConnection(
    host="landau.phys.ust.hk", 
    username="xchenhe", 
    password=os.getenv("HPC_PASSWORD")
)

# 2. Define Tools
@tool
def execute_hpc_command(command: str) -> str:
    """
    Executes a bash command on the remote Linux HPC.
    Use this to run GROMACS commands (e.g., 'gmx_mpi pdb2gmx ...'), check directories, 
    or submit jobs via SLURM.
    """
    print(f"\n[Agent wants to execute]: {command}")
    
    # --- 1. SECURITY SANDBOX: Block destructive commands ---
    # Add any commands you want to strictly forbid here
    forbidden_keywords = ["rm -rf /", "rm -rf ~", "sudo", "mkfs", "chmod -R 777 /", "reboot"]
    for keyword in forbidden_keywords:
        if keyword in command:
            reject_msg = f"SYSTEM REJECTED: Command contains forbidden keyword '{keyword}'."
            print(f"❌ {reject_msg}")
            # We return this string to the AI so it knows WHY it was blocked
            return reject_msg 
    
    # --- 2. HUMAN-IN-THE-LOOP: Require approval for heavy compute tasks ---
    # If the AI tries to run the actual MD engine or submit a batch job, pause and ask the user
    heavy_compute_keywords = ["gmx_mpi mdrun", "sbatch", "qsub","scancel"]
    requires_approval = any(keyword in command for keyword in heavy_compute_keywords)
    
    if requires_approval:
        print("\n WARNING: The Agent is attempting a compute-heavy or scheduling command.")
        # This will pause the local Windows terminal and wait for you to type 'y' or 'n'
        user_input = input(f"Allow execution of [{command}]? (y/n): ").strip().lower()
        if user_input != 'y':
            reject_msg = "USER REJECTED: The human overseer denied permission to run this command."
            print("❌ Execution aborted by user.")
            return reject_msg
    
    # --- 3. EXECUTION ---
    print("✅ Executing command...")
    result = hpc.run_command(command)
    
    if result['exit_code'] == 0:
        return f"Command Succeeded. Output:\n{result['stdout']}"
    else:
        return f"Command Failed with exit code {result['exit_code']}. Error:\n{result['stderr']}"


@tool
def read_hpc_file(filepath: str) -> str:
    """
    Reads the content of a text file from the HPC.
    Use this to read .mdp parameter files, .top topology files, or .log error files.
    """
    print(f"\n[Agent reading file]: {filepath}")
    result = hpc.run_command(f"cat {filepath}")
    return result['stdout'] if result['exit_code'] == 0 else f"Failed to read file: {result['stderr']}"


@tool
def download_hpc_file(remote_path: str, local_path: str) -> str:
    """
    Downloads a file from the remote HPC to the local computer.
    """
    print(f"\n[Agent downloading file]: {remote_path} -> {local_path}")
    try:
        # Utilizing the existing download_file method from HPCConnection
        result = hpc.download_file(remote_path, local_path)
        return f"Success: {result}"
    except Exception as e:
        return f"Failed to download file: {str(e)}"


@tool
def upload_hpc_file(local_path: str, remote_path: str) -> str:
    """
    Uploads a file from the local Windows computer to the remote HPC.
    Use this to transfer input files, scripts, or directories to the HPC.
    """
    print(f"\n[Agent uploading file]: {local_path} -> {remote_path}")
    try:
        # Utilizing the existing upload_file method from HPCConnection
        result = hpc.upload_file(local_path, remote_path)
        return f"Success: {result}"
    except Exception as e:
        return f"Failed to upload file: {str(e)}"

@tool
def read_local_file(filepath: str) -> str:
    """
    Reads the content of a text file from the local computer.
    Use this to inspect local input files, sub files, or scripts before modifying them.
    """
    print(f"\n[Agent reading local file]: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Failed to read local file: {str(e)}"

@tool
def write_local_file(filepath: str, content: str) -> str:
    """
    Writes or overwrites content to a file on the local computer.
    Use this to create Python scripts (.py), edit batch submission files (.sub), 
    or modify parameter files (.inp).
    """
    print(f"\n[Agent writing local file]: {filepath}")
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"Success: File successfully written to {filepath}"
    except Exception as e:
        return f"Failed to write local file: {str(e)}"


@tool
def create_local_directory(dir_path: str) -> str:
    """
    Creates a new directory on the local computer if it does not already exist.
    """
    print(f"\n[Agent creating local directory]: {dir_path}")
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"Success: Local directory '{dir_path}' is ready."
    except Exception as e:
        return f"Failed to create directory: {str(e)}"


@tool
def create_jupyter_notebook(filepath: str, python_code: str) -> str:
    """
    Creates a local Jupyter Notebook (.ipynb) file with the provided Python code.
    """
    print(f"\n[Agent creating Jupyter Notebook]: {filepath}")
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [line + "\n" for line in python_code.split("\n")]
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(notebook_content, f, indent=4)
        return f"Success: Jupyter notebook created at {filepath}"
    except Exception as e:
        return f"Failed to create notebook: {str(e)}"


@tool
def execute_local_command(command: str) -> str:
    """
    Executes a bash/PowerShell command on the local Windows system.
    Use this to run local data processing scripts, check local files, 
    or run local Python/Jupyter commands.
    """
    print(f"\n[Agent wants to execute local command]: {command}")
    
    # --- 1. SECURITY SANDBOX: Block destructive local commands ---
    forbidden_keywords = [
        "rmdir /s /q C:\\", "del /f /s /q C:\\", "format", 
        "rd /s /q C:\\", "shutdown", "net user"
    ]
    for keyword in forbidden_keywords:
        if keyword.lower() in command.lower():
            reject_msg = f"SYSTEM REJECTED: Local command contains forbidden keyword '{keyword}'."
            print(f"❌ {reject_msg}")
            return reject_msg 

    # --- 2. EXECUTION ---
    print("✅ Executing local command...")
    try:
        # Using shell=True allows running standard Windows shell commands or PowerShell
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            return f"Local Command Succeeded. Output:\n{output if output else '(Command executed with no output)'}"
        else:
            error_output = result.stderr.strip()
            return f"Local Command Failed with exit code {result.returncode}. Error:\n{error_output}"
            
    except Exception as e:
        return f"Failed to execute local command due to an exception: {str(e)}"


# 3. Export a list of all tools
ALL_TOOLS = [
    execute_hpc_command, 
    read_hpc_file,
    download_hpc_file,
    upload_hpc_file,         
    create_local_directory,
    create_jupyter_notebook,
    execute_local_command,
    read_local_file,         
    write_local_file         
]