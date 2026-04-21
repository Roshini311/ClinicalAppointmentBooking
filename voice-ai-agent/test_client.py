import asyncio
import websockets
import json

async def test_client():
    uri = "ws://localhost:8000/ws/testsession123"
    
    async with websockets.connect(uri) as ws:
        print("Connected to Voice AI WebSocket")
        
        # Test 1: Booking
        print("\n--- Test 1: Booking ---")
        msg = "Book appointment with cardiologist tomorrow"
        await ws.send(msg.encode('utf-8'))
        
        # Receive audio bytes
        audio_resp = await ws.recv()
        print(f"Received Audio Bytes (mock): {audio_resp.decode('utf-8')}")
        
        # Receive latency json
        latency_str = await ws.recv()
        print(f"Metrics: {latency_str}")
        
        # Test 2: Cancel
        print("\n--- Test 2: Cancellation ---")
        msg = "Cancel my appointment please"
        await ws.send(msg.encode('utf-8'))
        
        audio_resp = await ws.recv()
        print(f"Received Audio Bytes: {audio_resp.decode('utf-8')}")
        latency_str = await ws.recv()
        print(f"Metrics: {latency_str}")

if __name__ == "__main__":
    asyncio.run(test_client())
