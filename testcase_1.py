from agents import PolicyAgent
from helpers import print_llm_response, format_llm_response

print("Running Health Insurance Policy Agent")
agent = PolicyAgent()
prompt = "does my policy cover outpatient surgery?"

response = format_llm_response(agent.answer_query(prompt))
print_llm_response(response, title="Policy Agent Response")