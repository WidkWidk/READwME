"""词典查询接口测试"""

import json
import pytest
import httpx
from httpx import AsyncClient
from pytest_httpx import HTTPXMock


async def test_lookup_fallback_on_network_error(
    client: AsyncClient, httpx_mock: HTTPXMock
) -> None:
    """测试网络不通时返回 fallback 结果"""
    httpx_mock.add_exception(httpx.ConnectError("网络不通"))

    resp = await client.post("/api/dictionary/lookup", json={"word": "hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "hello"
    assert data["source"] == "fallback"
    assert len(data["meanings"]) > 0


async def test_lookup_unknown_word_fallback(
    client: AsyncClient, httpx_mock: HTTPXMock
) -> None:
    """测试网络不通且无本地词条时返回通用 fallback"""
    httpx_mock.add_exception(httpx.TimeoutException("超时"))

    resp = await client.post("/api/dictionary/lookup", json={"word": "xyzunknown"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "xyzunknown"
    assert data["source"] == "fallback"
    assert "查询失败" in data["meanings"][0]["definitions"][0]["definition"]


async def test_lookup_api_success(
    client: AsyncClient, httpx_mock: HTTPXMock
) -> None:
    """测试 API 正常返回时解析结果"""
    mock_response = [
        {
            "word": "python",
            "phonetic": "/ˈpaɪθɑːn/",
            "meanings": [
                {
                    "partOfSpeech": "noun",
                    "definitions": [
                        {
                            "definition": "A large heavy-bodied snake.",
                            "example": "The python coiled around its prey.",
                        }
                    ],
                }
            ],
        }
    ]
    httpx_mock.add_response(
        status_code=200,
        json=mock_response,
    )

    resp = await client.post("/api/dictionary/lookup", json={"word": "python"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "python"
    assert data["phonetic"] == "/ˈpaɪθɑːn/"
    assert data["source"] == "api"
    assert data["meanings"][0]["part_of_speech"] == "noun"
    assert "snake" in data["meanings"][0]["definitions"][0]["definition"]


async def test_lookup_word_not_found(
    client: AsyncClient, httpx_mock: HTTPXMock
) -> None:
    """测试 API 返回 404 时的处理"""
    httpx_mock.add_response(status_code=404)

    resp = await client.post("/api/dictionary/lookup", json={"word": "zzznonsense"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "zzznonsense"
    assert "未找到" in data["meanings"][0]["definitions"][0]["definition"]


async def test_lookup_empty_word(client: AsyncClient) -> None:
    """测试空单词被拒绝"""
    resp = await client.post("/api/dictionary/lookup", json={"word": ""})
    assert resp.status_code == 422


async def test_lookup_local_fallback_world(
    client: AsyncClient, httpx_mock: HTTPXMock
) -> None:
    """测试本地 fallback 词条 world"""
    httpx_mock.add_exception(httpx.ConnectError("网络不通"))

    resp = await client.post("/api/dictionary/lookup", json={"word": "world"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["word"] == "world"
    assert data["source"] == "fallback"
    assert data["phonetic"] == "/wɜːrld/"
