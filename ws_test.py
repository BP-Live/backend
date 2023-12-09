import asyncio
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # You can send a message
        response = await websocket.recv()
        print(response)

asyncio.get_event_loop().run_until_complete(test_websocket())