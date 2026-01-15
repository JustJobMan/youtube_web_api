# youtube_api_handler.py
import requests
import re

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_video_id_from_url(url):
    """유튜브 링크에서 videoId 추출"""
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    return None

# 1️⃣ 채널ID 기반 라이브 감지 (원래 기능 그대로)
def get_live_video_id_by_channel(channel_id):
    """
    채널ID 기반으로 진행 중 라이브 videoId 반환
    eventType=live 사용 → 원래 기능 그대로
    """
    params = {
        "part": "id",
        "channelId": channel_id,
        "eventType": "live",  # 라이브 감지용
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    res = requests.get("https://www.googleapis.com/youtube/v3/search", params=params).json()
    if "items" in res and len(res["items"]) > 0:
        return res["items"][0]["id"]["videoId"]
    return None

# 2️⃣ 시간조회 독립 함수 완전 복원
def get_youtube_time(youtube_url):
    """
    URL 기반 방송 시간 조회
    실제 방송 시작시간, 예약시간 반환
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
    return {
        "video_id": video_id,
        "title": item.get("snippet", {}).get("title"),
        "scheduledStartTime": live_details.get("scheduledStartTime"),
        "actualStartTime": live_details.get("actualStartTime"),
        "concurrentViewers": live_details.get("concurrentViewers")
    }

# 3️⃣ 라이브 채팅 ID 조회
def get_live_chat_id(youtube_url):
    """
    videoId 기반 라이브 채팅 ID 반환
    """
    video_id = get_video_id_from_url(youtube_url)
    if not video_id:
        return None

    res = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "liveStreamingDetails",
            "id": video_id,
            "key": YOUTUBE_API_KEY
        }
    ).json()

    if "items" in res and len(res["items"]) > 0:
        live_details = res["items"][0].get("liveStreamingDetails", {})
        return live_details.get("activeLiveChatId")
    return None
