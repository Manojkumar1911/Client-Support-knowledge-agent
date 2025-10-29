from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as chat_router
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Support AI Backend", version="1.0")

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # For production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat routes
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Health check / root route
@app.get("/")
def root():
    return {"message": "✅ Support AI Backend running successfully!"}


# Run server directly with `python app/main.py`
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
