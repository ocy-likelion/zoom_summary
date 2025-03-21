import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# NLTK 데이터 다운로드
nltk.download('punkt')
nltk.download('stopwords')

def analyze_lecture_content(text):
    """강의 내용을 분석하여 주요 키워드와 통계 추출"""
    # 텍스트 토큰화
    tokens = word_tokenize(text.lower())
    
    # 불용어 제거
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # 키워드 추출
    keyword_freq = Counter(tokens)
    top_keywords = keyword_freq.most_common(10)
    
    # 문장 길이 통계
    sentences = text.split('.')
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    avg_sentence_length = np.mean(sentence_lengths)
    
    # TF-IDF 분석
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text])
    
    return {
        'keywords': [kw for kw, _ in top_keywords],
        'keyword_frequencies': dict(top_keywords),
        'avg_sentence_length': float(avg_sentence_length),
        'total_words': len(tokens),
        'unique_words': len(set(tokens))
    } 