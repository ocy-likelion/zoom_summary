import re
import codecs
from io import StringIO, BytesIO
import chardet
import os

def clean_text(text):
    """텍스트 클리닝 함수"""
    if not text:
        return ""
    # 화자 이름과 콜론 제거 (예: "유건곤강사: " 제거)
    text = re.sub(r'[가-힣a-zA-Z]+\s*:', '', text)
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 숫자와 특수문자 제거 (한글, 영문, 기본 문장 부호 유지)
    text = re.sub(r'[^\w\s\.,!?\u3131-\u3163\uac00-\ud7a3]', ' ', text)
    # 중복 공백 제거
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def try_decode(content, encodings):
    """다양한 인코딩으로 디코딩을 시도하는 함수"""
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None

def process_vtt_file(file):
    """VTT 파일을 처리하여 텍스트로 변환"""
    try:
        # 파일 위치를 처음으로 이동
        file.seek(0)
        
        # 파일 전체 내용을 바이트로 읽기
        content = file.read()
        
        # 다양한 인코딩 시도
        encodings = [
            'utf-8-sig',  # BOM이 있는 UTF-8
            'utf-8',      # 일반 UTF-8
            'cp949',      # 한글 Windows
            'euc-kr',     # 한글
            'cp1252',     # Windows-1252
            'windows-1252',
            'ascii',      # ASCII
            'iso-8859-1'  # Latin-1
        ]
        
        # chardet로 인코딩 감지
        result = chardet.detect(content)
        if result['encoding'] and result['confidence'] > 0.8:
            encodings.insert(0, result['encoding'])
        
        # 여러 인코딩 시도
        content_str = try_decode(content, encodings)
        
        # 모든 시도 실패시 UTF-8로 강제 디코딩
        if content_str is None:
            content_str = content.decode('utf-8', errors='ignore')
        
        # VTT 파일 파싱
        lines = content_str.splitlines()
        transcript = []
        is_valid_vtt = False
        current_text = ""
        
        for line in lines:
            line = line.strip()
            
            # WEBVTT 헤더 확인
            if 'WEBVTT' in line:
                is_valid_vtt = True
                continue
            
            # 타임스탬프 라인이나 빈 줄, 숫자만 있는 라인 건너뛰기
            if '-->' in line or not line or line.isdigit():
                if current_text:
                    cleaned = clean_text(current_text)
                    if cleaned:
                        transcript.append(cleaned)
                    current_text = ""
                continue
            
            # 실제 자막 텍스트 수집
            current_text = current_text + " " + line if current_text else line
        
        # 마지막 텍스트 처리
        if current_text:
            cleaned = clean_text(current_text)
            if cleaned:
                transcript.append(cleaned)
        
        # VTT 형식 검증
        if not is_valid_vtt:
            raise ValueError('올바른 VTT 파일 형식이 아닙니다.')
        
        # 결과 검증
        if not transcript:
            raise ValueError('추출된 텍스트가 없습니다.')
        
        # 전체 텍스트 결합
        return ' '.join(transcript)
        
    except Exception as e:
        print(f"Error details: {str(e)}")  # 디버깅을 위한 에러 출력
        raise ValueError(f'VTT 파일 처리 중 오류가 발생했습니다: {str(e)}') 