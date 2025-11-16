from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, notes, admin
from mangum import Mangum
import os

app = FastAPI(title="Notes API", version="1.0.0")

SECRET_KEY = os.getenv("SECRET_KEY", "my-super-secret-key-for-notes-app-12345")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (not recommended for production)
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

@app.get("/debug")
def debug():
    return {
        "secret_set": bool(SECRET_KEY),
        "secret_length": len(SECRET_KEY) if SECRET_KEY else 0,
        "algorithm": ALGORITHM,
        "token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
    }
# def root():
#     return {"message": "Notes API is running"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
handler = Mangum(app)