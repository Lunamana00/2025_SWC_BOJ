import httpx

async def fetch_solvedac_data():
    url = "https://solved.ac/api/v3/user/top_100?handle=kth000928"
    headers = {
        "Accept": "application/json",
        "x-solvedac-language": "ko"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response.json()

# 비동기 함수 실행 방법
import asyncio
data = asyncio.run(fetch_solvedac_data())
print(data["items"][0])
