# Vehicle Service Log Agent

## Project Overview

An AgenicAI based online app for maintaning a log of servicing done till date for customer vehicles with details and generating reminders for upcoming or any pending service. This project aims to empower vehicle owners with information on their vehicle maintenace by making it accesible easily online. With VehicleServiceLogAgent, service center personnel can interact with AI Agent to upload full details of the vehicle servicing done with videos, pics and audit details. This provides a transparent view to vehicle owners ensuring good condition of their vehicles & safety.

Follow the steps below to set up and run the backend application.

## Steps to start backend

1. **Navigate to the backend directory**
   
    ```bash
   cd /workspace/vehicle_service_log_agent/backend
   ```
2. **Install the required dependencies**  
   
   Install all necessary Python packages using:  
   ```bash
   pip install -r requirements.txt
   ```
3. **Create Google AI Studio Key**
   
   Visit https://aistudio.google.com/ using your personal gmail id and create an API Key. If you are a first time user you might have to create a new project in https://console.cloud.google.com/ first , import it here and then create API Key.

4. **Update env with Google AI Studio Key**
   
   Once the key is created copy the key value and update the below variable in .env file

   ```GOOGLE_API_KEY=<Use your key>```

5. **Run the backend server**  
   
   Once the dependencies are installed and env is updated, start the application with:  
   ```bash
   python main.py
   ```

## Steps to start frontend

1. Find the `index.html` file inside the **frontend** directory.
2. **Configure the backend connection**  
   - Ensure that the **backend server** is up and running.  
   - Open the `apiService.js` file (usually located inside the `js` or `services` folder).  
   - Get the **host URL** or **API base URL** from the **Endpoints (Plug Icon)** in the leftside panel and look for 8080 Port.
   - Update the **host URL** or **API base URL** to match your backend’s running address.  
     Example:  
     ```js
     const API_CONFIG = {
      baseURL: "<BACKEND_URL>", // Configure the relevant backend url
      headers: {
       "Content-Type": "application/json",
      },
      };
     ```
3. **Start the frontend app**  
   - Right-click on `index.html`.  
   - Choose **"Open with Live Server"** (available in VS Code or similar editors).  
   - The application will automatically open in your default web browser.


