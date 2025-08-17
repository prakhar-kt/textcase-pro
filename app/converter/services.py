from sqlalchemy.ext.asyncio import AsyncSession
from app.account.models import User
from app.converter.models import UserCredits, APIKey, CreditRequest
from app.converter.utils import generate_api_key
from sqlalchemy import select, delete

async def generate_user_api_key(session: AsyncSession, user: User):
    await session.execute(delete(APIKey).where(APIKey.user_id == user.id))
    new_key = generate_api_key()
    key = APIKey(user_id = user.id, key=new_key)
    session.add(key)
    await session.commit()
    return new_key