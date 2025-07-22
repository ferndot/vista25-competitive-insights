from fastapi import HTTPException
from core.supabase import supabase_client
from models.auth import UserCreate, UserLogin, UserResponse, TokenResponse


class AuthService:
    def __init__(self):
        self.client = supabase_client

    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        try:
            response = self.client.auth.sign_up(
                {
                    "email": user_data.email,
                    "password": user_data.password,
                    "options": {"data": {"full_name": user_data.full_name}},
                }
            )

            if not response.user:
                raise HTTPException(status_code=400, detail="Registration failed")

            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_data.full_name,
                created_at=response.user.created_at,
            )

            return TokenResponse(
                access_token=response.session.access_token, user=user_response
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def login_user(self, user_data: UserLogin) -> TokenResponse:
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": user_data.email, "password": user_data.password}
            )

            if not response.user:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
            )

            return TokenResponse(
                access_token=response.session.access_token, user=user_response
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def get_current_user(self, access_token: str) -> UserResponse:
        try:
            response = self.client.auth.get_user(access_token)

            if not response.user:
                raise HTTPException(status_code=401, detail="Invalid token")

            return UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
            )
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))


auth_service = AuthService()
