"""词典查询路由"""

from fastapi import APIRouter

from app.models.schemas import DictLookupRequest, DictLookupResponse
from app.services.dict_service import lookup_word

router = APIRouter(prefix="/api/dictionary", tags=["dictionary"])


@router.post("/lookup", response_model=DictLookupResponse)
async def dictionary_lookup(body: DictLookupRequest) -> DictLookupResponse:
    """查询单词释义"""
    return await lookup_word(body.word)
