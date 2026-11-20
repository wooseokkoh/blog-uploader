# 출근길 미장 — 매주 1분 영상 템플릿

매주 이 파일을 복사해서 `YYYY-MM-DD.md`로 저장하고 `{ }` 부분만 채우면 됩니다.
예시: [2026-11-20.md](./2026-11-20.md)

---

## 0. 제작 순서 (체크리스트)

- [ ] Claude에게 "지난 일주일 미국장 중요 뉴스 5~6개 찾아서 이 템플릿 채워줘" 요청
- [ ] 수치는 **목요일 또는 금요일 종가 기준**으로 통일하고, 하단 고정 문구에 기준일 표기
- [ ] Flow 클립 생성 (무료 계정은 하루 약 5개 → **이틀에 나눠 생성**)
  - 1번 인트로 · 8번 아웃트로는 **처음 한 번만 만들고 매주 재사용** → 매주 6개만 생성
- [ ] CapCut에서 클립 이어 붙이기 + 한글 자막 + TTS 내레이션 + 로고 + BGM
- [ ] 게시글 문구·해시태그 붙여서 업로드

---

## 1. 이번 주 핵심 뉴스 ({시작일}~{종료일}, {기준일} 종가 기준)

1. **{지수 흐름}**: {S&P500 / 나스닥 / 다우 주간 등락}
2. **{이슈 1}**: {한 줄 요약}
3. **{이슈 2}**: {한 줄 요약}
4. **{이슈 3}**: {한 줄 요약}
5. **{금리·연준}**: {한 줄 요약}
6. **{화제 종목·IPO}**: {한 줄 요약}

출처:
- {링크}

---

## 2. 1분 콘티 (세로 9:16, 8초 클립 8개)

| # | 시간 | 내레이션 | 화면 자막 |
|---|---|---|---|
| 1 | 0~4초 | 출근길 미장! 지난주 미국장, 1분 요약 갑니다. | **출근길 미장** 로고 |
| 2 | 4~12초 | {지수 흐름 내레이션} | {자막} |
| 3 | 12~20초 | {이슈 1 내레이션} | {자막} |
| 4 | 20~28초 | {이슈 2 내레이션} | {자막} |
| 5 | 28~36초 | {이슈 3 내레이션} | {자막} |
| 6 | 36~44초 | {금리·연준 내레이션} | {자막} |
| 7 | 44~52초 | {화제 종목 내레이션} | {자막} |
| 8 | 52~60초 | 매일 아침 출근길 1분이면 미국장 끝! 도움 됐다면 좋아요, 놓치지 않으려면 팔로우 눌러주세요! | 👍 좋아요 · ➕ 팔로우 |

- 하단 고정 문구: `투자 권유 아님 · {기준일} 종가 기준`
- 내레이션 1줄은 **8초 ≈ 40~45음절** 이내로 (한국어 TTS 기준)
- 1번 클립은 앞 4초만 잘라 써서 전체 60초 맞추기

---

## 3. Flow 프롬프트

**공통 스타일** (모든 프롬프트 끝에 붙이기 — 클립끼리 톤 통일):
```
, cinematic, cool morning blue with warm sunrise accents, vertical 9:16, smooth slow camera motion, no text, no logos, no real people's faces
```

**고정 클립 (매주 재사용)**
1. 인트로: `A crowded morning subway train at sunrise, a commuter in a trench coat holding a coffee and a smartphone glowing with a stock chart, city skyline passing outside the window`
8. 아웃트로 (좋아요·팔로우): `A smiling commuter walking out of a subway station into bright morning sunlight, turning to the camera and giving a thumbs-up, warm hopeful mood`

**매주 바뀌는 클립 2~7** — 자주 쓰는 장면 예시:
| 상황 | 프롬프트 |
|---|---|
| 지수 하락 | `A giant digital stock ticker board on a dim trading floor, numbers flickering and turning red, downward arrows cascading` |
| 지수 상승 | `A giant digital stock ticker board on a bright trading floor, numbers turning green, upward arrows rising like fireworks` |
| AI·반도체 | `Rows of servers in a futuristic AI data center, glowing blue lights, slow dolly shot` |
| 거품·불안 | `A translucent soap bubble floating among server racks, lights shifting to red, the bubble slowly popping` |
| CEO·경영진 이슈 | `An empty black leather executive chair at the head of a long glass boardroom table, city lights behind, slow push-in` |
| 실적 호조 / 주가 반전 | `A glowing green microchip on a dark surface, a holographic chart rising above it, then the line sharply turning red and falling` |
| 금리 인상 | `A grand neoclassical central bank building with stone columns at dawn, a glowing holographic percentage sign rising upward in the sky` |
| 금리 인하 | `A grand neoclassical central bank building at dawn, a glowing holographic percentage sign slowly descending` |
| IPO·상장 | `Golden confetti falling over a busy trading floor, a large bell ringing, screens showing a fast rising green line` |
| 유가·에너지 | `Oil pump jacks silhouetted against a sunrise, a holographic price chart floating above` |
| 고용·소비 | `A busy city shopping street in the morning, people with shopping bags, holographic bar charts above the crowd` |

**Claude in Chrome 요청 문구**
> labs.google Flow에서 모델은 Veo 3.1 Lite, 화면 비율은 세로(9:16)로 설정하고, 아래 프롬프트로 영상을 하나씩 만들어서 다운로드해줘. 오늘은 {N}~{M}번만.

---

## 4. 편집 팁

- 한글 자막·로고·숫자는 **편집앱에서** 넣기 (Veo가 그리는 글자는 깨지기 쉬움)
- 내레이션은 편집앱 **TTS** 사용 (Veo 한국어 음성은 품질이 들쑥날쑥)
- 실존 인물 얼굴·회사 로고는 생성하지 않기 (초상권·상표 문제)
- 무료 계정은 Veo 3.1 **Quality 불가** → 항상 **Lite** 지정

---

## 5. 게시글 문구

```
☕ 출근길 1분, 지난주 미국장 핵심만!
{핵심 키워드 1} · {키워드 2} · {키워드 3} · {키워드 4}

👍 도움 됐다면 좋아요
➕ 매일 아침 받아보려면 팔로우
💬 이번 주 가장 충격적인 뉴스는? 댓글로!

#출근길미장 #미국주식 #미장 #S&P500 #나스닥 #경제뉴스 {#종목태그}
※ 투자 권유가 아닌 정보 제공 목적입니다.
```
