# api_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from youtube_api_handler import get_live_stream_details, get_live_video_id_by_channel

app = Flask(__name__)
CORS(app)

# 🔹 루트 접속 확인용
@app.route('/')
def root():
    return jsonify({"status": "ok", "message": "YouTube API 서버 정상 동작 중"})

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

@app.route('/get_live_video_id', methods=['POST'])
def get_live_video_id_api():
    data = request.get_json()
    channel_id = data.get('channelId')
    if not channel_id:
        return jsonify({"error": "channelId를 보내주세요."}), 400

    video_id = get_live_video_id_by_channel(channel_id)
    if not video_id:
        return jsonify({"error": "라이브 중인 영상이 없습니다."}), 400

    return jsonify({"video_id": video_id}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
