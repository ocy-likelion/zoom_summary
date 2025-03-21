from app import app
from flask import render_template, request, jsonify, send_file
from app.utils.vtt_processor import process_vtt_file
from app.utils.analyzer import analyze_lecture_content
from app.utils.curriculum_processor import process_curriculum_file, calculate_curriculum_match
import os
import tempfile
from werkzeug.utils import secure_filename
from .utils.excel_to_json_converter import convert_excel_to_json
import json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'vtt_file' not in request.files or 'curriculum_file' not in request.files:
        return jsonify({'error': '모든 필수 파일을 업로드해주세요.'}), 400
    
    vtt_file = request.files['vtt_file']
    curriculum_file = request.files['curriculum_file']
    
    if vtt_file.filename == '' or curriculum_file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400

    if not vtt_file.filename.endswith('.vtt'):
        return jsonify({'error': 'VTT 파일만 업로드 가능합니다.'}), 400

    try:
        # 임시 파일로 저장하여 처리
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vtt', mode='wb') as temp_vtt:
            vtt_content = vtt_file.read()
            temp_vtt.write(vtt_content)
            temp_vtt.flush()
            
            # 파일을 다시 열어서 처리
            with open(temp_vtt.name, 'rb') as f:
                transcript_text = process_vtt_file(f)
        
        # 임시 파일 삭제
        os.unlink(temp_vtt.name)
        
        # 텍스트 분석
        lecture_analysis = analyze_lecture_content(transcript_text)
        
        # 커리큘럼 파일 처리
        curriculum_data = process_curriculum_file(curriculum_file)
        
        # 커리큘럼과 강의 내용 매칭
        curriculum_match = calculate_curriculum_match(
            curriculum_data, 
            lecture_analysis['keywords']
        )
        
        # 결과 통합
        result = {
            **lecture_analysis,
            'curriculum_match': curriculum_match,
            'risk_matrix': {
                'high_risk': [],
                'medium_risk': [],
                'low_risk': []
            }
        }
        
        # 리스크 매트릭스 업데이트
        for topic_match in curriculum_match['topic_matches']:
            if topic_match['match_percentage'] < 30:
                result['risk_matrix']['high_risk'].append(topic_match['topic'])
            elif topic_match['match_percentage'] < 70:
                result['risk_matrix']['medium_risk'].append(topic_match['topic'])
            else:
                result['risk_matrix']['low_risk'].append(topic_match['topic'])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    if not data or 'curriculum' not in data:
        return jsonify({'error': '커리큘럼 데이터가 없습니다.'}), 400

    try:
        # 분석 결과 반환
        result = {
            'conformity': 85,  # 예시 값
            'keywords': ['파이썬', '데이터 분석', 'AI'],  # 예시 값
            'missing_topics': ['머신러닝 기초'],  # 예시 값
            'risk_matrix': {
                'high_risk': ['실습 환경 구성'],
                'medium_risk': ['데이터 전처리'],
                'low_risk': ['이론 학습']
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert-excel-to-json', methods=['POST'])
def convert_excel():
    """엑셀 파일을 JSON으로 변환하는 엔드포인트"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '파일이 업로드되지 않았습니다.'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '선택된 파일이 없습니다.'}), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': '엑셀 파일(.xlsx)만 업로드 가능합니다.'}), 400
        
        # 엑셀 파일을 JSON으로 변환
        json_data = convert_excel_to_json(file)
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(json_data, temp_file, ensure_ascii=False, indent=2)
            temp_filename = temp_file.name
        
        # JSON 파일 다운로드
        return send_file(
            temp_filename,
            mimetype='application/json',
            as_attachment=True,
            download_name='curriculum.json'
        )
        
    except Exception as e:
        return jsonify({'error': f'변환 중 오류가 발생했습니다: {str(e)}'}), 500 