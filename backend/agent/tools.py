import requests, os, random, json
from typing import Dict, Optional
from models.data_models import VehicleServiceLog
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)
service = Service(repo)

async def get_vehicle_service_logs(vehicle_id: Optional[str] = None) -> dict:
    return await service.get_vehicle_service_logs(vehicle_id)


async def add_vehicle_service_log(vehicle_name: str, service_date: str, cost: float, service_type: str) -> Dict:
    """
    Add a new vehicle service log to the database.
    Args:
        vehicle_name: Name of the vehicle
        service_date: Date of service in YYYY-MM-DD format
        cost: Cost of the service
        service_type: Type of service performed
    """
    log_data = {
        "vehicle_name": vehicle_name,
        "service_date": service_date,
        "cost": cost,
        "service_type": service_type
    }
    result = await service.create_vehicle_service_log(log_data)
    return {"message": f"Service log added for {vehicle_name}", "data": result}


async def list_services_by_vehicle(vehicle_name: str) -> Dict:
    """
    List all services done for a specific vehicle.
    Args:
        vehicle_name: Name of the vehicle to search for
    """
    logs = await service.get_vehicle_service_logs(vehicle_name)
    if not logs:
        return {"message": f"No service logs found for {vehicle_name}", "data": []}
    return {"message": f"Found {len(logs)} service(s) for {vehicle_name}", "data": logs}


async def get_vehicles_service_due_soon(days: int = 30) -> Dict:
    """
    Get vehicles that have their next service due soon.
    Args:
        days: Number of days to look ahead (default: 30)
    """
    from datetime import datetime, timedelta
    
    all_logs = await service.get_vehicle_service_logs(None)
    today = datetime.now()
    due_soon = []
    
    for log in all_logs:
        if "next_service_date" in log and log["next_service_date"]:
            try:
                next_service = datetime.strptime(log["next_service_date"], "%Y-%m-%d")
                days_until = (next_service - today).days
                if 0 <= days_until <= days:
                    due_soon.append({
                        "vehicle_name": log["vehicle_name"],
                        "next_service_date": log["next_service_date"],
                        "days_until_service": days_until
                    })
            except:
                pass
    
    if not due_soon:
        return {"message": f"No vehicles have service due in the next {days} days", "data": []}
    return {"message": f"Found {len(due_soon)} vehicle(s) with service due soon", "data": due_soon}


async def update_service_cost_by_vehicle(vehicle_name: str, new_cost: float) -> Dict:
    """
    Update the service cost for a specific vehicle's latest service.
    Args:
        vehicle_name: Name of the vehicle
        new_cost: New cost value
    """
    logs = await service.get_vehicle_service_logs(vehicle_name)
    if not logs:
        return {"message": f"No service logs found for {vehicle_name}", "success": False}
    
    # Update the most recent service log
    latest_log = logs[0]  # Assuming logs are sorted by date
    log_id = latest_log.get("id")
    
    if not log_id:
        return {"message": "Could not find log ID", "success": False}
    
    update_data = {"cost": new_cost}
    result = await service.update_vehicle_service_log(log_id, update_data)
    return {"message": f"Updated service cost for {vehicle_name} to Rs{new_cost}", "success": True, "data": result}


async def remove_service_log_by_vehicle(vehicle_name: str) -> Dict:
    """
    Remove service log entry for a specific vehicle.
    Args:
        vehicle_name: Name of the vehicle
    """
    logs = await service.get_vehicle_service_logs(vehicle_name)
    if not logs:
        return {"message": f"No service logs found for {vehicle_name}", "success": False}
    
    # Remove the most recent service log
    latest_log = logs[0]
    log_id = latest_log.get("id")
    
    if not log_id:
        return {"message": "Could not find log ID to remove", "success": False}
    
        
    # Call the delete method from service
    result = await service.delete_vehicle_service_log(log_id)
    return {"message": f"Service log for {vehicle_name} removed", "success": True, "data": result}


# Analytics Functions

async def get_total_services_count() -> Dict:
    """
    Get the total number of services recorded in the database.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    total_count = len(all_logs)
    return {"message": f"Total services recorded: {total_count}", "count": total_count, "data": all_logs}


async def get_average_service_cost() -> Dict:
    """
    Calculate the average service cost across all recorded services.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found to calculate average", "average_cost": 0}
    
    total_cost = sum(log.get("cost", 0) for log in all_logs)
    average_cost = total_cost / len(all_logs)
    
    return {
        "message": f"Average service cost: Rs{average_cost:.2f}",
        "average_cost": round(average_cost, 2),
        "total_services": len(all_logs),
        "total_cost": total_cost
    }


async def get_most_frequent_service_type() -> Dict:
    """
    Find which service type occurs most frequently in the database.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "most_frequent_type": None}
    
    # Count service types
    service_type_counts = {}
    for log in all_logs:
        service_type = log.get("service_type", "Unknown")
        service_type_counts[service_type] = service_type_counts.get(service_type, 0) + 1
    
    # Find the most frequent
    most_frequent_type = max(service_type_counts, key=service_type_counts.get)
    frequency = service_type_counts[most_frequent_type]
    
    return {
        "message": f"Most frequent service type: {most_frequent_type} (occurs {frequency} times)",
        "most_frequent_type": most_frequent_type,
        "frequency": frequency,
        "all_service_types": service_type_counts
    }


# Auditing Functions

async def get_most_recent_service() -> Dict:
    """
    Get the service that was done most recently.
    """
    from datetime import datetime
    
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "most_recent_service": None}
    
    # Sort by service_date to find the most recent
    sorted_logs = sorted(
        all_logs,
        key=lambda x: datetime.strptime(x.get("service_date", "1900-01-01"), "%Y-%m-%d"),
        reverse=True
    )
    
    most_recent = sorted_logs[0]
    
    return {
        "message": f"Most recent service: {most_recent.get('vehicle_name')} on {most_recent.get('service_date')}",
        "most_recent_service": most_recent
    }


async def get_overdue_services() -> Dict:
    """
    List all services that are overdue for the next maintenance date.
    """
    from datetime import datetime
    
    all_logs = await service.get_vehicle_service_logs(None)
    today = datetime.now()
    overdue_services = []
    
    for log in all_logs:
        if "next_service_date" in log and log["next_service_date"]:
            try:
                next_service = datetime.strptime(log["next_service_date"], "%Y-%m-%d")
                if next_service < today:
                    days_overdue = (today - next_service).days
                    overdue_services.append({
                        "vehicle_name": log["vehicle_name"],
                        "next_service_date": log["next_service_date"],
                        "days_overdue": days_overdue,
                        "owner": log.get("owner", "Unknown")
                    })
            except:
                pass
    
    if not overdue_services:
        return {"message": "No overdue services found", "overdue_services": []}
    
    return {
        "message": f"Found {len(overdue_services)} overdue service(s)",
        "overdue_services": overdue_services
    }


async def get_owner_with_most_services() -> Dict:
    """
    Find which owner has logged the most vehicle services.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "top_owner": None}
    
    # Count services by owner
    owner_counts = {}
    for log in all_logs:
        owner = log.get("owner", "Unknown")
        owner_counts[owner] = owner_counts.get(owner, 0) + 1
    
    # Find the owner with most services
    top_owner = max(owner_counts, key=owner_counts.get)
    service_count = owner_counts[top_owner]
    
    return {
        "message": f"Owner with most services: {top_owner} ({service_count} services)",
        "top_owner": top_owner,
        "service_count": service_count,
        "all_owner_counts": owner_counts
    }


# Multi-modal - Mechanic Functions

async def get_mechanic_with_most_services() -> Dict:
    """
    Find which mechanic has completed the most services.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "top_mechanic": None}
    
    # Count services by mechanic_id
    mechanic_counts = {}
    for log in all_logs:
        mechanic_id = log.get("mechanic_id", "Unknown")
        if mechanic_id and mechanic_id != "Unknown":
            mechanic_counts[mechanic_id] = mechanic_counts.get(mechanic_id, 0) + 1
    
    if not mechanic_counts:
        return {"message": "No mechanic information found in service logs", "top_mechanic": None}
    
    # Find mechanic with most services
    top_mechanic_id = max(mechanic_counts, key=mechanic_counts.get)
    service_count = mechanic_counts[top_mechanic_id]
    
    return {
        "message": f"Mechanic {top_mechanic_id} has completed {service_count} service(s)",
        "top_mechanic_id": top_mechanic_id,
        "service_count": service_count,
        "all_mechanic_counts": mechanic_counts
    }


async def get_total_cost_by_mechanic() -> Dict:
    """
    Calculate the total cost of services performed by each mechanic.
    """
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "mechanic_costs": {}}
    
    # Calculate total cost by mechanic
    mechanic_costs = {}
    mechanic_service_counts = {}
    
    for log in all_logs:
        mechanic_id = log.get("mechanic_id", "Unknown")
        cost = log.get("cost", 0)
        
        if mechanic_id and mechanic_id != "Unknown":
            mechanic_costs[mechanic_id] = mechanic_costs.get(mechanic_id, 0) + cost
            mechanic_service_counts[mechanic_id] = mechanic_service_counts.get(mechanic_id, 0) + 1
    
    if not mechanic_costs:
        return {"message": "No mechanic information found in service logs", "mechanic_costs": {}}
    
    # Create detailed report
    mechanic_report = []
    for mechanic_id, total_cost in mechanic_costs.items():
        mechanic_report.append({
            "mechanic_id": mechanic_id,
            "total_cost": total_cost,
            "service_count": mechanic_service_counts[mechanic_id],
            "average_cost": round(total_cost / mechanic_service_counts[mechanic_id], 2)
        })
    
    return {
        "message": f"Total cost calculated for {len(mechanic_costs)} mechanic(s)",
        "mechanic_costs": mechanic_costs,
        "detailed_report": mechanic_report
    }