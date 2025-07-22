from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from services.auth import auth_service

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    return await auth_service.login_user(user_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return await auth_service.get_current_user(credentials.credentials)
