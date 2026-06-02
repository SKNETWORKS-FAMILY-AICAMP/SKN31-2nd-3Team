# 🏨 Hotel Overbooking Manager

> 머신러닝 기반 호텔 예약 취소 예측 및 오버부킹 관리 대시보드

<br>

<p align="center">
  <img src="./assets/profile.png" width="700"/>
</p>

<br>

| 이름 | 역할 | 담당 업무 |
|:----:|:----:|-----------|
| 박동관 | 팀장 👑 | 데이터 전처리 · 오버부킹 추천 페이지 · 데이터 조사 |
| 박종현 | 팀원 | 모델 학습 · 현황판 페이지 · 데이터 조사 |
| 오형호 | 팀원 | 모델 학습 · 알림/액션 페이지 · 데이터 조사 |
| 이재일 | 팀원 | 데이터 전처리 · 예약 리스트 페이지 · 데이터 조사 |
| 고현아 | 팀원 | 데이터 전처리 · 알림/액션 페이지 · 데이터 조사 |

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-Pipeline-F7931E?logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-Classifier-AA0000?logoColor=white)
![Random Forest](https://img.shields.io/badge/Random_Forest-Classifier-228B22?logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data%20Processing-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Visualization-3F4F75?logo=plotly&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google%20Colab-Training-F9AB00?logo=googlecolab&logoColor=white)

<br>

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [WBS](#wbs)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [시스템 아키텍처](#-시스템-아키텍처)
- [파일 구조](#-파일-구조)
- [설치 및 실행](#-설치-및-실행)
- [데이터 명세](#-데이터-명세)
- [요구사항 명세](#-요구사항-명세)
- [미구현 항목 및 개선 계획](#-미구현-항목-및-개선-계획)

<br>

## 🔍 프로젝트 소개

**・서론 및 개요**

호텔을 관리하는 매니져 입장에서,  최고의 경영상태는 
「모든 객실이, 항상 100% 만실일때」의 모습일 것입니다. 

<img width="300" height="190" alt="image" src="https://github.com/user-attachments/assets/31efe310-e15e-464a-b97d-950aeda5bf4d" />


본 프로젝트는, 약 3년간 조사한 11만 9천건의 호텔예약 dataset으로부터,

가장 예약취소 확률이 높은 고객들을 사전 예측해 연락하도록 알람을 띄워, 

바로 대체자를 찾아 공실을 최소화 하도록 프로그램 되었습니다. 

---------------------------------------
**ㆍ비즈니스적 가치** 

미리 취소가능성이 높은 고객들을 예측하고 선별해, 

예정대로 투숙할지 재확인 연락을 제때 보낼수 있다면, 

<br>


예약취소가 되더라도, 아직 예약대기자가 있을때 대체고객을 즉시 배정할수 있으므로

공실발생을 막고 매출향상으로 이어지게 할수있습니다.

 ---------------------------------------
**・프로그램 개발목적**
: 호텔의 비즈니스 매니저들이 실시간으로 최신 예약상황을 모니터링 해,
  예약 취소율과 공실률을 통제/관리할수 있는 
  실제 사용가능한 프로그램의 제공.

 ---------------------------------------
 
**ㆍ사용 Data**

 약 3년간의 호텔 예약실적 11만 9천건 (포르투갈, Lisbon)
 
     ⇒ 숙박 기간,  고객의 과거 예약취소 이력, 보증금 납입여부, 특별 요구조건 유무, 주차공간의 요구 등



## 📆WBS

| 작업 | 담당/내용 | 5/22~25 | 5/26~27 | 5/28~29 | 5/30~31 | 6/1~6/3 |
|---|---|:--:|:--:|:--:|:--:|:--:|
| 주제 선정 & 배경 조사 | 주제 확정, 자료 리서치 | ▓ | | | | |
| 데이터 전처리 | 결측치·파생변수 처리 | | ▓ | | | |
| 머신러닝 / 모델 선정 | 모델 학습·비교·선정 | | ▓ | ▓ | | |
| 프론트 구축 | Streamlit 화면 개발 | | | | ▓ | |
| 산출물 | 산출물 작성 | | | | | ▓ |

<br>

## ✨ 주요 기능

| 모듈 | 기능 요약 |
|------|-----------|
| 📊 **현황판** | 실시간 KPI(투숙 현황, 점유율, 체크인/아웃 예정, 예측 취소) 및 오늘 체크인 고객 위험도 테이블 |
| 📋 **예약 리스트** | 상태 필터(전체/In-House/Expected/위험만), 고객명 검색, 취소확률 배지 및 바 차트 |
| 📈 **오버부킹 추천** | 날짜별 추천 오버부킹 수 계산, 향후 7일 예측 차트, 취소 예측 중요 변수 TOP 5 |
| 🔔 **알림 / 액션** | 고위험 고객 카드 목록, 안내 발송 버튼, 조치 완료 체크 관리 |

<br>

## 🛠 기술 스택

### Frontend / UI

| 기술 | 버전 | 사용 목적 |
|------|------|-----------|
| **Streamlit** | 1.x | 웹 대시보드 UI 프레임워크. 사이드바 네비게이션, 멀티페이지 라우팅, 위젯(date_input, selectbox, checkbox, metric 등) 전반에 사용 |
| **Plotly Express** | latest | 오버부킹 추천 페이지의 향후 7일 막대 차트 및 Feature Importance 파이 차트 렌더링 |
| **pandas Styler** | - | 예약 리스트 테이블의 행 배경색, 배지 스타일, 취소확률 바 차트 등 조건부 서식 적용 |

### Data Processing

| 기술 | 버전 | 사용 목적 |
|------|------|-----------|
| **pandas** | latest | CSV 로드, 파생 컬럼 생성(`checkout_date`, `status`, `arrival_date_month_num`), 필터링·정렬·집계 전반 |
| **NumPy** | latest | 수치 연산 및 모델 학습 시 배열 처리 |

### Machine Learning

| 기술 | 버전 | 사용 목적 |
|------|------|-----------|
| **scikit-learn Pipeline** | latest | 전처리기(`ColumnTransformer`)와 분류기를 하나의 `Pipeline`으로 묶어 학습·추론 일관성 보장 |
| **ColumnTransformer** | - | 수치형 컬럼(중앙값 대치 → `StandardScaler`)과 범주형 컬럼(최빈값 대치 → `OneHotEncoder`) 병렬 전처리 |
| **RandomForestClassifier** | latest | 최종 선택 분류 모델. 5개 후보 모델(Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost) 비교 후 AUC 기준 최고 성능으로 채택 |
| **XGBoostClassifier** | latest | 5개 후보 모델 중 하나로 비교 실험에 사용. AUC 기준 Random Forest에 이어 2위 성능을 기록했으나 최종 모델에서 제외 |
| **GridSearchCV** | - | XGBoost 하이퍼파라미터 튜닝 (`n_estimators`, `max_depth`, `learning_rate`). `scoring='roc_auc'`, `cv=3` |
| **joblib** | latest | 학습 완료 Pipeline을 `best_model.pkl`로 직렬화(저장) 및 역직렬화(로드) |

**모델 평가 지표**

| 지표 | 설명 |
|------|------|
| Accuracy | 전체 예측 정확도 |
| Precision | 취소 예측 정밀도 (False Positive 최소화) |
| Recall | 실제 취소 탐지율 (False Negative 최소화) |
| **AUC (ROC)** | 최종 모델 선택 기준 지표 |

**피처 엔지니어링** (학습 시 생성한 주요 파생 피처)

```python
room_assignment_changed  # 예약 객실 ≠ 배정 객실 여부 (0/1)
total_stay_nights        # 주말 박수 + 주중 박수
total_people             # 성인 + 어린이 + 유아 합산 인원
is_adr_0                 # 객실 단가 0원 여부 (프로모션 등)
Agent_check              # 에이전트 예약 여부 (0/1)
foreigner                # 비포르투갈인 여부 (0/1)
arrival_weekday          # 체크인 요일
```

### Development Environment

| 기술 | 사용 목적 |
|------|-----------|
| **Google Colab** | 모델 학습 및 전처리 노트북 실행 환경 (`Preprocessing_hotel_dataset.ipynb`) |
| **Jupyter Notebook** | 데이터 탐색, 피처 엔지니어링, 모델 비교 실험 |
| **Google Drive** | 학습 데이터 및 모델 파일(`best_model.pkl`) 저장소 |

<br>

## 🏗 시스템 아키텍처

```
demo_data.csv
      │
      ▼
 utils.py ── load_data() ── @st.cache_data
      │         │
      │    arrival_date, checkout_date, status 파생 컬럼 생성
      │
      ├──► main_board.py        (📊 현황판)
      ├──► reservation_list.py  (📋 예약 리스트)
      ├──► overbooking_recommend.py (📈 오버부킹 추천)
      └──► alert_action.py      (🔔 알림 / 액션)
                │
                ▼
         best_model.pkl ── predict_proba() ── 취소확률 0~100%
```

**데이터 흐름**

1. `utils.py`의 `load_data()`가 CSV를 로드하고 `arrival_date`, `checkout_date`, `status` 파생 컬럼을 생성합니다.
2. 각 페이지 모듈은 캐시된 결과의 `.copy()` 복사본을 사용해 원본 오염을 방지합니다.
3. `best_model.pkl`로 `Expected` 상태 행의 취소확률을 실시간 예측합니다.
4. 예측 결과를 바탕으로 KPI 계산, 위험 분류, 오버부킹 추천을 수행합니다.

<br>

## 📁 파일 구조

```
📦 SKN31-2nd-3Team
 ┣ 📂 산출물                                # 데이터 전 처리 결과서, 모델 학습 결과서
 ┣ 📂 assets                                
 ┃  └ 📄 profile.png                        # README 프로필 이미지
 ┣ 📂 Dataset
 ┃  └ 📄 demo_data.csv                      # 호텔 예약 데이터셋
 ┃  └ 📄 hotel_bookings.csv                 # 학습용 데이터셋
 ┣ 📂 model&preprocessing
 ┃  └ 📄 best_model.zip                     # 학습 완료 ML 모델 zip 파일
 ┃  └ 📄 best_model.pkl                     # 학습 완료 ML 모델 (sklearn Pipeline)
 ┃  └ 📄 Preprocessing_hotel_dataset.ipynb  # 프로세스 실행파일
 ┣ 📂 utils
 ┃  └ 📄 __init__.py                        # 해당폴더 패키지로 인식
 ┃  └ 📄 utils.py                           # 공통 유틸 – CSV 로드, status 파생, DEMO_TODAY
 ┣ 📂 web_pages
 ┃  └ 📄 __init__.py                        # 해당폴더 패키지로 인식  
 ┃  └ 📄 main_board.py                      # 현황판 모듈
 ┃  └ 📄 reservation_list.py                # 예약 리스트 모듈
 ┃  └ 📄 overbooking_recommend.py           # 오버부킹 추천 모듈
 ┃  └ 📄 alert_action.py                    # 알림 / 액션 모듈
 ┣ 📄 app.py                                # 진입점 – 사이드바 네비게이션 및 페이지 라우팅
 ┗ 📄 requirements.txt                      # 파이썬 라이브러리(패키지) 목록          
```

<br>

## 🚀 설치 및 실행

### 요구 사항

- Python 3.9 이상
- 아래 패키지 설치 필요

```bash
pip install streamlit pandas scikit-learn joblib plotly
```

### 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속 후 좌측 사이드바에서 메뉴를 선택하세요.

<br>

## 📊 데이터 명세

### 입력 데이터 (`demo_data.csv`)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `customer_name` | string | 고객 식별자 (모델 피처 제외) |
| `arrival_date` | datetime | 체크인 예정일 |
| `total_stay_nights` | int | 총 투숙 박수 |
| `is_canceled` | int (0/1) | 실제 취소 여부 (모델 학습 레이블) |
| `lead_time` | int | 예약일~체크인 간격(일). 200일 초과 시 위험 태그 표시 |
| `previous_cancellations` | int | 과거 취소 횟수. 1 이상 시 위험 태그 표시 |
| `total_of_special_requests` | int | 특별 요청 수. 0이면 위험 태그 표시 |
| `adults` | int | 성인 투숙 인원 수 |
| `meal` | string | 식사 유형 코드 (`BB` / `HB` / `FB` / `SC` / `Undefined`) |
| `market_segment` | string | 예약 채널 (Online TA, Direct 등) |

### 파생 컬럼 (`utils.py` 자동 생성)

| 파생 컬럼 | 생성 기준 | 설명 |
|-----------|-----------|------|
| `arrival_date_month_num` | `arrival_date.dt.month` | 모델 피처용 월 숫자 |
| `checkout_date` | `arrival_date + total_stay_nights` | 퇴실 예정일 |
| `status` | arrival / checkout / `DEMO_TODAY` / `is_canceled` | `Expected` / `In-House` / `Checked-Out` / `Canceled` |

### 예약 상태(`status`) 분류 기준

```
DEMO_TODAY = 2017-08-14 (utils.py 기준일)

In-House   : arrival_date < TODAY  AND  checkout_date > TODAY  AND  is_canceled == 0
Checked-Out: checkout_date <= TODAY                            AND  is_canceled == 0
Canceled   : arrival_date < TODAY                              AND  is_canceled == 1
Expected   : 위 3가지 조건에 해당하지 않는 나머지 모든 예약
```

<br>

## 📝 요구사항 명세

### 기능 요구사항

#### 공통 (FR-COM)

| ID | 설명 | 우선순위 |
|----|------|----------|
| FR-COM-001 | 사이드바에 4개 메뉴를 라디오 버튼으로 제공 | 필수 |
| FR-COM-002 | 선택된 메뉴에 따라 해당 모듈의 `run()` 함수 호출 | 필수 |
| FR-COM-003 | ML 모델은 `@st.cache_resource`, 데이터는 `@st.cache_data`로 캐싱 | 필수 |
| FR-COM-004 | 파일 미존재 등 예외 발생 시 `st.error()` 출력 후 `st.stop()` | 필수 |

#### 현황판 (FR-MB)

| ID | 설명 | 우선순위 |
|----|------|----------|
| FR-MB-001 | 현재 투숙 중(In-House) 건수 및 점유율을 KPI 카드로 표시 | 필수 |
| FR-MB-002 | 오늘 체크아웃 예정 건수, 가용 객실 수 표시 | 필수 |
| FR-MB-003 | 오늘 체크인 예정 / 실제 취소 / 모델 예측 취소 기댓값 표시 | 필수 |
| FR-MB-004 | 객실 점유율을 `st.progress()` 바로 시각화 | 필수 |
| FR-MB-005 | 오늘 체크인 예정 고객을 취소확률 내림차순 스타일드 테이블로 출력 | 필수 |
| FR-MB-006 | 취소확률 70%↑ 빨강 / 40~69% 노랑 / 40%↓ 초록 배지 표시 | 필수 |

#### 예약 리스트 (FR-RL)

| ID | 설명 | 우선순위 |
|----|------|----------|
| FR-RL-001 | `Expected` 상태에만 취소확률 예측, 그 외는 `—` 표시 | 필수 |
| FR-RL-002 | 전체 / 투숙중 / 예약확정 / 취소위험(70%↑) / 취소완료 5가지 탭 필터 | 필수 |
| FR-RL-003 | 고객명 부분 검색 (대소문자 무시) | 필수 |
| FR-RL-004 | 취소확률 70%↑ 고객 수를 상단 경고 배너로 표시 | 필수 |
| FR-RL-005 | 행 배경색 + 배지 스타일 + 취소확률 바 차트 스타일드 테이블 | 필수 |
| FR-RL-006 | Expected/위험만 탭은 취소확률 내림차순, 전체/In-House는 체크인 날짜 오름차순 정렬 | 권장 |
| FR-RL-007 | 예약 추가 / 예약 수정 버튼 UI 제공 (현재 목업) | 선택 |

#### 오버부킹 추천 (FR-OB)

| ID | 설명 | 우선순위 |
|----|------|----------|
| FR-OB-001 | 날짜 선택기로 분석 기준일 지정 | 필수 |
| FR-OB-002 | 예약 건수 / 예상 취소 / 예상 체크인 / 점유율 / 추천 오버부킹 수 KPI 표시 | 필수 |
| FR-OB-003 | 예측 취소 기댓값 반올림 → 추천 오버부킹 수로 제시 | 필수 |
| FR-OB-004 | 예상 점유율을 Progress 바로 시각화 | 필수 |
| FR-OB-005 | 오늘부터 7일간 일별 추천 오버부킹 수를 Plotly 막대 차트로 표시 | 필수 |
| FR-OB-006 | 취소 예측 중요 변수 TOP 5를 파이 차트 및 테이블로 표시 | 권장 |
| FR-OB-007 | 해당 날짜 예약 없을 시 `st.warning()` 안내 | 필수 |

#### 알림 / 액션 (FR-AA)

| ID | 설명 | 우선순위 |
|----|------|----------|
| FR-AA-001 | 날짜 선택기로 분석 기준일 지정 | 필수 |
| FR-AA-002 | 총 체크인 예정 / 즉시 연락 필요(70%↑) / 모니터링 필요(50~69%) KPI 3열 표시 | 필수 |
| FR-AA-003 | 즉시 연락 필요(빨강) / 모니터링 필요(노랑) 고객을 2열 카드로 표시 | 필수 |
| FR-AA-004 | 장기 예약(200일↑) / 과거 취소 이력 / 특별 요청 없음 피처 기반 원인 태그 표시 | 필수 |
| FR-AA-005 | ✉️ 안내 발송 버튼 클릭 시 `st.toast()`로 발송 완료 알림 | 필수 |
| FR-AA-006 | 조치 완료 체크 시 해당 카드를 목록 하단으로 이동 및 반투명 처리 | 필수 |
| FR-AA-007 | 취소 확률 높은 순 / 체크인 임박 순 정렬 selectbox 제공 | 권장 |
| FR-AA-008 | 조치 완료 목록을 `st.session_state`로 관리 (페이지 재실행 시 상태 유지) | 필수 |

### 비기능 요구사항

| ID | 구분 | 설명 | 우선순위 |
|----|------|------|----------|
| NFR-001 | 성능 | ML 모델 및 데이터는 캐시를 통해 최초 1회만 로드 | 필수 |
| NFR-002 | 데이터 무결성 | 각 모듈은 `load_data()`의 `.copy()` 복사본을 사용 | 필수 |
| NFR-003 | UI 반응성 | 체크박스 상태 변경 시 `st.rerun()`으로 즉각 화면 갱신 | 필수 |
| NFR-004 | 유지보수성 | 모듈별 `run()` 함수로 진입점 통일 | 권장 |
| NFR-005 | 레이아웃 | `layout='wide'`로 와이드 레이아웃 기본 사용 | 권장 |
| NFR-006 | 예외 처리 | `FileNotFoundError` 및 일반 예외 발생 시 사용자 친화적 오류 메시지 출력 | 필수 |
| NFR-007 | 결측치 처리 | 날짜 파싱 실패 등 결측치는 `fillna(0)`으로 처리하여 런타임 오류 방지 | 필수 |

<br>

## 🔧 미구현 항목 및 개선 계획

| 항목 | 현재 상태 | 개선 방향 |
|------|-----------|-----------|
| 오버부킹 추천 페이지 | `app.py`에서 🚧 준비 중으로 임시 처리 | `overbooking_recommend.py` 연동 활성화 |
| 알림/액션 페이지 | `app.py`에서 🚧 준비 중으로 임시 처리 | `alert_action.py` 연동 활성화 |
| 예약 추가/수정 | 버튼 UI만 존재, 이벤트 미연결 (목업) | 예약 CRUD 기능 구현 |
| 실제 알림 발송 | `st.toast()`로 발송 시뮬레이션만 수행 | 카카오 알림톡 또는 SMS API 연동 |
| `TOTAL_ROOMS` 설정 | 각 모듈에 하드코딩 (100 또는 800) | 설정 파일 또는 UI에서 동적 설정으로 통합 |
| 실시간 데이터 | 정적 CSV 기반 (`DEMO_TODAY` 고정) | DB 연동 또는 실시간 PMS 연계 |

<br>

---

> SKN31 2차 프로젝트 3팀
