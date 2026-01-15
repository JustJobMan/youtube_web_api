# youtube_api_handler.py
import requests
import re
from datetime import datetime

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_video_id_from_url(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    return None

def get_live_stream_details(youtube_url):
    """
    URL 기반 방송 시간 조회 (원래 기능)
    시:분:초 포함
    """
    video_id = get_video_id_from_url(youtube_url)
    if not video_id:
        return {"error": "유효한 유튜브 링크가 아닙니다."}

    res = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "liveStreamingDetails,snippet",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }
    ).json()

    if "items" not in res or len(res["items"]) == 0:
        return {"error": "라이브 정보를 가져올 수 없습니다."}

    item = res["items"][0]
    live_details = item.get("liveStreamingDetails", {})

    def format_time(t):
        if t:
            try:
                dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return t
        return None

    return {
        "video_id": video_id,
        "title": item.get("snippet", {}).get("title"),
        "scheduledStartTime": format_time(live_details.get("scheduledStartTime")),
        "actualStartTime": format_time(live_details.get("actualStartTime")),
        "concurrentViewers": live_details.get("concurrentViewers")
    }
