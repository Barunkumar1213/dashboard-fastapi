from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, notes, admin

app = FastAPI(title="Notes API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://dashboard-fastapi.vercel.app",  # Vercel backend (for self)
        "https://your-frontend-domain.vercel.app",  # Replace with your frontend domain
        "https://localhost:3000"  # HTTPS local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def root():
    return {"message": "Notes API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)