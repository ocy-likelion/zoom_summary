document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const resultsSection = document.querySelector('.results-section');

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const vttFile = document.getElementById('vttFile').files[0];
        const curriculumFile = document.getElementById('curriculumFile').files[0];
        
        if (!vttFile || !curriculumFile) {
            alert('모든 필수 파일을 선택해주세요.');
            return;
        }

        const formData = new FormData();
        formData.append('vtt_file', vttFile);
        formData.append('curriculum_file', curriculumFile);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (response.ok) {
                displayResults(data);
            } else {
                alert(data.error || '파일 처리 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버 통신 중 오류가 발생했습니다.');
        }
    });

    function displayResults(data) {
        resultsSection.style.display = 'block';
        
        // 정합성 점수 표시
        document.getElementById('conformityScore').textContent = 
            `${data.curriculum_match.overall_match}%`;
        
        // 키워드 리스트 표시
        const keywordsList = document.getElementById('keywordsList');
        keywordsList.innerHTML = data.keywords
            .map(kw => `<span class="keyword">${kw}</span>`)
            .join('');
        
        // 커리큘럼 매칭 결과 표시
        const curriculumMatch = document.getElementById('curriculumMatch');
        curriculumMatch.innerHTML = data.curriculum_match.topic_matches
            .map(match => `
                <div class="match-item">
                    <span class="match-topic">${match.topic}</span>
                    <span class="match-percentage">${match.match_percentage}%</span>
                </div>
            `).join('');
        
        // 리스크 매트릭스 차트 생성
        createRiskMatrix(data.risk_matrix);
        
        // 키워드 빈도 차트 생성
        createKeywordFrequencyChart(data.keyword_frequencies);
        
        // 커리큘럼 비교 차트 생성
        createCurriculumComparisonChart(data.curriculum_match.topic_matches);
    }

    function createRiskMatrix(riskData) {
        const data = [{
            type: 'heatmap',
            x: ['낮음', '중간', '높음'],
            y: ['낮음', '중간', '높음'],
            z: [
                [riskData.low_risk.length, riskData.medium_risk.length, riskData.high_risk.length],
                [0, 0, 0],
                [0, 0, 0]
            ],
            colorscale: 'RdYlGn',
            reversescale: true
        }];

        const layout = {
            title: '리스크 매트릭스',
            xaxis: {title: '발생 가능성'},
            yaxis: {title: '영향도'}
        };

        Plotly.newPlot('riskMatrix', data, layout);
    }

    function createKeywordFrequencyChart(frequencies) {
        const data = [{
            type: 'bar',
            x: Object.keys(frequencies),
            y: Object.values(frequencies),
            marker: {
                color: '#4a90e2'
            }
        }];

        const layout = {
            title: '키워드 빈도',
            xaxis: {title: '키워드'},
            yaxis: {title: '빈도'}
        };

        Plotly.newPlot('keywordFrequency', data, layout);
    }

    function createCurriculumComparisonChart(matches) {
        const data = [{
            type: 'bar',
            x: matches.map(m => m.topic),
            y: matches.map(m => m.match_percentage),
            marker: {
                color: matches.map(m => {
                    if (m.match_percentage < 30) return '#ff4d4d';
                    if (m.match_percentage < 70) return '#ffd700';
                    return '#32cd32';
                })
            }
        }];

        const layout = {
            title: '커리큘럼 주제별 매칭률',
            xaxis: {
                title: '주제',
                tickangle: -45
            },
            yaxis: {
                title: '매칭률 (%)',
                range: [0, 100]
            }
        };

        Plotly.newPlot('curriculumComparison', data, layout);
    }

    // 엑셀 변환 폼 이벤트 핸들러
    document.getElementById('excelConverterForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('excelFile');
        
        if (!fileInput.files[0]) {
            alert('파일을 선택해주세요.');
            return;
        }
        
        formData.append('file', fileInput.files[0]);
        
        try {
            const response = await fetch('/convert-excel-to-json', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '변환 중 오류가 발생했습니다.');
            }
            
            // 파일 다운로드 처리
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'curriculum.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // 폼 초기화
            fileInput.value = '';
            alert('변환이 완료되었습니다. JSON 파일이 다운로드됩니다.');
            
        } catch (error) {
            alert(error.message);
        }
    });
}); 