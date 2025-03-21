# 온라인 강의 분석기

Zoom 강의 자막(VTT) 파일을 분석하여 강의 내용을 요약하고 커리큘럼과의 정합성을 분석하는 웹 애플리케이션입니다.

## 주요 기능

1. VTT 파일 분석
   - 강의 내용 텍스트 추출
   - 키워드 추출 및 빈도 분석
   - 문장 구조 분석

2. 커리큘럼 정합성 분석
   - 강의 내용과 커리큘럼 비교
   - 정합성 점수 산출
   - 리스크 매트릭스 시각화

## 설치 방법

1. 저장소 클론
```bash
git clone [repository-url]
cd [repository-name]
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 실행 방법

1. Flask 서버 실행
```bash
python run.py
```

2. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 기술 스택

- Backend: Flask
- Frontend: HTML, CSS, JavaScript
- 데이터 분석: pandas, numpy
- 자연어 처리: NLTK
- 시각화: Plotly

## 라이선스

MIT License # zoom_summary
