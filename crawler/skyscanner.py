import asyncio
import random
import os
from playwright.async_api import async_playwright

SCREENSHOT_PATH = "data/screenshot.png"

async def get_screenshot(origin: str, destination: str, date: str) -> str | None:
    url = (
        f"https://www.skyscanner.co.kr/transport/flights/"
        f"{origin}/{destination}/{date.replace('-', '')}/"
        f"?adults=1&currency=KRW"
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
                    "--disable-infobars",
                    "--window-size=1920,1080",
                ]
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

            # 봇 감지 우회
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
                Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en-US'] });
            """)

            page = await context.new_page()

            # 랜덤 딜레이 (인간처럼)
            await asyncio.sleep(random.uniform(1, 3))
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # 페이지 로딩 대기
            await asyncio.sleep(random.uniform(4, 7))

            # 스크롤 (인간처럼)
            await page.mouse.move(random.randint(400, 800), random.randint(200, 400))
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await page.evaluate("window.scrollBy(0, 300)")
            await asyncio.sleep(random.uniform(2, 4))

            # 스크린샷
            os.makedirs("data", exist_ok=True)
            await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
            print(f"스크린샷 저장: {SCREENSHOT_PATH}")

            await browser.close()
            return SCREENSHOT_PATH

    except Exception as e:
        print(f"크롤링 오류: {e}")
        return None
