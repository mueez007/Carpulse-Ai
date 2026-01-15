import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# How many rows you want
N_SAMPLES = 2000  # you can increase this to 5000+ if needed

OUTPUT_PATH = Path("synthetic_vehicle_service_logs.csv")

VEHICLE_MODELS = [
    "Hyundai Creta",
    "Maruti Swift",
    "Tata Nexon",
    "Honda City",
    "Kia Seltos",
    "Mahindra XUV300",
    "Hyundai i20",
    "Maruti Baleno",
]

SERVICE_TYPES = [
    "General Service",
    "Brake Service",
    "AC Repair",
    "Engine Repair",
    "Clutch Overhaul",
    "Wheel Alignment & Balancing",
    "Battery Replacement",
]

MECHANIC_NAMES = [
    "Ramesh",
    "Sameer",
    "Irfan",
    "Deepak",
    "Shiva",
    "Anil",
    "Manoj",
    "Kiran",
]

OWNER_FIRST_NAMES = [
    "Rahul", "Sneha", "Praveen", "Varsha", "Arjun",
    "Karthik", "Shreya", "Rohan", "Nisha", "Amit",
]

OWNER_LAST_NAMES = [
    "Kumar", "Reddy", "Mehta", "Rao", "Patel",
    "Sharma", "Shetty", "Naik", "Verma", "Gupta",
]

# Base cost assumptions per service type (roughly realistic, in INR)
BASE_SERVICE_COST = {
    "General Service": (2000, 4000),
    "Brake Service": (1500, 3000),
    "AC Repair": (1800, 3500),
    "Engine Repair": (7000, 20000),
    "Clutch Overhaul": (8000, 15000),
    "Wheel Alignment & Balancing": (600, 1500),
    "Battery Replacement": (3000, 7000),
}

# Model-specific cost multiplier (SUVs a bit more expensive)
MODEL_COST_FACTOR = {
    "Hyundai Creta": 1.15,
    "Maruti Swift": 0.95,
    "Tata Nexon": 1.05,
    "Honda City": 1.10,
    "Kia Seltos": 1.15,
    "Mahindra XUV300": 1.10,
    "Hyundai i20": 1.00,
    "Maruti Baleno": 0.98,
}


def random_owner_name():
    return f"{random.choice(OWNER_FIRST_NAMES)} {random.choice(OWNER_LAST_NAMES)}"


def random_phone():
    # Indian style mobile number, not real
    start = random.choice(["9", "8", "7"])
    rest = "".join(str(random.randint(0, 9)) for _ in range(9))
    return f"+91 {start}{rest}"


def random_vehicle_id(vehicle_model: str) -> str:
    slug = vehicle_model.replace(" ", "_").lower()
    suffix = random.randint(1000, 9999)
    return f"{slug}_{suffix}"


def random_service_and_cost(vehicle_model: str, mileage: int):
    service_type = random.choices(
        SERVICE_TYPES,
        weights=[30, 15, 10, 5, 8, 12, 5],  # General service more frequent
        k=1,
    )[0]

    base_min, base_max = BASE_SERVICE_COST[service_type]
    base = random.uniform(base_min, base_max)

    # Mild mileage influence: higher mileage → slightly more expensive
    mileage_factor = 1.0 + (mileage / 200_000)  # up to +75% around 150k km

    model_factor = MODEL_COST_FACTOR.get(vehicle_model, 1.0)

    # Add some noise (±20%)
    noise = random.uniform(0.8, 1.2)

    cost = base * mileage_factor * model_factor * noise
    cost = max(500, cost)  # minimum sanity floor

    return service_type, round(cost, 2)


def random_service_date():
    # Random date in the last ~3 years
    today = datetime.now().date()
    days_back = random.randint(0, 3 * 365)
    dt = today - timedelta(days=days_back)
    # return datetime object at noon (just to have a time)
    return datetime(dt.year, dt.month, dt.day, 12, 0, 0)


def random_next_service_date(service_date: datetime, service_type: str):
    # General service-based interval — rough rules
    if service_type == "General Service":
        months = random.randint(5, 7)
    elif service_type in ("Brake Service", "Wheel Alignment & Balancing", "AC Repair"):
        months = random.randint(4, 8)
    elif service_type in ("Engine Repair", "Clutch Overhaul", "Battery Replacement"):
        months = random.randint(8, 18)
    else:
        months = random.randint(6, 12)

    # Convert months ~ approx to days
    days = months * 30 + random.randint(-15, 15)
    next_date = service_date + timedelta(days=days)
    return next_date


def random_description(service_type: str):
    examples = {
        "General Service": [
            "Engine oil and oil filter changed, general inspection done.",
            "Periodic service, fluids checked and topped up.",
            "Standard service with air filter cleaning and washing.",
        ],
        "Brake Service": [
            "Rear brake pads replaced and brake fluid topped up.",
            "Front brake pads and discs inspected and replaced.",
            "Brake noise complaint resolved, pads adjusted.",
        ],
        "AC Repair": [
            "AC gas refilled and compressor checked.",
            "Cooling issue fixed, condenser cleaned.",
            "AC vents cleaned and cabin filter replaced.",
        ],
        "Engine Repair": [
            "Misfiring issue fixed, spark plugs replaced.",
            "Timing belt replaced and engine tuned.",
            "Engine overhaul and major internal components serviced.",
        ],
        "Clutch Overhaul": [
            "Full clutch kit replaced.",
            "Clutch plate and pressure plate changed.",
            "Clutch slip issue fixed, release bearing replaced.",
        ],
        "Wheel Alignment & Balancing": [
            "4-wheel alignment and balancing done.",
            "Steering pull corrected by wheel alignment.",
            "Tyre rotation and balancing performed.",
        ],
        "Battery Replacement": [
            "Old battery replaced with new 60Ah unit.",
            "Battery terminals cleaned and new battery installed.",
            "No-start issue fixed with new battery.",
        ],
    }
    return random.choice(examples.get(service_type, ["Service performed."]))


def generate_rows(n_samples: int):
    for _ in range(n_samples):
        vehicle_model = random.choice(VEHICLE_MODELS)
        owner_name = random_owner_name()
        owner_phone = random_phone()
        vehicle_id = random_vehicle_id(vehicle_model)
        mechanic_name = random.choice(MECHANIC_NAMES)

        # Mileage between 5,000 and 1,80,000 km
        mileage = random.randint(5_000, 180_000)

        service_date = random_service_date()
        service_type, cost = random_service_and_cost(vehicle_model, mileage)
        next_service_date = random_next_service_date(service_date, service_type)

        description = random_description(service_type)

        yield {
            "id": str(uuid.uuid4()),
            "vehicle_model": vehicle_model,
            "owner_name": owner_name,
            "owner_phone_number": owner_phone,
            "vehicle_id": vehicle_id,
            "service_date": service_date.isoformat(),       # matches your schema
            "service_type": service_type,
            "description": description,
            "mileage": mileage,
            "cost": cost,
            "next_service_date": next_service_date.isoformat(),
            "mechanic_name": mechanic_name,
        }


def main():
    fieldnames = [
        "id",
        "vehicle_model",
        "owner_name",
        "owner_phone_number",
        "vehicle_id",
        "service_date",
        "service_type",
        "description",
        "mileage",
        "cost",
        "next_service_date",
        "mechanic_name",
    ]

    print(f"Generating {N_SAMPLES} synthetic vehicle service logs...")
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in generate_rows(N_SAMPLES):
            writer.writerow(row)

    print(f"Done. Wrote synthetic data to: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
