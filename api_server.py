from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from youtube_api_handler import get_live_stream_details, get_video_id_from_channel
import re

app = Flask(__name__)
CORS(app)

# HTML에서 버튼 클릭 시 사용
CHANNEL_MAP = {
    "여우": "UCmdBA1aN06wlUl29x0MYf5w",
    "현승": "UC2JW8eHSobyEFqME7u_WGxA",
    "준기": "UCWfWEhWbaUQ-OL2Qh231iAw",
    "일뚜": "UCTMSBtBmt2lf9tm8Nri7zDw",
    "뱅진": "UCcyCsHYIn1F_u-k4w38smoA",
    "렌지": "UCTMSBtBmt2lf9tm8Nri7zDw",
    "여누킹": "UChPS68Lq1znFEkC4yA2OgwQ",
    "덕근": "UCjPZjkCqyxtT2Jfr8xsR12Q",
    "마왕": "UCNb-uMihutMhX9SJ5NQsMZg",
    "진또": "UCpg_r1e7K8l1N91O75oEsiQ",
    "윤시원": "UCBXWqgmDszukzW-Tbd-Ur_w",
    "주작남": "UCm_yg5iPpDhZ7qSZ0HFbwug",
    "사수기릿": "UCWYcVc0rUfQ3hOntgo4NBAA"
}

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
    """
    HTML 버튼 클릭 -> channelName 전달 -> videoId 반환
    """
    data = request.get_json()
    channel_name = data.get("channelName")
    if not channel_name or channel_name not in CHANNEL_MAP:
        return jsonify({"error": "유효한 채널 이름이 아닙니다."}), 400

    channel_id = CHANNEL_MAP[channel_name]
    video_id = get_video_id_from_channel(channel_id)
    if not video_id:
        return jsonify({"error": "라이브 중인 비디오를 찾을 수 없습니다."}), 400

    return jsonify({"video_id": video_id})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
