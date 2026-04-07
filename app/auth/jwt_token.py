import uuid
import jwt



async def create_access_token(user_id: int) -> str:
    