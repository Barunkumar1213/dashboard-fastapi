from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
import uuid
import os

from models.user import UserCreate, UserResponse, UserLogin, Token, TokenData
from database.db_file import db

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = "my-super-secret-key-for-notes-app-12345"
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# -----------------------------------------------------
# FIXED: SAFELY HANDLE BCRYPT 72-BYTE LIMIT
# -----------------------------------------------------
def truncate_password(password: str) -> str:
    """
    Safely truncate a password to 72 bytes for bcrypt.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return password_bytes


def verify_password(plain_password, hashed_password):
    truncated_bytes = truncate_password(plain_password)
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(truncated_bytes, hashed_bytes)


def get_password_hash(password):
    truncated_bytes = truncate_password(password)
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(truncated_bytes, salt)
    return hashed_bytes.decode('utf-8')


# -----------------------------------------------------
# JWT TOKEN HELPERS
# -----------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    user = db.get_user_by_email(email=token_data.email)
    if not user:
        raise credentials_exception

    return user


# -----------------------------------------------------
# ROUTES
# -----------------------------------------------------

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate):
    # Password validation
    if len(user.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 chars")
    if len(user.password) > 200:  # just to avoid extremely large inputs
        raise HTTPException(status_code=400, detail="Password too long")

    # Check email exists
    existing_user = db.get_user_by_email(email=user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = get_password_hash(user.password)

    new_user = {
        "id": str(uuid.uuid4()),
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    }

    created_user = db.add_user(new_user)
    return UserResponse(**created_user)


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin):
    user = db.get_user_by_email(email=user_credentials.email)

    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)
