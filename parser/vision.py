import base64
import json
import httpx
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

async def parse_price(screenshot_path: str) -> int | None:
    try:
        with open(screenshot_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")

        prompt = """이 네이버 항공권 검색 결과 화면에서 가장 저렴한 항공권 가격을 찾아주세요.

다음 JSON 형식으로만 응답하세요. 다른 텍스트는 절대 포함하지 마세요:
{"price": 숫자, "currency": "KRW", "found": true}

가격을 찾지 못한 경우:
{"price": null, "currency": null, "found": false}

주의사항:
- 가격은 원화(₩) 기준 숫자만 (쉼표 제외)
- 가장 낮은 가격 기준
- 화면에 가격이 없거나 로딩 중이면 found: false"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 100,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_data,
                                    },
                                },
                                {"type": "text", "text": prompt},
                            ],
                        }
                    ],
                },
                timeout=30,
            )

        data = response.json()
        text = data["content"][0]["text"].strip()
        result = json.loads(text)

        if result.get("found") and result.get("price"):
            print(f"파싱 성공: {result['price']:,}원")
            return int(result["price"])
        else:
            print("가격 파싱 실패: 화면에서 가격을 찾지 못함")
            return None

    except Exception as e:
        print(f"Vision 파싱 오류: {e}")
        return None
