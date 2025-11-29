# Arena: LLM-Powered Coding Problem Solver

Here's how you can use the application:

  1. Check the Health
  You can check if the server and the configured LLM provider are running by navigating to http://localhost:8000/api/health in your browser or using
```powershell
   curl http://localhost:8000/api/health
```

  1. Run a Problem Synchronously (Simple)
  You can POST a problem to the /api/arena endpoint. The server will run the entire process and return the final results all at once.

  Example using `curl`:
```powershell
   curl -X POST "http://localhost:8000/api/arena" \
   -H "Content-Type: application/json" \
   -d '{
     "problem": "Write a function named `sum_evens` that returns the sum of all even numbers in a list of integers."
   }'
```
  3. Run a Problem with Real-Time Updates (Advanced)
  For a better experience (as intended for the frontend), you can connect to the /ws/arena WebSocket. The server will send you events as they happen (problem parsing, agent generation,
  test results, etc.).