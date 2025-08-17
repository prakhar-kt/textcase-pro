from fastapi import APIRouter, Depends
from app.converter.schemas import APIKeyOut
from app.converter.services import generate_user_api_key
from app.db.config import SessionDep
from app.account.models import User
from app.account.dependencies import get_current_user

router = APIRouter()

@router.post("/generate-api-key", response_model=APIKeyOut)
async def generate_api_key(session: SessionDep, 
                           user: User = Depends(get_current_user)):
    key = await generate_user_api_key(session, user)
    return {"key": key}


