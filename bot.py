import asyncio
import random
from notifier.telegram import run_bot
from main import check_price

async def scheduler():
    """1시간마다 가격 조회"""
    while True:
        try:
            await check_price()
        except Exception as e:
            print(f"스케줄러 오류: {e}")

        # 55~75분 랜덤 대기 (패턴 감지 방지)
        wait = random.randint(55 * 60, 75 * 60)
        print(f"다음 조회까지 {wait // 60}분 대기")
        await asyncio.sleep(wait)

async def main():
    """스케줄러 + 텔레그램 봇 동시 실행"""
    await asyncio.gather(
        scheduler(),
        run_bot(),
    )

if __name__ == "__main__":
    asyncio.run(main())
