import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router

app = FastAPI(
    title="ACDSF Core Dashboard API Server",
    description="Backend interface orchestrating Administrator, Analyst, Incident Manager, and Executive dashboards."
)

# Configure CORS so React frontend can connect cleanly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bind routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "ACDSF core API backend running."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8030)
