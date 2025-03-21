import pandas as pd
import json
from io import StringIO
import os

def normalize_column_names(df):
    """열 이름을 정규화"""
    column_mapping = {
        '주제': 'topic',
        '토픽': 'topic',
        '제목': 'topic',
        '챕터': 'topic',
        '단원': 'topic',
        '교과목명': 'topic',
        '구분': 'topic',
        '설명': 'description',
        '내용': 'description',
        '상세내용': 'description',
        '세부내용': 'description',
        '시간': 'duration',
        '소요시간': 'duration'
    }
    
    # 열 이름 전처리
    print("\n=== 열 이름 정규화 시작 ===")
    print("원본 열 이름:", list(df.columns))
    
    # 열 이름 전처리 (공백 제거 및 소문자 변환)
    df.columns = df.columns.str.strip().str.lower()
    print("공백 제거 및 소문자 변환 후 열 이름:", list(df.columns))
    
    # 매핑 시도
    renamed_columns = {}
    for orig_col in df.columns:
        # 열 이름에서 공백과 특수문자 제거
        clean_col = ''.join(e for e in orig_col if e.isalnum())
        print(f"처리 중인 열: {orig_col} -> 정제된 이름: {clean_col}")
        
        # 정확한 매칭 시도
        if orig_col in column_mapping:
            renamed_columns[orig_col] = column_mapping[orig_col]
            print(f"정확한 매칭 성공: {orig_col} -> {column_mapping[orig_col]}")
            continue
            
        # 정제된 이름으로 매칭 시도
        if clean_col in column_mapping:
            renamed_columns[orig_col] = column_mapping[clean_col]
            print(f"정제된 이름으로 매칭 성공: {orig_col} -> {column_mapping[clean_col]}")
            continue
            
        # 부분 문자열 매칭 시도
        matched = False
        for key in column_mapping:
            if key in orig_col or key in clean_col:
                renamed_columns[orig_col] = column_mapping[key]
                print(f"부분 매칭 성공: {orig_col} -> {column_mapping[key]} (키워드: {key})")
                matched = True
                break
        
        # 특수 케이스 처리
        if not matched:
            if '교과' in orig_col or '과목' in orig_col:
                renamed_columns[orig_col] = 'topic'
                print(f"특수 케이스 매칭: {orig_col} -> topic (교과/과목)")
            elif '세부' in orig_col or '내용' in orig_col:
                renamed_columns[orig_col] = 'description'
                print(f"특수 케이스 매칭: {orig_col} -> description (세부/내용)")
    
    # 열 이름 변경 적용
    if renamed_columns:
        df = df.rename(columns=renamed_columns)
        print("\n변경된 열 이름:", list(df.columns))
    else:
        print("\n매칭된 열 없음")
    
    print("=== 열 이름 정규화 완료 ===\n")
    return df

def validate_columns(df):
    """필수 열이 있는지 확인"""
    required_columns = ['topic', 'description']
    
    # 현재 열 출력 (디버깅용)
    print(f"검증 전 열 이름: {list(df.columns)}")
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        # 한글 열 이름으로 다시 시도
        df = normalize_column_names(df)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            available_columns = ", ".join(df.columns)
            raise ValueError(
                f'필수 열이 없습니다. 다음 열이 필요합니다: \n'
                f'- topic (또는 주제, 토픽, 제목, 챕터, 단원)\n'
                f'- description (또는 설명, 내용, 상세내용, 세부내용)\n'
                f'현재 사용 가능한 열: {available_columns}'
            )
    
    return df

def process_excel(file):
    """엑셀 파일 처리"""
    try:
        print("\n=== 엑셀 파일 처리 시작 ===")
        print("파일 읽기 시작...")
        
        # 엑셀 파일의 모든 시트를 읽어옵니다
        df = pd.read_excel(file, header=None)
        print(f"파일 읽기 완료. 크기: {df.shape}")
        
        # 데이터 미리보기
        print("\n원본 데이터 미리보기:")
        print(df.head())
        
        # 실제 헤더 행을 찾습니다
        for idx, row in df.iterrows():
            # 행의 값들을 문자열로 변환하여 검사
            row_values = row.astype(str)
            if any('교과목명' in val for val in row_values) or any('세부내용' in val for val in row_values):
                # 해당 행을 새로운 헤더로 설정
                df.columns = df.iloc[idx]
                # 헤더 행 이후의 데이터만 선택
                df = df.iloc[idx+1:].reset_index(drop=True)
                break
        
        print("\n처리된 데이터 미리보기:")
        print(df.head())
        print("\n현재 열 이름:", list(df.columns))
        
        # 열 이름 정리 (공백 제거)
        df.columns = df.columns.str.strip()
        
        # 필수 열 확인
        if '교과목명' not in df.columns:
            # 열 이름 매핑 시도
            df = normalize_column_names(df)
            
            if '교과목명' not in df.columns and 'topic' not in df.columns:
                raise ValueError(f"'교과목명' 열을 찾을 수 없습니다. 현재 열: {list(df.columns)}")
        
        if '세부내용' not in df.columns:
            if 'description' not in df.columns:
                raise ValueError(f"'세부내용' 열을 찾을 수 없습니다. 현재 열: {list(df.columns)}")
        
        # 결과 데이터프레임 생성
        topic_col = '교과목명' if '교과목명' in df.columns else 'topic'
        desc_col = '세부내용' if '세부내용' in df.columns else 'description'
        
        result_df = pd.DataFrame({
            'topic': df[topic_col],
            'description': df[desc_col]
        })
        
        # 데이터 전처리
        result_df = result_df.fillna('')
        
        # 불필요한 공백 제거
        result_df['topic'] = result_df['topic'].str.strip()
        result_df['description'] = result_df['description'].str.strip()
        
        # 빈 행 제거
        result_df = result_df[
            (result_df['topic'].str.len() > 0) | 
            (result_df['description'].str.len() > 0)
        ].reset_index(drop=True)
        
        # 결과 데이터 확인
        print("\n최종 처리된 데이터:")
        for idx, row in result_df.head().iterrows():
            print(f"행 {idx}:")
            print(f"  - topic: {row['topic']}")
            print(f"  - description: {row['description']}")
        print("=== 엑셀 파일 처리 완료 ===\n")
        
        return result_df.to_dict('records')
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n=== 엑셀 처리 오류 발생 ===")
        print(f"오류 메시지: {error_msg}")
        print(f"오류 타입: {type(e).__name__}")
        print(f"현재 열 이름: {list(df.columns) if 'df' in locals() else '알 수 없음'}")
        print("=== 오류 정보 끝 ===\n")
        raise ValueError(f'엑셀 파일 처리 중 오류가 발생했습니다: {error_msg}')

def process_csv(content):
    """CSV 파일 처리"""
    try:
        df = pd.read_csv(StringIO(content))
        df = validate_columns(df)
        df = df.fillna('')
        result_df = df[['topic', 'description']]
        return result_df.to_dict('records')
    except Exception as e:
        raise ValueError(f'CSV 파일 처리 중 오류가 발생했습니다: {str(e)}')

def process_json(file):
    """JSON 파일 처리"""
    try:
        # JSON 파일 읽기
        print("\n=== JSON 파일 처리 시작 ===")
        content = json.load(file)
        
        # JSON 구조 출력
        print("\n현재 JSON 구조:")
        print(json.dumps(content[:1], indent=2, ensure_ascii=False))
        
        if not isinstance(content, list):
            raise ValueError("JSON 파일은 리스트 형식이어야 합니다.")
            
        if not content:
            raise ValueError("JSON 파일이 비어있습니다.")
            
        # 필드 이름 매핑
        field_mappings = {
            'topic': ['topic', '주제', '토픽', '제목', '교과목명', '과목명', '교과', '과정명'],
            'description': ['description', '설명', '내용', '상세내용', '세부내용']
        }
        
        processed_data = []
        for idx, item in enumerate(content):
            if not isinstance(item, dict):
                raise ValueError(f"{idx+1}번째 항목이 객체 형식이 아닙니다.")
            
            # topic 필드 찾기
            topic_value = None
            for key in item.keys():
                if any(field in key.lower() for field in field_mappings['topic']):
                    topic_value = item[key]
                    break
            
            # description 필드 찾기
            desc_value = None
            for key in item.keys():
                if any(field in key.lower() for field in field_mappings['description']):
                    desc_value = item[key]
                    break
            
            if topic_value is None or desc_value is None:
                print(f"\n문제가 있는 항목 {idx+1}:")
                print(json.dumps(item, indent=2, ensure_ascii=False))
                raise ValueError(f"{idx+1}번째 항목에서 필수 필드를 찾을 수 없습니다.")
            
            processed_data.append({
                'topic': str(topic_value).strip(),
                'description': str(desc_value).strip()
            })
        
        print("\n처리된 데이터 예시:")
        for item in processed_data[:2]:
            print(json.dumps(item, indent=2, ensure_ascii=False))
        
        print(f"\n총 {len(processed_data)}개 항목 처리 완료")
        print("=== JSON 파일 처리 완료 ===\n")
        
        return processed_data
        
    except json.JSONDecodeError as e:
        print(f"\nJSON 파싱 오류: {str(e)}")
        raise ValueError("올바른 JSON 형식이 아닙니다.")
    except Exception as e:
        print(f"\nJSON 처리 오류: {str(e)}")
        raise ValueError(f"JSON 파일 처리 중 오류가 발생했습니다: {str(e)}")

def process_curriculum_file(file):
    """커리큘럼 파일 처리 (JSON/CSV/Excel)"""
    try:
        filename = file.filename.lower()
        
        if filename.endswith('.json'):
            return process_json(file)
        elif filename.endswith('.csv'):
            content = file.read().decode('utf-8')
            return process_csv(content)
        elif filename.endswith('.xlsx'):
            return process_excel(file)
        else:
            raise ValueError("지원하지 않는 파일 형식입니다. JSON, CSV, Excel 파일만 지원합니다.")
            
    except Exception as e:
        print(f"\n커리큘럼 처리 오류: {str(e)}")
        raise ValueError(f"커리큘럼 파일 처리 중 오류가 발생했습니다: {str(e)}")

def calculate_curriculum_match(curriculum_data, lecture_keywords):
    """커리큘럼과 강의 내용의 매칭 정도 계산"""
    matches = []
    total_match_score = 0
    
    for item in curriculum_data:
        # 토픽과 설명을 결합하여 매칭
        topic_text = f"{item['topic']} {item['description']}"
        topic_keywords = set(topic_text.lower().split())
        
        # 키워드 매칭 점수 계산
        matching_keywords = topic_keywords.intersection(set(lecture_keywords))
        match_score = len(matching_keywords) / len(topic_keywords) * 100 if topic_keywords else 0
        
        matches.append({
            'topic': item['topic'],
            'match_percentage': round(match_score, 1),
            'matching_keywords': list(matching_keywords)
        })
        
        total_match_score += match_score
    
    average_match = total_match_score / len(curriculum_data) if curriculum_data else 0
    
    return {
        'overall_match': round(average_match, 1),
        'topic_matches': matches
    } 