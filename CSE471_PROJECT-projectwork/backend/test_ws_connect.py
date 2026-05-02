import asyncio
import websockets

async def test_ws():
    rfq_id = "7985b314-a785-4aa6-a991-5102d561561f"
    user_id = "34cdba7d-6ba8-402f-b59c-73ff7f4db9b1"
    uri = f"ws://localhost:8000/ws/chat/{rfq_id}/{user_id}"
    
    print(f"Connecting to {uri}")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            # Wait for a bit
            await asyncio.sleep(2)
            print("Still connected!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
