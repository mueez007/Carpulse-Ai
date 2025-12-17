from google.adk.agents import LlmAgent
from .prompt import *
from .tools import *
from constants import AGENT_NAME, AGENT_DESCRIPTION, AGENT_MODEL

root_agent = LlmAgent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    description=AGENT_DESCRIPTION, 
    instruction=ROOT_AGENT_PROMPT,
    tools=[
        get_vehicle_service_logs,
        add_vehicle_service_log,
        list_services_by_vehicle,
        get_vehicles_service_due_soon,
        update_service_cost_by_vehicle,
        remove_service_log_by_vehicle,
        # Analytics tools
        get_total_services_count,
        get_average_service_cost,
        get_most_frequent_service_type,
        # Auditing tools
        get_most_recent_service,
        get_overdue_services,
        get_owner_with_most_services,
        # Multi-modal - Mechanic tools
        add_mechanic,
        list_mechanics,
        get_mechanic_with_most_services,
        get_total_cost_by_mechanic,
        # Multi-modal - Documentation tools
        upload_service_documentation,
        get_service_documentation,
        process_uploaded_service_images,
        # 🔔 Reminder / Twilio tool
        send_service_reminders,
        get_vehicle_images,
    ]
)