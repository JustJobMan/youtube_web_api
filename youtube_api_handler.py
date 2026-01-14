# youtube_api_handler.py
import requests
import re

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_video_id_from_channel(channel_id):
    """
    채널ID 기반으로 라이브 중인 videoId 반환.
    """
    params = {
        "part": "id",
        "channelId": channel_id,
        "eventType": "live",
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    live_res = requests.get("https://www.googleapis.com/youtube/v3/search", params=params).json()
    if "items" in live_res and len(live_res["items"]) > 0:
        return live_res["items"][0]["id"]["videoId"]
    return None

def get_live_stream_details(youtube_url):
    """
    기존 get_youtube_time에서 호출
    """
    video_id = None
    # 링크 기반 videoId 조회
    match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        video_id = match.group(1)
    if not video_id:
        # @핸들/live 같은 경우 처리는 서버에서 채널ID 기반
        return {"error": "유효한 유튜브 링크 또는 라이브를 찾을 수 없습니다."}

    # 방송 시간 조회
    video_res = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "liveStreamingDetails,snippet",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }
    ).json()

    if "items" not in video_res or len(video_res["items"]) == 0:
        return {"error": "라이브 영상 정보를 가져올 수 없습니다."}

    item = video_res["items"][0]
    live_details = item.get("liveStreamingDetails", {})
    return {
        "video_id": video_id,
        "title": item.get("snippet", {}).get("title"),
        "scheduledStartTime": live_details.get("scheduledStartTime"),
        "actualStartTime": live_details.get("actualStartTime"),
        "concurrentViewers": live_details.get("concurrentViewers")
    }
