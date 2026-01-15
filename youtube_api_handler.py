# youtube_api_handler.py
import requests
import re

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_video_id_from_url(url):
    """
    기존 링크에서 videoId 추출
    """
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    return None

def get_live_video_id_by_channel(channel_id, max_results=5):
    """
    채널ID를 받아서 현재 진행 중인 라이브 videoId 반환
    최근 max_results개의 영상 확인
    """
    # 최근 업로드 영상 가져오기 (eventType 제거)
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "maxResults": max_results,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    res = requests.get("https://www.googleapis.com/youtube/v3/search", params=params).json()
    
    if "items" not in res or len(res["items"]) == 0:
        return None

    # 각 영상의 liveStreamingDetails 확인
    for item in res["items"]:
        video_id = item["id"]["videoId"]
        video_res = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "liveStreamingDetails",
                "id": video_id,
                "key": YOUTUBE_API_KEY
            }
        ).json()

        if "items" in video_res and len(video_res["items"]) > 0:
            live_details = video_res["items"][0].get("liveStreamingDetails", {})
            if live_details and "actualStartTime" in live_details:
                # 진행 중인 라이브 발견
                return video_id

    return None

def get_live_stream_details(youtube_url):
    """
    기존 get_youtube_time에서 호출, 링크 기반
    """
    video_id = get_video_id_from_url(youtube_url)
    if not video_id:
        return {"error": "유효한 유튜브 링크 또는 라이브를 찾을 수 없습니다."}

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
