# 블로그 사진 올리기

폰의 사진·영상을 GitHub 비공개 워크스페이스(`do-better-workspace`)의 `00-inbox/raw/날짜_포스팅이름/` 폴더로 바로 올리는 웹앱입니다.

- 앱 주소: https://wooseokkoh.github.io/blog-uploader/
- 이 저장소에는 **앱 코드만** 있습니다. 사진과 토큰은 여기에 저장되지 않습니다.
- 토큰은 폰 브라우저 안에만 저장되고, GitHub(api.github.com) 외에는 어디로도 보내지 않습니다.

## 1. 토큰 만들기 (처음 한 번)

1. https://github.com/settings/personal-access-tokens/new 접속
2. **Token name**: `blog-uploader`
3. **Expiration**: 1년 정도로 설정 (만료되면 새로 만들어 앱 설정에 다시 넣기)
4. **Repository access**: **Only select repositories** → `do-better-workspace`
5. **Permissions → Repository permissions → Contents**: **Read and write**
6. **Generate token** → `github_pat_...` 복사 → 앱 설정(⚙)에 붙여넣기 → **저장하고 연결 확인**

## 2. 폰에 설치

- **갤럭시(크롬)**: 앱 주소 접속 → 오른쪽 위 **⋮** → **홈 화면에 추가** (또는 **앱 설치**)
- **아이폰(사파리)**: 앱 주소 접속 → 아래 **공유** 버튼 → **홈 화면에 추가**

## 3. 사용법

1. 포스팅 이름 입력 (예: `저스트짐`)
2. **사진·영상 선택** → 여러 장 선택
3. **N개 올리기** → 완료 메시지가 뜰 때까지 화면 켜 두기

갤럭시에서는 갤러리에서 사진 선택 → **공유** → **사진올리기**로도 보낼 수 있습니다.

- 파일 이름 앞에 `01_`, `02_` 순번이 붙어 고른 순서가 유지됩니다.
- 같은 날 같은 포스팅 이름으로 또 올리면 번호가 이어서 붙습니다.
- 파일 1개당 100MB까지 올릴 수 있습니다 (GitHub 한도).
