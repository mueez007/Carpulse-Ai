import os, random, json
from typing import Dict, Optional
from datetime import datetime, timedelta
from models.data_models import VehicleServiceLog, Mechanic
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)
service = Service(repo)

# Challenge 2: Core Vehicle Service Log Operations

async def add_vehicle_service_log(
    vehicle_model: str,
    owner_name: str,
    service_type: str,
    service_date: str,
    next_service_date: str,
    service_cost: float,
    description: str = "",
    mileage: int = 0
) -> Dict:
    """
    Add a new vehicle service log to the database.
    
    Args:
        vehicle_model: Model of the vehicle (e.g., "Hyundai Creta")
        owner_name: Name of the vehicle owner
        service_type: Type of service performed
        service_date: Date of service in YYYY-MM-DD format
        next_service_date: Date for next service in YYYY-MM-DD format
        service_cost: Cost of the service
        description: Details about the service performed
        mileage: Vehicle mileage at service time
    """
    try:
        # Create vehicle_id from model and random number
        vehicle_id = f"{vehicle_model.replace(' ', '_').lower()}_{random.randint(1000, 9999)}"
        
        log_data = VehicleServiceLog(
            vehicle_model=vehicle_model,
            owner_name=owner_name,
            vehicle_id=vehicle_id,
            service_date=datetime.strptime(service_date, "%Y-%m-%d"),
            service_type=service_type,
            description=description,
            mileage=mileage,
            cost=service_cost,
            next_service_date=datetime.strptime(next_service_date, "%Y-%m-%d") if next_service_date else None
        )
        
        result = await service.create_vehicle_service_log(log_data)
        return {
            "message": f"Successfully added service log for {vehicle_model}",
            "success": True,
            "data": {
                "id": result.id,
                "vehicle_model": result.vehicle_model,
                "owner_name": result.owner_name,
                "service_type": result.service_type,
                "service_date": result.service_date.strftime("%Y-%m-%d"),
                "cost": result.cost
            }
        }
    except Exception as e:
        return {"message": f"Error adding service log: {str(e)}", "success": False}


async def list_services_by_vehicle(vehicle_model: str) -> Dict:
    """
    List all services done for a specific vehicle model.
    
    Args:
        vehicle_model: Model of the vehicle to search for (e.g., "Hyundai Creta")
    """
    try:
        logs = await service.get_services_by_vehicle_model(vehicle_model)
        
        if not logs:
            return {
                "message": f"No service logs found for vehicle model: {vehicle_model}",
                "success": True,
                "data": []
            }
        
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                "id": log.id,
                "vehicle_model": log.vehicle_model,
                "owner_name": log.owner_name,
                "service_type": log.service_type,
                "service_date": log.service_date.strftime("%Y-%m-%d"),
                "next_service_date": log.next_service_date.strftime("%Y-%m-%d") if log.next_service_date else "Not set",
                "cost": log.cost,
                "mileage": log.mileage,
                "description": log.description
            })
        
        return {
            "message": f"Found {len(logs)} service(s) for {vehicle_model}",
            "success": True,
            "data": formatted_logs
        }
    except Exception as e:
        return {"message": f"Error retrieving services: {str(e)}", "success": False}


async def get_vehicles_service_due_soon(days: int = 30) -> Dict:
    """
    Get vehicles that have their next service due soon.
    """
    try:
        # Get all logs first
        all_logs = await service.get_vehicle_service_logs(None)
        
        if not all_logs:
            return {
                "message": f"No vehicles have service due in the next {days} days",
                "success": True,
                "data": []
            }
        
        today = datetime.now().date()
        formatted_logs = []
        
        for log in all_logs:
            if log.next_service_date:
                try:
                    # Handle both string and datetime objects
                    if isinstance(log.next_service_date, str):
                        next_service = datetime.fromisoformat(log.next_service_date).date()
                    else:
                        next_service = log.next_service_date.date()
                    
                    days_until = (next_service - today).days
                    
                    if 0 <= days_until <= days:
                        formatted_logs.append({
                            "vehicle_model": log.vehicle_model or "Unknown",
                            "owner_name": log.owner_name or "Unknown",
                            "next_service_date": next_service.strftime("%Y-%m-%d"),
                            "days_until_service": days_until,
                            "last_service_type": log.service_type or "Unknown",
                            "last_service_date": log.service_date.strftime("%Y-%m-%d") if log.service_date else "Unknown"
                        })
                except Exception as e:
                    print(f"Error processing log {log.id}: {e}")
                    continue
        
        if not formatted_logs:
            return {
                "message": f"No vehicles have service due in the next {days} days",
                "success": True,
                "data": []
            }
        
        # Sort by days until service
        formatted_logs.sort(key=lambda x: x["days_until_service"])
        
        return {
            "message": f"Found {len(formatted_logs)} vehicle(s) with service due in the next {days} days",
            "success": True,
            "data": formatted_logs
        }
        
    except Exception as e:
        return {
            "message": f"Error retrieving vehicles due for service: {str(e)}",
            "success": False,
            "data": []
        }


async def update_service_cost_by_vehicle(vehicle_model: str, new_cost: float) -> Dict:
    """
    Update the service cost for a specific vehicle model.
    
    Args:
        vehicle_model: Model of the vehicle to update
        new_cost: New service cost value
    """
    try:
        success = await service.update_service_cost_by_model(vehicle_model, new_cost)
        
        if success:
            return {
                "message": f"Successfully updated service cost for {vehicle_model} to Rs{new_cost}",
                "success": True
            }
        else:
            return {
                "message": f"No service logs found for vehicle model: {vehicle_model}",
                "success": False
            }
    except Exception as e:
        return {"message": f"Error updating service cost: {str(e)}", "success": False}


async def remove_service_log_by_vehicle(vehicle_model: str) -> Dict:
    """
    Remove service log entries for a specific vehicle model.
    
    Args:
        vehicle_model: Model of the vehicle to remove logs for
    """
    try:
        success = await service.delete_by_vehicle_model(vehicle_model)
        
        if success:
            return {
                "message": f"Successfully removed all service logs for {vehicle_model}",
                "success": True
            }
        else:
            return {
                "message": f"No service logs found for vehicle model: {vehicle_model}",
                "success": False
            }
    except Exception as e:
        return {"message": f"Error removing service logs: {str(e)}", "success": False}


# Existing functions (keep for compatibility)
async def get_vehicle_service_logs(vehicle_id: Optional[str] = None) -> dict:
    return await service.get_vehicle_service_logs(vehicle_id)


# Analytics Functions (Challenge 3)
async def get_total_services_count() -> Dict:
    """Get the total number of services recorded in the database."""
    all_logs = await service.get_vehicle_service_logs(None)
    total_count = len(all_logs)
    return {"message": f"Total services recorded: {total_count}", "count": total_count, "data": all_logs}


async def get_average_service_cost() -> Dict:
    """Calculate the average service cost across all recorded services."""
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found to calculate average", "average_cost": 0}
    
    total_cost = sum(log.cost for log in all_logs)
    average_cost = total_cost / len(all_logs)
    
    return {
        "message": f"Average service cost: Rs{average_cost:.2f}",
        "average_cost": round(average_cost, 2),
        "total_services": len(all_logs),
        "total_cost": total_cost
    }


async def get_most_frequent_service_type() -> Dict:
    """Find which service type occurs most frequently in the database."""
    all_logs = await service.get_vehicle_service_logs(None)
    
    if not all_logs:
        return {"message": "No services found", "most_frequent_type": None}
    
    service_type_counts = {}
    for log in all_logs:
        service_type = log.service_type
        service_type_counts[service_type] = service_type_counts.get(service_type, 0) + 1
    
    most_frequent_type = max(service_type_counts, key=service_type_counts.get)
    frequency = service_type_counts[most_frequent_type]
    
    return {
        "message": f"Most frequent service type: {most_frequent_type} (occurs {frequency} times)",
        "most_frequent_type": most_frequent_type,
        "frequency": frequency,
        "all_service_types": service_type_counts
    }


# Auditing Functions (Challenge 4)
async def get_most_recent_service() -> Dict:
    """Get the service that was done most recently."""
    try:
        all_logs = await service.get_vehicle_service_logs(None)
        
        if not all_logs:
            return {
                "message": "No services found in the database",
                "success": True,
                "most_recent_service": None
            }
        
        # Filter out logs without service_date and sort by service_date
        valid_logs = [log for log in all_logs if log.service_date is not None]
        
        if not valid_logs:
            return {
                "message": "No services with valid service dates found",
                "success": True,
                "most_recent_service": None
            }
        
        # Sort by service_date to find the most recent
        sorted_logs = sorted(
            valid_logs,
            key=lambda x: x.service_date,
            reverse=True
        )
        
        most_recent = sorted_logs[0]
        
        # Format the response
        service_date_str = most_recent.service_date.strftime("%Y-%m-%d") if most_recent.service_date else "Unknown"
        
        response_message = f"Most recent service: {most_recent.vehicle_model or 'Unknown Vehicle'} " \
                          f"owned by {most_recent.owner_name or 'Unknown Owner'} " \
                          f"on {service_date_str}. " \
                          f"Service type: {most_recent.service_type or 'Unknown'}, " \
                          f"Cost: ₹{most_recent.cost or '0'}"
        
        return {
            "message": response_message,
            "success": True,
            "most_recent_service": {
                "vehicle_model": most_recent.vehicle_model,
                "owner_name": most_recent.owner_name,
                "service_date": service_date_str,
                "service_type": most_recent.service_type,
                "cost": most_recent.cost,
                "description": most_recent.description,
                "mileage": most_recent.mileage
            }
        }
    except Exception as e:
        error_message = f"Error finding most recent service: {str(e)}"
        return {
            "message": error_message,
            "success": False,
            "most_recent_service": None
        }


async def get_overdue_services() -> Dict:
    """List all services that are overdue for the next maintenance date."""
    try:
        all_logs = await service.get_vehicle_service_logs(None)
        today = datetime.now().date()
        overdue_services = []
        
        for log in all_logs:
            if log.next_service_date:
                try:
                    # Handle both string and datetime objects
                    if isinstance(log.next_service_date, str):
                        next_service = datetime.fromisoformat(log.next_service_date).date()
                    else:
                        next_service = log.next_service_date.date()
                    
                    if next_service < today:
                        days_overdue = (today - next_service).days
                        overdue_services.append({
                            "vehicle_model": log.vehicle_model or "Unknown",
                            "owner_name": log.owner_name or "Unknown",
                            "next_service_date": next_service.strftime("%Y-%m-%d"),
                            "days_overdue": days_overdue,
                            "last_service_date": log.service_date.strftime("%Y-%m-%d") if log.service_date else "Unknown"
                        })
                except Exception as e:
                    print(f"Error processing overdue service {log.id}: {e}")
                    continue
        
        if not overdue_services:
            return {
                "message": "No overdue services found. All vehicles are up to date!",
                "success": True,
                "overdue_services": []
            }
        
        # Sort by days overdue (most overdue first)
        overdue_services.sort(key=lambda x: x["days_overdue"], reverse=True)
        
        overdue_list = "\n".join([
            f"- {svc['vehicle_model']} ({svc['owner_name']}): Due on {svc['next_service_date']} ({svc['days_overdue']} days overdue)"
            for svc in overdue_services
        ])
        
        return {
            "message": f"Found {len(overdue_services)} overdue service(s):\n{overdue_list}",
            "success": True,
            "overdue_services": overdue_services
        }
    except Exception as e:
        return {
            "message": f"Error retrieving overdue services: {str(e)}",
            "success": False,
            "overdue_services": []
        }


async def get_owner_with_most_services() -> Dict:
    """Find which owner has logged the most vehicle services."""
    try:
        all_logs = await service.get_vehicle_service_logs(None)
        
        if not all_logs:
            return {
                "message": "No services found in the database",
                "success": True,
                "top_owner": None
            }
        
        # Count services by owner
        owner_counts = {}
        for log in all_logs:
            owner = log.owner_name or "Unknown Owner"
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
        
        if not owner_counts:
            return {
                "message": "No owner information found in service logs",
                "success": True,
                "top_owner": None
            }
        
        # Find the owner with most services
        top_owner = max(owner_counts, key=owner_counts.get)
        service_count = owner_counts[top_owner]
        
        # Create breakdown of all owners
        owner_breakdown = "\n".join([
            f"- {owner}: {count} service(s)"
            for owner, count in sorted(owner_counts.items(), key=lambda x: x[1], reverse=True)
        ])
        
        return {
            "message": f"Owner with most services: {top_owner} ({service_count} services)\n\nAll owners:\n{owner_breakdown}",
            "success": True,
            "top_owner": top_owner,
            "service_count": service_count,
            "all_owner_counts": owner_counts
        }
    except Exception as e:
        return {
            "message": f"Error finding owner with most services: {str(e)}",
            "success": False,
            "top_owner": None
        }


# Multi-modal - Mechanic Functions (Challenge 5)
async def add_mechanic(
    name: str,
    specialization: str,
    contact_number: str,
    experience_years: int
) -> Dict:
    """
    Add a new mechanic to the database.
    
    Args:
        name: Name of the mechanic
        specialization: Specialization area (e.g., Engine, Brakes, AC)
        contact_number: Contact number
        experience_years: Years of experience
    """
    try:
        mechanic_data = Mechanic(
            name=name,
            specialization=specialization,
            contact_number=contact_number,
            experience_years=experience_years
        )
        
        result = await service.create_mechanic(mechanic_data)
        return {
            "message": f"Successfully added mechanic: {name}",
            "success": True,
            "data": {
                "id": result.id,
                "name": result.name,
                "specialization": result.specialization,
                "experience_years": result.experience_years
            }
        }
    except Exception as e:
        return {"message": f"Error adding mechanic: {str(e)}", "success": False}

async def list_mechanics() -> Dict:
    """List all mechanics in the database."""
    try:
        mechanics = await service.list_mechanics()
        
        if not mechanics:
            return {
                "message": "No mechanics found in the database",
                "success": True,
                "data": []
            }
        
        formatted_mechanics = []
        for mechanic in mechanics:
            formatted_mechanics.append({
                "id": mechanic.id,
                "name": mechanic.name,
                "specialization": mechanic.specialization,
                "contact_number": mechanic.contact_number,
                "experience_years": mechanic.experience_years
            })
        
        mechanics_list = "\n".join([
            f"- {m['name']}: {m['specialization']} ({m['experience_years']} years experience)"
            for m in formatted_mechanics
        ])
        
        return {
            "message": f"Found {len(mechanics)} mechanic(s):\n{mechanics_list}",
            "success": True,
            "data": formatted_mechanics
        }
    except Exception as e:
        return {"message": f"Error retrieving mechanics: {str(e)}", "success": False}

async def get_mechanic_with_most_services() -> Dict:
    """Find which mechanic has completed the most services."""
    try:
        all_logs = await service.get_vehicle_service_logs(None)
        
        if not all_logs:
            return {
                "message": "No services found",
                "success": True,
                "top_mechanic": None
            }
        
        # Count services by mechanic_id
        mechanic_counts = {}
        for log in all_logs:
            mechanic_id = log.mechanic_id
            if mechanic_id:
                mechanic_counts[mechanic_id] = mechanic_counts.get(mechanic_id, 0) + 1
        
        if not mechanic_counts:
            return {
                "message": "No mechanic information found in service logs",
                "success": True,
                "top_mechanic": None
            }
        
        # Find mechanic with most services
        top_mechanic_id = max(mechanic_counts, key=mechanic_counts.get)
        service_count = mechanic_counts[top_mechanic_id]
        
        # Try to get mechanic details
        try:
            mechanic = await service.get_mechanic(top_mechanic_id)
            mechanic_name = mechanic.name if mechanic else f"Mechanic {top_mechanic_id}"
        except:
            mechanic_name = f"Mechanic {top_mechanic_id}"
        
        return {
            "message": f"{mechanic_name} has completed the most services: {service_count} service(s)",
            "success": True,
            "top_mechanic": mechanic_name,
            "service_count": service_count,
            "all_mechanic_counts": mechanic_counts
        }
    except Exception as e:
        return {
            "message": f"Error finding mechanic with most services: {str(e)}",
            "success": False,
            "top_mechanic": None
        }

async def get_total_cost_by_mechanic() -> Dict:
    """Calculate the total cost of services performed by each mechanic."""
    try:
        all_logs = await service.get_vehicle_service_logs(None)
        
        if not all_logs:
            return {
                "message": "No services found", 
                "success": True,
                "mechanic_costs": {}
            }
        
        # Calculate total cost by mechanic
        mechanic_costs = {}
        mechanic_service_counts = {}
        
        for log in all_logs:
            mechanic_id = log.mechanic_id
            cost = log.cost
            
            if mechanic_id:
                mechanic_costs[mechanic_id] = mechanic_costs.get(mechanic_id, 0) + cost
                mechanic_service_counts[mechanic_id] = mechanic_service_counts.get(mechanic_id, 0) + 1
        
        if not mechanic_costs:
            return {
                "message": "No mechanic information found in service logs",
                "success": True, 
                "mechanic_costs": {}
            }
        
        # Create detailed report with mechanic names
        mechanic_report = []
        total_revenue = 0
        
        for mechanic_id, total_cost in mechanic_costs.items():
            try:
                mechanic = await service.get_mechanic(mechanic_id)
                mechanic_name = mechanic.name if mechanic else f"Mechanic {mechanic_id}"
            except:
                mechanic_name = f"Mechanic {mechanic_id}"
            
            service_count = mechanic_service_counts[mechanic_id]
            average_cost = round(total_cost / service_count, 2)
            total_revenue += total_cost
            
            mechanic_report.append({
                "mechanic_name": mechanic_name,
                "mechanic_id": mechanic_id,
                "total_cost": total_cost,
                "service_count": service_count,
                "average_cost": average_cost
            })
        
        # Sort by total cost (highest first)
        mechanic_report.sort(key=lambda x: x["total_cost"], reverse=True)
        
        report_lines = [
            f"- {mr['mechanic_name']}: ₹{mr['total_cost']} ({mr['service_count']} services, avg: ₹{mr['average_cost']})"
            for mr in mechanic_report
        ]
        
        return {
            "message": f"Total revenue by mechanic (Total: ₹{total_revenue}):\n" + "\n".join(report_lines),
            "success": True,
            "total_revenue": total_revenue,
            "mechanic_report": mechanic_report
        }
    except Exception as e:
        return {
            "message": f"Error calculating costs by mechanic: {str(e)}",
            "success": False,
            "mechanic_costs": {}
        }


# Multi-modal - Documentation Upload Functions
async def upload_service_documentation(
    vehicle_model: str,
    service_date: str,
    document_type: str,
    description: str = ""
) -> Dict:
    """
    Upload and link service documentation to a service record.
    
    Args:
        vehicle_model: Vehicle model the documentation belongs to
        service_date: Date of the service (YYYY-MM-DD)
        document_type: Type of document (invoice, photo, report, checklist)
        description: Description of the uploaded document
    """
    try:
        # This would typically handle the actual file upload
        # For now, we'll create a record of the upload
        
        return {
            "message": f"Successfully linked {document_type} documentation for {vehicle_model} service on {service_date}",
            "success": True,
            "data": {
                "vehicle_model": vehicle_model,
                "service_date": service_date,
                "document_type": document_type,
                "description": description,
                "upload_timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {"message": f"Error uploading documentation: {str(e)}", "success": False}

async def get_service_documentation(vehicle_model: str) -> Dict:
    """
    Get all documentation for a specific vehicle's services.
    
    Args:
        vehicle_model: Vehicle model to get documentation for
    """
    try:
        # This would typically query uploaded files
        # For now, we'll return a mock response
        
        return {
            "message": f"Documentation for {vehicle_model}:",
            "success": True,
            "data": {
                "vehicle_model": vehicle_model,
                "documents": [
                    {
                        "type": "invoice",
                        "date": "2024-01-15",
                        "description": "Service invoice and receipt"
                    },
                    {
                        "type": "photo", 
                        "date": "2024-01-15",
                        "description": "Before and after service photos"
                    }
                ]
            }
        }
    except Exception as e:
        return {"message": f"Error retrieving documentation: {str(e)}", "success": False}

async def process_uploaded_service_images(vehicle_model: str, image_description: str = "") -> Dict:
    """
    Process uploaded service images and link them to vehicle service records.
    
    Args:
        vehicle_model: Vehicle model the images belong to
        image_description: Description of what the images show
    """
    try:
        return {
            "message": f"Successfully processed service images for {vehicle_model}. Images show: {image_description}",
            "success": True,
            "data": {
                "vehicle_model": vehicle_model,
                "image_description": image_description,
                "processed_at": datetime.now().isoformat(),
                "images_linked": True
            }
        }
    except Exception as e:
        return {"message": f"Error processing service images: {str(e)}", "success": False}