# youtube_api_handler.py
import requests

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_live_video_id_by_channel(channel_id):
    """
    채널ID를 받아서 현재 라이브 중인 videoId 반환
    """
    params = {
        "part": "id",
        "channelId": channel_id,
        "eventType": "live",
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    res = requests.get("https://www.googleapis.com/youtube/v3/search", params=params).json()
    if "items" in res and len(res["items"]) > 0:
        return res["items"][0]["id"]["videoId"]
    return None

def get_live_stream_details(youtube_url):
    """
    기존 get_youtube_time에서 호출, 링크 기반
    """
    # videoId 추출
    video_id = get_video_id_from_url(youtube_url)
    if not video_id:
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

def get_video_id_from_url(url):
    """
    기존 링크에서 videoId 추출
    """
    import re
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    return None
