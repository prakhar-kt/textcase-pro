from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from app.account.models import User
from app.converter.models import UserCredits, APIKey, CreditRequest
from app.converter.utils import generate_api_key
from sqlalchemy import select, delete
from fastapi import HTTPException


async def generate_user_api_key(session: AsyncSession, user: User):
    await session.execute(delete(APIKey).where(APIKey.user_id == user.id))
    new_key = generate_api_key()
    key = APIKey(user_id=user.id, key=new_key)
    session.add(key)
    await session.commit()
    return new_key


async def get_user_api_key(session: AsyncSession, user: User):
    stmt = select(APIKey).where(APIKey.user_id == user.id)
    result = await session.scalars(stmt)
    key_obj = result.first()
    if not key_obj:
        return HTTPException(status_code=404, detail="API Key not found")

    return key_obj.key


async def get_or_create_user_credits(session: AsyncSession, user: Union[User, int]):
    user_id = user.id if isinstance(user, User) else user
    stmt = select(UserCredits).where(UserCredits.user_id == user_id)
    result = await session.scalars(stmt)
    credits_obj = result.first()
    if not credits_obj:
        credits_obj = UserCredits(user_id=user_id, credits=10)
        session.add(credits_obj)
        await session.commit()
        await session.refresh(credits_obj)
    return credits_obj


async def get_credits_request_list(session: AsyncSession, user: User):
    result = await session.scalars(
        select(CreditRequest).order_by(CreditRequest.created_at.desc())
    )
    return result.all()


async def submit_credit_request(session: AsyncSession, user: User, credits: int):
    credit_request = CreditRequest(
        user_id=user.id, credits_requested=credits, status="pending"
    )
    session.add(credit_request)
    await session.commit()
    await session.refresh(credit_request)
    return credit_request


async def approve_credit_request(session: AsyncSession, request_id: int):
    req = await session.get(CreditRequest, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Already processed")
    credits_obj = await get_or_create_user_credits(session, req.user_id)
    credits_obj.credits += req.credits_requested
    req.status = "approved"
    await session.commit()
    await session.refresh(req)
    return req


