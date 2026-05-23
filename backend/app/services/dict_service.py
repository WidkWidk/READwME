"""词典查询服务 — 支持在线 API 和本地 fallback"""

import httpx

from app.config import settings
from app.models.schemas import DictDefinition, DictLookupResponse, DictMeaning

LOCAL_FALLBACK = {
    "hello": DictLookupResponse(
        word="hello",
        phonetic="/həˈloʊ/",
        meanings=[
            DictMeaning(
                part_of_speech="exclamation",
                definitions=[DictDefinition(definition="用于问候或引起注意")],
            )
        ],
        source="fallback",
    ),
    "world": DictLookupResponse(
        word="world",
        phonetic="/wɜːrld/",
        meanings=[
            DictMeaning(
                part_of_speech="noun",
                definitions=[DictDefinition(definition="世界；地球")],
            )
        ],
        source="fallback",
    ),
}


async def lookup_word(word: str) -> DictLookupResponse:
    """查询单词释义，网络不通时使用本地 fallback"""
    try:
        async with httpx.AsyncClient(timeout=settings.dict_timeout) as client:
            resp = await client.get(f"{settings.dict_api_base}/{word}")
            if resp.status_code == 200:
                data = resp.json()
                return _parse_api_response(data, word)
            elif resp.status_code == 404:
                return _not_found_response(word)
    except (httpx.TimeoutException, httpx.ConnectError, Exception):
        pass

    if word.lower() in LOCAL_FALLBACK:
        return LOCAL_FALLBACK[word.lower()]

    return DictLookupResponse(
        word=word,
        phonetic=None,
        meanings=[
            DictMeaning(
                part_of_speech="unknown",
                definitions=[DictDefinition(definition="查询失败，请稍后重试")],
            )
        ],
        source="fallback",
    )


def _parse_api_response(data: list, word: str) -> DictLookupResponse:
    """解析词典 API 返回的 JSON 数据"""
    entry = data[0]
    phonetic = entry.get("phonetic", "")
    meanings: list[DictMeaning] = []
    for m in entry.get("meanings", []):
        defs = [
            DictDefinition(
                definition=d.get("definition", ""),
                example=d.get("example"),
            )
            for d in m.get("definitions", [])[:3]
        ]
        meanings.append(DictMeaning(part_of_speech=m.get("partOfSpeech", ""), definitions=defs))
    return DictLookupResponse(word=word, phonetic=phonetic or None, meanings=meanings, source="api")


def _not_found_response(word: str) -> DictLookupResponse:
    """生成未找到单词的响应"""
    return DictLookupResponse(
        word=word,
        phonetic=None,
        meanings=[
            DictMeaning(
                part_of_speech="unknown",
                definitions=[DictDefinition(definition="未找到该单词")],
            )
        ],
        source="api",
    )
