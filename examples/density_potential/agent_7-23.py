from langchain_deepseek import ChatDeepSeek
from langchain.agents import create_agent
from agent_tools import ALL_TOOLS, hpc  # Import tools and the connection

# Initialize the DeepSeek Model
llm = ChatDeepSeek(model="deepseek-v4-pro", temperature=0.1)

# Define the System Prompt
system_message = """
You are an autonomous computational chemistry AI agent capable of managing molecular dynamics simulations and local data analysis.

Given a task subject, remote directory, and local directory, your protocol is to:
1. Inspect the remote directory to identify relevant simulation files.
2. Execute the appropriate tool commands non-interactively to compute and extract the requested data.
3. Ensure the local directory exists, then download the result files.
4. Create a local Jupyter notebook (.ipynb) with complete, runnable Python code to plot and save the visualization graph.
5. Self-correct automatically if any command fails by inspecting error outputs.
"""

# Build the Agent
agent_executor = create_agent(
    model=llm, 
    tools=ALL_TOOLS, 
    system_prompt=system_message
)


def run_md_analysis(subject: str, hpc_dir: str, local_dir: str):
    """
    Triggers the agent with minimal required task information.
    """
    user_prompt = f"""
    Perform the following analysis task:
    - Subject: {subject}
    - Remote HPC Directory: {hpc_dir}
    - Local Directory: {local_dir}
    """
    
    print(f"🚀 Starting agent task \n")

    response = agent_executor.invoke(
        {"messages": [("user", user_prompt)]},
       )
        
    return response["messages"][-1].content


# Test the End-to-End System
try:
    run_md_analysis(
        subject="system density",
        hpc_dir="/home/xchenhe/polar_project/a_DIO/b_test1/2.5_from_2.3_T_NH_P_C-rescale",
        local_dir="examples\density_potential"
    )
finally:
    hpc.close()