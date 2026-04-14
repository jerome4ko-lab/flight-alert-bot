import asyncio
import random
import os
from playwright.async_api import async_playwright

SCREENSHOT_PATH = "data/screenshot.png"

async def get_screenshot(origin: str, destination: str, date: str) -> str | None:
    ymd = date.replace("-", "")
    url = (
        f"https://flight.naver.com/flights/international/"
        f"{origin}-{destination}-{ymd}?adult=1&fareType=Y"
    )

    print(f"접속 URL: {url}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--window-size=1920,1080",
                ],
            )

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                locale="ko-KR",
                timezone_id="Asia/Seoul",
            )

            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )

            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("초기 DOM 로드 완료, 결과 대기 중...")

            # 1단계: 최소 15초 기본 대기
            await asyncio.sleep(15)

            # 2단계: 가격 텍스트 등장까지 최대 120초 polling
            try:
                await page.wait_for_function(
                    """() => {
                        const text = document.body.innerText || '';
                        const priceMatches = text.match(/[0-9,]{4,}\\s*원/g) || [];
                        const stillLoading = document.querySelectorAll('[class*=skeleton], [class*=Skeleton], [class*=loading], [class*=Loading]').length > 0;
                        return priceMatches.length >= 2 && !stillLoading;
                    }""",
                    timeout=120000,
                    polling=2000,
                )
                print("검색 결과 로딩 완료")
            except Exception as e:
                print(f"결과 대기 타임아웃: {e}")

            # 3단계: 렌더 안정화 추가 대기
            await asyncio.sleep(5)
            await page.evaluate("window.scrollBy(0, 200)")
            await asyncio.sleep(2)

            os.makedirs("data", exist_ok=True)
            await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
            print(f"스크린샷 저장: {SCREENSHOT_PATH}")

            await browser.close()
            return SCREENSHOT_PATH

    except Exception as e:
        print(f"크롤링 오류: {e}")
        return None
