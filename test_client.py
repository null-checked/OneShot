import asyncio
import websockets
import json

async def run_arena_test():
    """Connects to the WebSocket and tests the arena."""
    uri = "ws://localhost:8000/ws/arena"
    try:
        async with websockets.connect(uri) as websocket:
            print("--- Connected to WebSocket ---")
            
            # 1. Send the problem description
            problem_description = "Write a function named `sum_evens` that returns the sum of all even numbers in a list of integers."
            print(f"--- Sending problem: '{problem_description}' ---")
            await websocket.send(json.dumps({
                "problem": problem_description
            }))

            # 2. Listen for real-time events from the server
            while True:
                message = await websocket.recv()
                event = json.loads(message)
                
                print(f"\n--- Received event: {event['type']} ---")
                print(json.dumps(event.get('data', {}), indent=2))
                
                # Stop listening after the final results are received
                if event['type'] == 'final_results':
                    print("\n--- Workflow complete ---")
                    break
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(run_arena_test())
