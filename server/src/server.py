from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dataclasses import dataclass
import uuid
import json


@dataclass
class ConnectionManager:
    def __init__(self):
        """
        Initialize the ConnectionManager class and store the active websocket
        connections in a dictionary
        """
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket):
        """
        Connect to the websocket endpoint and wait for a message to be received and
        send a message to the websocket endpoint with the unique id
        """
        # Connect to the websocket endpoint and wait for a message to be received
        await websocket.accept()
        id = str(uuid.uuid4())
        self.active_connections[id] = websocket

        # Send a message to the websocket endpoint with the unique id
        await self.send_message_to(websocket, json.dumps({"type": "connect", "id": id}))

    def disconnect(self, websocket: WebSocket):
        """
        Close the websocket connection and remove it from the active connections dictionary
        """
        id = self.find_connection_id(websocket)
        del self.active_connections[id]
        return id

    def find_connection_id(self, websocket: WebSocket):
        """
        Find the unique id of a websocket connection in the active connections dictionary
        """
        val_list = list(self.active_connections.values())
        key_list = list(self.active_connections.keys())
        id = val_list.index(websocket)
        return key_list[id]

    async def send_message_to(self, ws: WebSocket, message: str):
        """
        Send a message to a websocket endpoint
        """
        await ws.send_text(message)

    async def broadcast(self, message: str):
        """
        Send a message to all websocket endpoints
        """
        for connection in self.active_connections.values():
            await connection.send_text(message)


# Create a FastAPI instance
app = FastAPI()

# Create a ConnectionManager instance to manage the websocket connections
connection_manager = ConnectionManager()


# Create a websocket endpoint
@app.websocket("/messaging")
async def websocket_endpoint(websocket: WebSocket):
    # Connect to the websocket endpoint and wait for a message to be received
    await connection_manager.connect(websocket)
    # Keep the websocket connection open and wait for a message to be received
    try:
        while True:
            # Receive a message from the websocket endpoint and send it back
            data = await websocket.receive_text()
            print(f"Message text was: {data}")
            # Send a message to all clients
            await connection_manager.broadcast(data)

    except WebSocketDisconnect:
        # Remove the websocket connection from the active connections dictionary
        id = connection_manager.disconnect(websocket)
        # Broadcast a message to all clients that a client has disconnected with the unique id
        await connection_manager.broadcast(json.dumps({"type": "disconnect", "id": id}))
