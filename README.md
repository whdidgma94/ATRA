# ATRA — Android Test Report Automation

> Android 실기기에 자동으로 테스트를 실행하고, 결과를 HTML 리포트 · 이메일로 정리해주는 데스크탑 도구입니다.

---

## 목차

1. [ATRA가 뭔가요?](#1-atra가-뭔가요)
2. [주요 기능](#2-주요-기능)
3. [전체 흐름](#3-전체-흐름)
4. [사전 요구사항](#4-사전-요구사항)
5. [설치 방법](#5-설치-방법)
6. [실행 방법](#6-실행-방법)
7. [프로젝트 구조](#7-프로젝트-구조)
8. [테스트 케이스 작성법](#8-테스트-케이스-작성법)
9. [설정 안내](#9-설정-안내)
10. [자주 묻는 질문 (FAQ)](#10-자주-묻는-질문-faq)

---

## 1. ATRA가 뭔가요?

**ATRA**는 **Android Test Report Automation**의 약자입니다.

쉽게 말하면:

> "Android 폰 여러 대에 테스트를 동시에 자동으로 돌리고, 결과를 보기 좋게 정리해 이메일로 보내주는 프로그램"

예를 들어, Samsung SmartThings 앱이 Android 12 · 13 · 14 버전에서 모두 정상 동작하는지 확인해야 할 때, 기기를 PC에 꽂고 ATRA를 실행하면 알아서 테스트를 돌린 뒤 리포트를 만들어줍니다.

---

## 2. 주요 기능

| 기능 | 설명 |
|------|------|
| **다중 기기 동시 테스트** | Android 폰 여러 대를 동시에 연결해 병렬로 테스트 실행 |
| **화면 자동 녹화** | 각 테스트 케이스 실행 중 화면을 MP4로 녹화 저장 |
| **자동 로그 수집** | 테스트 실패 시 스크린샷 · 로그캣 · ADB 버그리포트 자동 저장 |
| **실패 케이스 검토 UI** | 실패한 테스트를 화면에서 직접 확인하고 결과를 조정 |
| **PLM 이슈 연동** | 이슈 번호와 코멘트를 리포트에 함께 기록 |
| **HTML 리포트 생성** | 전체 테스트 결과를 보기 좋은 HTML 파일로 자동 생성 |
| **이메일 폼 생성** | 리포트를 이메일로 보낼 수 있는 형태로 변환 |

---

## 3. 전체 흐름

```
[ATRA 실행]
     │
     ▼
[모드 선택]
  ├─ 테스트 실행   ──────────────────────────────────┐
  └─ 기존 로그로 리포트만 생성 ──────────────────┐  │
                                                 │  │
                                                 │  ▼
                                                 │ [기기 선택]
                                                 │     │
                                                 │     ▼
                                                 │ [테스트 자동 실행]
                                                 │ (기기마다 Appium 서버 기동 →
                                                 │  TC 순차 실행 → 화면 녹화)
                                                 │     │
                                                 └─────┤
                                                       ▼
                                               [결과 분석 & 실패 검토]
                                                       │
                                                       ▼
                                               [PLM 이슈 정보 입력]
                                                       │
                                                       ▼
                                               [HTML 리포트 생성]
                                                       │
                                                       ▼
                                               [이메일 폼 생성 & 전송]
```

---

## 4. 사전 요구사항

ATRA를 실행하려면 아래 프로그램들이 PC에 미리 설치되어 있어야 합니다.

### 필수 설치 목록

| 프로그램 | 버전 | 확인 명령어 |
|----------|------|-------------|
| **Python** | 3.11 이상 | `python --version` |
| **Node.js** | 18 이상 | `node --version` |
| **Appium** | 2.x | `appium --version` |
| **Android SDK (ADB)** | 최신 | `adb --version` |
| **FFmpeg** | 최신 | `ffmpeg -version` |

### 설치 순서

#### 1) Python 설치
[python.org](https://www.python.org/downloads/)에서 Python 3.11 이상을 다운로드 후 설치합니다.
> ⚠️ 설치 시 "Add Python to PATH" 옵션을 반드시 체크하세요.

#### 2) Node.js 설치
[nodejs.org](https://nodejs.org/)에서 LTS 버전을 다운로드 후 설치합니다.

#### 3) Appium 설치
```bash
npm install -g appium
appium driver install uiautomator2
```

#### 4) Android SDK (ADB) 설치
[Android Studio](https://developer.android.com/studio)를 설치하면 ADB가 함께 포함됩니다.
또는 Android SDK Platform-Tools만 별도로 다운로드할 수 있습니다.
설치 후 ADB 경로를 시스템 환경 변수 PATH에 추가해야 합니다.

#### 5) FFmpeg 설치
[ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드 후 압축 해제합니다.
`ffmpeg.exe`가 있는 `bin` 폴더를 시스템 환경 변수 PATH에 추가합니다.

---

## 5. 설치 방법

### 1. 저장소 복제
```bash
git clone <저장소_URL>
cd ATRA
```

### 2. Python 패키지 설치
```bash
pip install PyQt6 appium-python-client selenium
```

> requirements.txt가 없는 경우 위 명령어로 직접 설치합니다.

### 3. Android 기기 연결 확인
```bash
adb devices
```
기기가 정상 연결되면 다음과 같이 출력됩니다:
```
List of devices attached
RFXXXXXXXX    device
```
> ⚠️ 기기에서 **USB 디버깅**을 활성화해야 합니다.
> 설정 → 개발자 옵션 → USB 디버깅 ON

---

## 6. 실행 방법

```bash
python main.py
```

실행하면 ATRA 창이 열립니다.

### 화면 설명

#### 모드 선택 화면
- **테스트 실행**: 연결된 Android 기기에서 테스트를 바로 시작합니다.
- **리포트만 생성**: 이전에 저장된 로그 폴더를 선택해 리포트만 새로 만듭니다.

#### 기기 선택 화면
- ADB로 연결된 기기 목록이 자동으로 표시됩니다.
- 각 기기의 Android 버전을 선택하고 확인을 누릅니다.

#### 테스트 진행 화면
- 기기별 · TC별 진행 상황이 실시간으로 표시됩니다.
- 테스트가 모두 끝나면 자동으로 다음 화면으로 넘어갑니다.

#### 실패 검토 화면
- 실패한 테스트 케이스 목록이 표시됩니다.
- 스크린샷과 로그를 보면서 각 실패를 "Pass 처리" 또는 "Fail 유지"로 검토합니다.

#### PLM 정보 입력 화면
- 해결되지 않은 이슈가 있을 때 PLM 이슈 번호와 코멘트를 입력합니다.

#### 이메일 폼 화면
- 최종 HTML 리포트가 생성된 후, 이메일로 전송할 수 있는 폼이 표시됩니다.

---

## 7. 프로젝트 구조

```
ATRA/
├── main.py                     # 프로그램 시작점
│
├── api/
│   └── actions.py              # TC 파일에서 공통으로 사용하는 함수 모음
│                               # (find, click, scroll, saveLog 등)
│
├── config/
│   └── common_variable.py      # 전역 설정값 (로그 저장 경로, OS 버전 코드 등)
│
├── core/
│   ├── webdriver.py            # Appium 드라이버 연결 관리
│   ├── appium_manager.py       # Appium 서버를 자동으로 켜고 끄는 코드
│   └── test_runner.py          # TC를 순서대로 실행하고 결과를 기록하는 엔진
│
├── ui/
│   ├── app_window.py           # 메인 창 — 6개 화면을 순서대로 전환
│   ├── theme.py                # 다크 테마 스타일
│   └── pages/                  # 각 화면(페이지) 코드
│       ├── mode_selector.py    # 모드 선택 화면
│       ├── device_selector.py  # 기기 선택 화면
│       ├── test_progress.py    # 테스트 진행 화면
│       ├── fail_reviewer.py    # 실패 검토 화면
│       ├── plm_info.py         # PLM 정보 입력 화면
│       └── email_form.py       # 이메일 폼 화면
│
├── report/
│   ├── report_controller.py    # 리포트 생성 전체 과정 조율
│   ├── log_analyzer.py         # log.txt 파일을 파싱해 결과 추출
│   ├── tc_parser.py            # TC 파일에서 메타데이터 읽기
│   └── html_builder.py         # HTML 리포트 파일 생성
│
├── email_feature/
│   ├── email_controller.py     # 이메일 전송 제어
│   ├── process_report.py       # HTML → 이메일 폼 변환
│   └── template_generator.py  # 이메일 HTML 템플릿 생성
│
└── testcase/
    ├── build_verification_test_0010.py   # BVT 테스트 케이스 예시
    └── build_verification_test_0020.py
```

---

## 8. 테스트 케이스 작성법

테스트 케이스(TC)는 `testcase/` 폴더에 `.py` 파일로 작성합니다.

### 기본 구조

```python
# testcase/my_test_0010.py

from main import find, saveLog

def run(wd):
    # 1. 확인하고 싶은 화면 요소를 find()로 찾습니다
    if not find("확인하려는_요소"):
        saveLog("FAIL -> 요소를 찾지 못했습니다")  # 실패 시 로그 저장 후 TC 종료

    # 2. 버튼을 클릭하려면 click=True 추가
    find("다음", click=True)

    # 3. 모두 통과하면 함수를 종료합니다 (return None = Pass)
```

### 주요 함수 설명

| 함수 | 설명 | 예시 |
|------|------|------|
| `find(요소)` | 화면에 요소가 있는지 확인 | `find("확인 버튼")` |
| `find(요소, click=True)` | 요소를 찾아서 클릭 | `find("다음", click=True)` |
| `saveLog("메시지")` | 실패 로그 저장 후 TC 즉시 종료 | `saveLog("FAIL -> 버튼 없음")` |
| `scrollDown()` | 화면을 아래로 스크롤 | `scrollDown()` |
| `scrollUp()` | 화면을 위로 스크롤 | `scrollUp()` |
| `send_text(요소, "텍스트")` | 텍스트 입력 필드에 값 입력 | `send_text("검색창", "SmartThings")` |

### 요소 지정 방법

`find()` 함수에 전달하는 요소는 다음 형태 중 하나로 지정합니다:

```python
# Accessibility ID (텍스트 그대로)
find("Map view")

# Resource ID (android:id/)
find("android:id/aerr_close")

# XPath
find("//android.widget.TextView[@text='설정']")

# UiAutomator (복잡한 조건 검색)
find('new UiSelector().text("확인")')
```

### 파일 이름 규칙

- 반드시 `.py` 확장자
- `__init__.py`처럼 `__`로 시작하는 파일은 TC로 인식하지 않음
- 알파벳 순서대로 실행되므로 앞에 번호를 붙이는 것을 권장

---

## 9. 설정 안내

### 로그 저장 경로 변경

기본적으로 로그는 NAS 경로에 저장됩니다. 로컬 PC에 저장하려면 환경 변수를 설정하세요:

**Windows:**
```
시스템 속성 → 환경 변수 → 새로 만들기
변수 이름: ATRA_LOG_BASE
변수 값:   C:\Users\사용자명\Desktop\ATRA_LOG
```

또는 CMD에서 임시 설정:
```cmd
set ATRA_LOG_BASE=C:\Users\사용자명\Desktop\ATRA_LOG
python main.py
```

### Android OS 버전 코드 매핑

`config/common_variable.py` 파일의 `os_version_dic`에서 확인할 수 있습니다:

| Android 버전 | 코드명 |
|-------------|--------|
| 11 | ROS |
| 12 | SOS |
| 13 | TOS |
| 14 | UOS |
| 15 | VOS |
| 16 | BOS |
| 17 | COS |

---

## 10. 자주 묻는 질문 (FAQ)

**Q. `adb devices`를 실행했는데 기기가 안 보여요.**

A. 다음을 확인하세요:
1. USB 케이블이 데이터 전송을 지원하는지 확인 (충전 전용 케이블은 불가)
2. 기기에서 USB 디버깅이 활성화되어 있는지 확인
3. 기기 화면에 "USB 디버깅을 허용하시겠습니까?" 팝업이 표시되면 "허용"을 누르세요

---

**Q. `appium --version` 명령어가 동작하지 않아요.**

A. Node.js 설치 후 터미널을 새로 열거나, 다음 명령어로 다시 설치해 보세요:
```bash
npm install -g appium
```

---

**Q. 테스트 실행 중 "Appium 서버가 기동되지 않았습니다" 오류가 나요.**

A. 포트(4723)가 이미 사용 중일 수 있습니다. 다음 명령어로 확인 후 기존 프로세스를 종료하세요:
```bash
# Windows
netstat -ano | findstr 4723
taskkill /PID <PID번호> /F
```

---

**Q. 로그가 NAS에 저장되지 않아요.**

A. 회사 네트워크에 연결되어 있는지 확인하세요. 로컬 저장을 원하면 [설정 안내 → 로그 저장 경로 변경](#로그-저장-경로-변경)을 참고하세요.

---

**Q. TC 파일을 추가했는데 실행이 안 돼요.**

A. 다음을 확인하세요:
1. 파일이 `testcase/` 폴더 안에 있는지
2. 파일명이 `__`로 시작하지 않는지
3. 파일 안에 `def run(wd):` 함수가 있는지

---

## 라이선스

사내 내부 도구입니다. 외부 배포 및 사용을 금지합니다.
