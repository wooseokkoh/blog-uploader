# CapCut MCP 연결 가이드 (내 PC에서)

CapCut 데스크톱 앱이 있는 **내 PC**에서 Claude Code 세션을 열어 진행합니다.
클라우드 세션에서는 CapCut 앱에 접근할 수 없어서 이 작업을 할 수 없습니다.

> ⚠️ 비공식 도구입니다. CapCut 약관상 자동화 접근이 금지돼 있다고 알려져 있어 계정 제재 위험이 0은 아닙니다.
> CapCut 계정 비밀번호는 필요 없고, 어디에도 입력하지 마세요.

## 1. 내 PC에서 Claude Code 세션 열기

- **Claude 데스크톱 앱** → 새 Claude Code 세션 → 작업 폴더 선택 (예: `문서/capcut-mcp`)
- 또는 그 폴더에서 터미널 열고:
  ```bash
  claude remote-control
  ```
  → 휴대폰·웹의 Claude Code 앱에서 이어서 작업 가능

## 2. 사전 준비

- CapCut **데스크톱 앱** (국제판) 설치
- Python 3.10 이상, FFmpeg, Git

## 3. 로컬 Claude에게 붙여 넣을 요청문

```
이 폴더에 VectCutAPI(https://github.com/sun-guannan/VectCutAPI)를 설치하고
Claude Code에 MCP로 연결해줘.

1. git clone 후 venv-capcut 가상환경을 만들고
   requirements.txt, requirements-mcp.txt 설치
2. config.json.example을 config.json으로 복사하고
   draft_profile을 capcut_legacy로 설정 (CapCut 국제판 사용)
3. mcp_server.py를 Claude Code MCP 서버로 등록 (venv 파이썬 사용, 작업 폴더는 VectCutAPI)
   → 등록 후 python test_mcp_client.py로 도구 11개가 잡히는지 확인
4. 이 PC의 CapCut 초안(drafts) 폴더 위치를 찾아서 알려줘
   (save_draft로 생긴 dfd_ 폴더를 그곳에 복사해야 CapCut에서 열림)

설치 명령은 실행 전에 무엇을 하는지 먼저 보여줘.
```

## 4. 연결 후 영상 편집 요청 예시

`출근길미장_2026-11-20.mp4`, `출근길미장_2026-11-20.srt`를 같은 폴더에 둔 뒤:

```
capcut MCP로 새 초안을 만들어줘. 세로 1080x1920.
1) 출근길미장_2026-11-20.mp4를 비디오 트랙에 넣고
2) 출근길미장_2026-11-20.srt를 자막으로 추가 (영상에 자막이 이미 있으니 투명도 0)
3) 저장한 뒤 dfd_ 폴더를 CapCut 초안 폴더로 복사해줘
```

## 5. 알아둘 한계

- **TTS(음성 내레이션) 도구는 없습니다.** CapCut에서 자막 전체 선택 → **텍스트 읽기**로 음성을 직접 입혀야 합니다.
- **최종 내보내기(Export)는 CapCut에서 직접** 눌러야 합니다.
- CapCut 업데이트 후 초안이 안 열리면 VectCutAPI를 최신으로 업데이트(`git pull`)하세요.
