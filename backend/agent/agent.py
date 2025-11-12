from google.adk.agents import LlmAgent
from .prompt import *
from .tools import *
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION, 
    instruction=ROOT_AGENT_PROMPT,
    tools= [
    get_vehicle_service_logs]
)