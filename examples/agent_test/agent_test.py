from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

# Load variables from the .env file into your environment
load_dotenv() 

llm = ChatDeepSeek(
    model="deepseek-v4-pro", 
    temperature=0.1,
    max_retries=2,
)

# Test the LLM to ensure it can respond
response = llm.invoke("What is the command to minimize energy in GROMACS?")
print(response.content)