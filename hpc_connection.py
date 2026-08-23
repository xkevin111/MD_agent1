import paramiko
import os
import threading

class HPCConnection:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        
        # Initialize SSH Client
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"Connecting to {host}...")
        # Connect using the password
        # Connect using the password
        self.ssh.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            look_for_keys=False,  # 强制不搜索本地 ~/.ssh 密钥
            allow_agent=False     # 强制不使用本地 SSH Agent
        )
        
        # Initialize SFTP for file transfers
        self.sftp = self.ssh.open_sftp()
        self.sftp_lock = threading.Lock()
        print("Connection established successfully.")

    def run_command(self, command):
        """Executes a command on the HPC and returns the output."""
        
        gmx_env_setup = (
            "export LD_LIBRARY_PATH=/home/xchenhe/local_gcc11/lib64:$LD_LIBRARY_PATH && "
            "source /home/xchenhe/software2/gromacs/gromacs-2024.1-mpi/bin/GMXRC"
        )
        
        full_command = f"{gmx_env_setup} && {command}"
        
        stdin, stdout, stderr = self.ssh.exec_command(full_command)
        
        # 1. Close stdin so remote programs don't wait for input
        stdin.close()
        
        # 2. Read the outputs FIRST to prevent buffer deadlocks
        out = stdout.read().decode('utf-8', errors='ignore').strip()
        err = stderr.read().decode('utf-8', errors='ignore').strip()
        
        # 3. THEN get the exit status
        exit_status = stdout.channel.recv_exit_status()
        
        return {
            "exit_code": exit_status,
            "stdout": out,
            "stderr": err
        }

    def upload_file(self, local_path, remote_path):
        """Uploads a file from Windows to the HPC."""
        with self.sftp_lock:
            self.sftp.put(local_path, remote_path)
        return f"Uploaded {local_path} to {remote_path}"

    def download_file(self, remote_path, local_path):
        """Downloads a file from the HPC to Windows."""
        with self.sftp_lock:
            self.sftp.get(remote_path, local_path)
        return f"Downloaded {remote_path} to {local_path}"

    def close(self):
        """Closes the connection."""
        self.sftp.close()
        self.ssh.close()
        print("Connection closed.")