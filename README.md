# ✈️ 항공권 최저가 알림 봇

스카이스캐너 최저가를 모니터링하고 텔레그램으로 알림을 보내는 봇

## 기술 스택
- Python + Playwright (크롤링)
- Claude Vision API (가격 파싱)
- Telegram Bot API (알림 + 명령)
- Railway (배포)

## 텔레그램 명령어
```
/set 260824   날짜 변경 (YY MM DD)
/check        지금 바로 조회
/status       현재 설정 확인
/history      최근 가격 이력
/help         도움말
```

## Railway 배포 방법

### 1. GitHub 레포 생성 후 푸시
```bash
git init
git add .
git commit -m "init"
git remote add origin https://github.com/YOUR_ID/flight-alert-bot.git
git push -u origin main
```

### 2. Railway 세팅
1. railway.com 접속 → New Project → Deploy from GitHub
2. 레포 선택
3. Variables 탭에서 환경변수 추가:

```
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_TOKEN=YOUR_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_CHAT_ID
```

### 3. 배포 완료
Railway가 Dockerfile 감지해서 자동 빌드 & 실행

## 환경변수
| 변수 | 설명 |
|------|------|
| ANTHROPIC_API_KEY | Anthropic API 키 |
| TELEGRAM_TOKEN | 텔레그램 봇 토큰 |
| TELEGRAM_CHAT_ID | 텔레그램 채팅 ID |

## 파일 구조
```
flight-alert-bot/
├── bot.py              # 진입점 (스케줄러 + 봇 동시 실행)
├── main.py             # 가격 조회 로직
├── crawler/
│   └── skyscanner.py   # Playwright 크롤링
├── parser/
│   └── vision.py       # Claude Vision 파싱
├── notifier/
│   └── telegram.py     # 텔레그램 알림 + 명령 처리
├── data/
│   └── config.json     # 노선/날짜 설정
├── Dockerfile
└── requirements.txt
```
