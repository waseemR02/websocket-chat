from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# Create a FastAPI instance
app = FastAPI()


# Create a websocket endpoint
@app.websocket("/messaging")
async def websocket_endpoint(websocket: WebSocket):
    # Connect to the websocket endpoint and wait for a message to be received
    await websocket.accept()
    # Keep the websocket connection open and wait for a message to be received
    try:
        while True:
            # Receive a message from the websocket endpoint and send it back
            data = await websocket.receive_text()
            print(f"Message text was: {data}")
            await websocket.send_text(data)
    except WebSocketDisconnect:
        # Close the websocket connection
        await websocket.close()
