import httpx
import json
import os
import asyncio

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
CONFIG_PATH = "data/config.json"
HISTORY_PATH = "data/price_history.json"

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def send_message(text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
        )

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_history():
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except:
        return {"lowest": None, "records": []}

async def handle_update(update: dict):
    message = update.get("message", {})
    text = message.get("text", "").strip()
    chat_id = str(message.get("chat", {}).get("id", ""))

    # 허용된 chat_id만 처리
    if chat_id != TELEGRAM_CHAT_ID:
        return

    if text.startswith("/set"):
        # /set 260824
        parts = text.split()
        if len(parts) == 2 and len(parts[1]) == 6:
            date = parts[1]
            config = load_config()
            config["date"] = date
            save_config(config)

            # 최저가 이력 초기화 (날짜 바뀌면 새로 시작)
            history = {"lowest": None, "records": []}
            with open(HISTORY_PATH, "w") as f:
                json.dump(history, f)

            d = date
            full_date = f"20{d[:2]}-{d[2:4]}-{d[4:]}"
            await send_message(f"✅ 날짜 변경 완료!\n📅 {full_date}\n최저가 이력 초기화됨")
        else:
            await send_message("❌ 형식 오류\n사용법: /set 260824")

    elif text == "/check":
        await send_message("🔍 지금 바로 조회할게요...")
        # main.py의 check_price 호출
        from main import check_price
        await check_price()

    elif text == "/status":
        config = load_config()
        history = load_history()
        d = config["date"]
        full_date = f"20{d[:2]}-{d[2:4]}-{d[4:]}"
        lowest = history.get("lowest")
        lowest_str = f"{lowest:,}원" if lowest else "아직 없음"
        await send_message(
            f"📋 현재 설정\n\n"
            f"노선: {config['origin']} → {config['destination']}\n"
            f"날짜: {full_date}\n"
            f"기록 최저가: {lowest_str}\n"
            f"조회 횟수: {len(history.get('records', []))}회"
        )

    elif text == "/history":
        history = load_history()
        records = history.get("records", [])[-5:]  # 최근 5개
        if not records:
            await send_message("📭 가격 이력 없음")
            return
        lines = ["📈 최근 가격 이력\n"]
        for r in reversed(records):
            ts = r["timestamp"][:16].replace("T", " ")
            lines.append(f"{ts}: {r['price']:,}원")
        await send_message("\n".join(lines))

    elif text == "/help":
        await send_message(
            "✈️ 항공권 알림 봇\n\n"
            "/set 260824 - 날짜 변경\n"
            "/check - 지금 바로 조회\n"
            "/status - 현재 설정 확인\n"
            "/history - 최근 가격 이력\n"
            "/help - 도움말"
        )

async def run_bot():
    """Polling 방식으로 텔레그램 명령 수신"""
    offset = 0
    print("텔레그램 봇 시작...")

    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(
                    f"{BASE_URL}/getUpdates",
                    params={"offset": offset, "timeout": 30},
                    timeout=35,
                )
                data = response.json()

                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    await handle_update(update)

            except Exception as e:
                print(f"봇 오류: {e}")
                await asyncio.sleep(5)
