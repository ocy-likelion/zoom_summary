import pandas as pd
import json

def convert_excel_to_json(excel_file):
    """
    엑셀 파일을 JSON 형식으로 변환
    """
    try:
        print("\n=== 엑셀 파일 변환 시작 ===")
        
        # 엑셀 파일 읽기 (헤더 없이)
        df = pd.read_excel(excel_file, header=None)
        print(f"파일 읽기 완료. 크기: {df.shape}")
        
        # 모든 행의 데이터 출력하여 구조 확인
        print("\n=== 엑셀 파일 구조 확인 ===")
        print("처음 5개 행의 데이터:")
        for idx, row in df.head().iterrows():
            print(f"\n행 {idx + 1}:")
            for col_idx, value in enumerate(row):
                print(f"  열 {col_idx + 1}: {value}")
        
        # 실제 헤더 행 찾기
        header_row = -1
        header_keywords = ['교과목명', '과목명', '교과', '과정명', '세부내용', '내용', '설명']
        
        for idx, row in df.iterrows():
            row_values = row.astype(str)
            if any(keyword in val for keyword in header_keywords for val in row_values):
                header_row = idx
                print(f"\n헤더 행 발견 (행 번호: {idx + 1}):")
                print(row_values.values)
                break
        
        if header_row == -1:
            print("\n=== 현재 발견된 열 이름들 ===")
            for col_idx in range(df.shape[1]):
                unique_values = df[col_idx].astype(str).unique()
                print(f"\n열 {col_idx + 1} 의 고유 값들:")
                print(unique_values[:5])  # 처음 5개의 고유 값만 출력
            raise ValueError("교과목 관련 열을 찾을 수 없습니다. 엑셀 파일의 구조를 확인해주세요.")
        
        # 헤더 행을 기준으로 데이터프레임 재구성
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # 열 이름 정리
        df.columns = df.columns.str.strip()
        print("\n현재 열 이름들:", list(df.columns))
        
        # 필요한 열 찾기
        topic_keywords = ['교과목명', '과목명', '교과', '과정명']
        desc_keywords = ['세부내용', '내용', '설명']
        
        topic_col = None
        desc_col = None
        
        for col in df.columns:
            if any(keyword in str(col) for keyword in topic_keywords):
                topic_col = col
            elif any(keyword in str(col) for keyword in desc_keywords):
                desc_col = col
        
        if topic_col is None or desc_col is None:
            raise ValueError(f"필요한 열을 찾을 수 없습니다. 현재 열: {list(df.columns)}")
        
        print(f"\n사용할 열:")
        print(f"주제 열: {topic_col}")
        print(f"설명 열: {desc_col}")
        
        # 결과 데이터프레임 생성
        result_df = pd.DataFrame({
            'topic': df[topic_col],
            'description': df[desc_col]
        })
        
        # 데이터 정리
        result_df = result_df.fillna('')
        result_df['topic'] = result_df['topic'].str.strip()
        result_df['description'] = result_df['description'].str.strip()
        
        # 빈 행 제거
        result_df = result_df[
            (result_df['topic'].str.len() > 0) | 
            (result_df['description'].str.len() > 0)
        ].reset_index(drop=True)
        
        # JSON 형식으로 변환
        json_data = result_df.to_dict('records')
        
        print("\n=== 변환된 데이터 미리보기 ===")
        for i, item in enumerate(json_data[:3]):
            print(f"\n항목 {i+1}:")
            print(f"  topic: {item['topic']}")
            print(f"  description: {item['description']}")
        
        print(f"\n총 {len(json_data)}개 항목이 변환되었습니다.")
        print("=== 엑셀 파일 변환 완료 ===\n")
        
        return json_data
        
    except Exception as e:
        print(f"\n=== 변환 중 오류 발생 ===")
        print(f"오류 메시지: {str(e)}")
        print("=== 오류 정보 끝 ===\n")
        raise 