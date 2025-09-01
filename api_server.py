# api_server.py (내용 복사)

from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_api_handler import get_live_stream_details # 1.2에서 만든 핵심 로직 임포트
import os

app = Flask(__name__)
CORS(app) # 🚨 중요: 모든 도메인からの API 호출을 허용합니다.

@app.route('/get_youtube_time', methods=['POST'])
def get_youtube_time_api():
    """유튜브 링크를 받아 라이브 정보를 JSON으로 반환하는 API 엔드포인트"""
    data = request.get_json() # 웹에서 보낸 JSON 데이터를 받습니다.
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({"error": "유튜브 링크 주소를 'url' 파라미터로 JSON 형식으로 제공해주세요."}), 400

    result = get_live_stream_details(youtube_url)

    if "error" in result:
        return jsonify(result), 400
    else:
        return jsonify(result), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)