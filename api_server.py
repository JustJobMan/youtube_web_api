# api_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from youtube_api_handler import get_live_stream_details, get_live_chat_id, get_live_chat_messages
import re

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

@app.route('/get_live_chat', methods=['POST'])
def get_live_chat_api():
    data = request.get_json()
    youtube_url = data.get('url')
    if not youtube_url:
        return jsonify({"error": "유튜브 링크를 'url'로 보내주세요."}), 400

    match = re.search(r'(?:v=|youtu\.be/|live/)([a-zA-Z0-9_-]{11})', youtube_url)
    if not match:
        return jsonify({"error": "유효한 유튜브 링크가 아닙니다."}), 400
    video_id = match.group(1)

    live_chat_id = get_live_chat_id(video_id)
    if not live_chat_id:
        return jsonify({"error": "라이브 채팅을 찾을 수 없습니다. 방송 중인지 확인하세요."}), 400

    page_token = data.get('pageToken')
    messages, next_page_token, polling_interval = get_live_chat_messages(live_chat_id, page_token)
    return jsonify({
        "messages": messages,
        "nextPageToken": next_page_token,
        "pollingInterval": polling_interval
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
