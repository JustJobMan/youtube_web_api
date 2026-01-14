# youtube_api_handler.py
import requests
import re

YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"  # 실제 키로 교체

def get_video_id_from_handle(url_or_handle):
    """
    핸들(@핸들/live) 또는 유튜브 링크를 받아서 videoId 반환.
    라이브 중인 영상만 반환.
    """
    # 1️⃣ 핸들 URL이면 채널ID 가져오기
    match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)/?live', url_or_handle)
    if match:
        handle = match.group(1)
        # 채널ID 조회
        channel_res = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "id",
                "forUsername": handle,   # 일반 @핸들용
                "key": YOUTUBE_API_KEY
            }
        ).json()
        if "items" in channel_res and len(channel_res["items"]) > 0:
            channel_id = channel_res["items"][0]["id"]
        else:
            # @핸들 방식 실패 시, search API 사용
            search_res = requests.get(
                "https://www.googleapis.com/youtube/v3/search",
                params={
                    "part": "snippet",
                    "q": handle,
                    "type": "channel",
                    "key": YOUTUBE_API_KEY
                }
            ).json()
            if "items" in search_res and len(search_res["items"]) > 0:
                channel_id = search_res["items"][0]["id"]["channelId"]
            else:
                return None
    else:
        # 일반 유튜브 링크
        channel_id = None

    # 2️⃣ 채널ID 기반으로 라이브 비디오 검색
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
    video_id = get_video_id_from_handle(youtube_url)
    if not video_id:
        return {"error": "유효한 유튜브 링크 또는 라이브를 찾을 수 없습니다."}

    # 방송 시간 조회 (예시)
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
