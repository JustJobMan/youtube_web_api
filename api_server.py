# api_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from youtube_api_handler import get_live_stream_details  # URL 기반 조회만 사용

app = Flask(__name__)
CORS(app)

@app.route('/get_youtube_time', methods=['POST'])
def get_youtube_time_api():
    data = request.get_json()
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({"error": "유튜브 링크를 'url'로 보내주세요."}), 400

    result = get_live_stream_details(youtube_url)
    if "error" in result:
        return jsonify(result), 400

    return jsonify(result), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
