from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import MongoDB
from routers import conversations, chat, sessions_v2, chat_v2


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up application...")
    await MongoDB.connect()
    yield
    # Shutdown
    print("Shutting down application...")
    await MongoDB.close()


app = FastAPI(
    title="Chat Application API",
    description="Multi-turn chat with image and CSV data support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router)
app.include_router(chat.router)

# Include v2 routers for frontend integration
app.include_router(sessions_v2.router)
app.include_router(chat_v2.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chat Application API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = MongoDB.database
        if db is None:
            return {"status": "unhealthy", "database": "not connected"}

        # Try to ping the database
        await db.command("ping")

        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
