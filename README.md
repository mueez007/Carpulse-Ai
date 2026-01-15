CarPulse AI — Intelligent Agentic Vehicle Service Management System

CarPulse AI is an end-to-end platform designed for modern vehicle service centers.
It automates service logging, mechanic management, reminders, documentation processing, and introduces agentic AI to understand natural language, execute backend tools, and deliver insights.

The system combines FastAPI, React, SQLite, machine learning, and a fully integrated domain-aware AI agent capable of performing real operations on the database.

Core Features
1. Vehicle Service Log Management

Add, update, delete service logs.

Track owner information, vehicle details, service type, cost, mileage, and next service date.

Auto-generate vehicle IDs.

Retrieve logs by vehicle ID or model.

Full CRUD implementation via backend tools.

2. Mechanic Management

Add and manage mechanics with specialization, experience, and contact information.

View all mechanics.

Analytics: identify mechanics with the highest service count, highest revenue generated.

3. Agentic AI System (Key Highlight)

The system includes a domain-trained agent that can:

Interpret natural language instructions.

Map user requests to backend tools.

Fetch, create, update, or delete service logs.

Analyze images and extract structured information.

Process voice inputs into structured service records.

Perform multi-step reasoning and decide the correct tool to execute.

Provide actionable insights based on historical data.

The agent is not a chatbot.
It is an operational AI that takes instructions like:

“Show me cars due for service next week.”

“Add a service log for Arun’s Creta serviced today.”

“Which mechanic generated the highest revenue this month?”

“Upload this invoice and extract the service details.”

The agent executes real backend operations safely and reliably.

4. Machine Learning: Service Cost Prediction

A regression model built using sklearn.

Trained using synthetic, domain-correct data.

Features include vehicle model, service type, mileage, and mechanic experience.

Returns:

Predicted cost

Low estimate

High estimate

Endpoint: /vehicle_service_logs/estimate-cost

5. Automated Service Reminders

Identifies customers with upcoming service dates.

Sends SMS reminders via Twilio (sandbox-safe mode included).

Gracefully handles missing numbers and unverified accounts.

6. Documentation and Image Handling

Upload service images or documents.

Retrieve all images linked to a vehicle.

Agent can interpret images and extract structured fields.

Useful for scanning invoices, service checklists, and before/after photos.

7. Voice Support

Upload audio describing a service.

Agent converts audio description into structured service logs.

8. Authentication System

Register, Login, and “Me” endpoints.

JWT-based secure authentication.

Integrated with frontend session management.

9. Frontend (React + Vite)

View all logs with a clean interface.

Add/Edit/Delete service logs with modal forms.

Live cost estimation using the machine learning model.

Agent chat interface.

Mechanic dashboard.

Image viewer for service images.

Dark/Light theme toggle.
Project Structure
backend/
    main.py
    routers/
    services/
    repos/
    models/
    ml/
    service_images/
    auth_db.py

frontend/
    src/
        api/
        pages/
        components/
        config/
        context/
        styles/
    vite.config.js
    Installation and Running the System

This section shows exactly how to get the entire system running on any development machine.

Backend Setup

Clone the project.

Navigate to backend:

cd backend


Create virtual environment:

python -m venv env


Activate environment:

Windows:

env\Scripts\activate


macOS/Linux:

source env/bin/activate


Install dependencies:

pip install -r requirements.txt


Run the database initialization automatically (handled by main.py).

Start backend:

uvicorn main:app --reload --port 8080


Backend now runs at:
http://127.0.0.1:8080

Frontend Setup

Navigate to frontend:

cd frontend


Install dependencies:

npm install


Create .env file:

VITE_API_URL=http://127.0.0.1:8080


Start development server:

npm run dev


Frontend runs at:
http://127.0.0.1:5173

Machine Learning Training

The model is located under backend/ml/.

To retrain:

python train_model.py


Outputs:

service_cost_model.pkl

Training logs including R² score.
Key Agent Tools Exposed to AI

The agent has access to the following backend tools:

get_vehicle_service_logs

add_vehicle_service_log

list_services_by_vehicle

get_vehicles_service_due_soon

update_service_cost_by_vehicle

remove_service_log_by_vehicle

get_total_services_count

get_average_service_cost

get_most_frequent_service_type

get_most_recent_service

get_overdue_services

get_owner_with_most_services

add_mechanic

list_mechanics

get_mechanic_with_most_services

get_total_cost_by_mechanic

upload_service_documentation

get_service_documentation

process_uploaded_service_images

send_service_reminders

get_vehicle_images

These allow the agent to execute actual backend operations.

How the Agent Works (High-Level)

User sends a natural-language request.

Agent parses intent using LLM reasoning.

Agent determines which backend tool is required.

Agent validates inputs.

Agent executes the correct tool.

Agent formats a human-readable response.

This is an operational agent, not a conversational bot.

Conclusion

CarPulse AI combines classical software engineering with modern agentic AI capabilities.
It automates operations, enhances accuracy, reduces workshop overload, and provides predictive intelligence.
The system is modular, scalable, and ready for real-world extension into production environments.

