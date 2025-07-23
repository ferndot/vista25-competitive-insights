from core.supabase import supabase_client
from models.auth import UserCreate, UserLogin, UserResponse, TokenResponse


class AuthError(Exception):
    """Custom exception for authentication errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


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
                raise AuthError("Registration failed", 400)

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
            raise AuthError(str(e), 400)

    async def login_user(self, user_data: UserLogin) -> TokenResponse:
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": user_data.email, "password": user_data.password}
            )

            if not response.user:
                raise AuthError("Invalid credentials", 401)

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
            raise AuthError(str(e), 401)

    async def get_current_user(self, access_token: str) -> UserResponse:
        try:
            response = self.client.auth.get_user(access_token)

            if not response.user:
                raise AuthError("Invalid token", 401)

            return UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name"),
                created_at=response.user.created_at,
            )
        except Exception as e:
            raise AuthError(str(e), 401)


auth_service = AuthService()
