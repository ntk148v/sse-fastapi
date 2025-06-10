from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import asyncio
import uvicorn
from pathlib import Path

app = FastAPI(title="Soccer Livescore SSE API")

# Mount the frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the mock data
DATA_FILE = Path(__file__).parent / "data" / "soccer_data.json"

def load_mock_data():
    if not DATA_FILE.exists():
        # Create data directory if it doesn't exist
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        # Create a sample data point if file doesn't exist
        sample_data = [{"score": {"home": 0, "away": 0}, "time": "0:00", "match": "Team A vs Team B"}]
        with open(DATA_FILE, "w") as f:
            json.dump(sample_data, f, indent=2)

    with open(DATA_FILE, "r") as f:
        return json.load(f)

async def livescore_generator():
    """
    Generator that yields soccer livescore data as Server-Sent Events.
    Each event includes the current score, match time, and team names.
    """
    data = load_mock_data()
    for update in data:
        # Convert the data point to JSON string
        event_data = json.dumps(update)
        # Yield the event in SSE format
        yield f"data: {event_data}\n\n"
        # Simulate real-time updates with a delay
        await asyncio.sleep(2)  # 2-second delay between updates

@app.get("/")
async def root():
    """Serve the frontend HTML page"""
    return FileResponse("frontend/index.html")

@app.get("/livescore")
async def livescore():
    """
    Endpoint that streams soccer livescore updates using Server-Sent Events.
    """
    return StreamingResponse(
        livescore_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

def main():
    """Run the FastAPI application using uvicorn server."""
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
