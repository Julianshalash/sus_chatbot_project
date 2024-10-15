import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
import os
import openai
from dotenv import load_dotenv
from backend import BuildingDataProcessor
from U_value import chatbot_calculate
import bcrypt
import yaml
from pydantic import BaseModel
import asyncio

# Load environment variables
load_dotenv()
app = FastAPI()

# Enable CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sus-chatbot-project-2.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load credentials from the YAML file
def load_credentials():
    with open('config_users.yml', 'r') as file:
        config = yaml.safe_load(file)
        return config['credentials']

credentials = load_credentials()
# Configure logging
logging.basicConfig(level=logging.DEBUG)
openai.api_key = os.getenv('OPENAI_API_KEY')  # Load API Key from environment

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.debug(f"Connected: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.debug(f"Disconnected: {websocket.client}")

    async def keep_alive(self, websocket: WebSocket):
        try:
            while websocket in self.active_connections:
                await websocket.send_text("")  # Send ping message to keep the connection alive
                await asyncio.sleep(30)  # Ping every 30 seconds (adjust as needed)
        except Exception as e:
            logging.error(f"Keep-alive failed: {e}")
            self.disconnect(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            logging.debug(f"Sending message to {websocket.client}: {message}")
            await websocket.send_text(message)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            self.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
async def get():
    with open("interface_secure.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

class LoginRequest(BaseModel):
    username: str
    password: str

def validate_login(login_data: LoginRequest):
    # Iterate over each user in the credentials list
    for user in credentials:
        # Check if the username matches
        if login_data.username == user['username']:
            # Check if the password matches
            if bcrypt.checkpw(login_data.password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return True
        # If no match found, raise an exception
        raise HTTPException(status_code=401, detail="Invalid username or password")
@app.post("/validate_login")
async def validate_login_endpoint(login_data: LoginRequest):
    validate_login(login_data)
    return {"success": True, "message": "Login successful"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    manager = ConnectionManager()
    await manager.connect(websocket)
    logging.debug("Client connected to WebSocket.")
    try:
        while True:
            data = await websocket.receive_text()
            logging.debug(f"Received message from client: {data}")
            # Intent recognition logic to decide which backend to use
            if "u value" in data.lower() or "weighted u" in data.lower():  # Handle U-value related inputs
                logging.debug("Processing U-value related query.")
                response = chatbot_calculate(data)  # Use the second module to handle U-value calculations
            else:
                logging.debug("Processing building data related query.")
                processor = BuildingDataProcessor(data.lower())  # Normalize case for all processing
                response = processor.process()  # Use the first module to handle building data
            if response:  # Ensure that there is something to send back
               logging.debug(f"Response: {response}")
               await manager.send_personal_message(response, websocket)
            else:
                logging.debug("No response generated.")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"Error in websocket endpoint: {e}")
        manager.disconnect(websocket)
