import asyncio
import json
import os
from crawler.skyscanner import get_screenshot
from parser.vision import parse_price
from notifier.telegram import send_message
from datetime import datetime

CONFIG_PATH = "data/config.json"
HISTORY_PATH = "data/price_history.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def load_history():
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except:
        return {"lowest": None, "records": []}

def save_history(history):
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

async def check_price():
    config = load_config()
    history = load_history()

    origin = config["origin"]
    destination = config["destination"]
    date = config["date"]  # YYMMDD 형식

    print(f"[{datetime.now()}] 가격 조회 시작: {origin} → {destination} ({date})")

    # 날짜 변환 YYMMDD → YYYY-MM-DD
    d = date
    full_date = f"20{d[:2]}-{d[2:4]}-{d[4:]}"

    # 스크린샷 캡처
    screenshot_path = await get_screenshot(origin, destination, full_date)
    if not screenshot_path:
        await send_message("⚠️ 스카이스캐너 캡처 실패. 봇 감지 또는 네트워크 오류.")
        return

    # Vision으로 가격 파싱
    price = await parse_price(screenshot_path)
    if not price:
        await send_message("⚠️ 가격 파싱 실패. 스크린샷을 확인하세요.")
        return

    print(f"현재 최저가: {price:,}원")

    # 가격 이력 저장
    record = {
        "timestamp": datetime.now().isoformat(),
        "price": price,
        "date": date
    }
    history["records"].append(record)

    # 최저가 갱신 여부 확인
    prev_lowest = history.get("lowest")
    if prev_lowest is None or price < prev_lowest:
        history["lowest"] = price
        save_history(history)

        msg = (
            f"✈️ 최저가 갱신!\n\n"
            f"노선: {origin} → {destination}\n"
            f"날짜: {full_date}\n"
            f"💰 현재 최저가: {price:,}원\n"
            f"📉 이전 최저가: {f'{prev_lowest:,}원' if prev_lowest else '없음'}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        await send_message(msg)
        print("✅ 최저가 갱신 알림 발송!")
    else:
        save_history(history)
        print(f"최저가 변동 없음 (현재 최저: {prev_lowest:,}원)")

if __name__ == "__main__":
    asyncio.run(check_price())
