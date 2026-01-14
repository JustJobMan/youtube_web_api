import os
from datetime import datetime
import re
import pytz
import googleapiclient.discovery

def get_youtube_service_instance():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY 환경 변수가 설정되지 않았습니다.")
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

YOUTUBE_SERVICE = get_youtube_service_instance()

def find_latest_live_video_id(channel_name: str):
    try:
        search_request = YOUTUBE_SERVICE.search().list(
            part="snippet",
            q=channel_name,
            type="video",
            eventType="live",
            maxResults=1
        )
        search_response = search_request.execute()
        items = search_response.get('items', [])
        if not items:
            return None
        return items[0]['id']['videoId']
    except Exception as e:
        print(f"Error finding live video ID: {e}")
        return None

def get_live_stream_details(youtube_input: str):
    video_id = None
    match = re.search(r'(?:v=|youtu\.be/|live/)([a-zA-Z0-9_-]{11})', youtube_input)
    if match:
        video_id = match.group(1)
    else:
        video_id = find_latest_live_video_id(youtube_input)

    if not video_id:
        return {"error": "유효한 유튜브 링크 또는 라이브를 찾을 수 없습니다."}

    try:
        request = YOUTUBE_SERVICE.videos().list(
            part="liveStreamingDetails,snippet",
            id=video_id
        )
        response = request.execute()
        if not response['items']:
            return {"error": f"해당 ID({video_id})에 대한 정보를 찾을 수 없습니다."}

        item = response['items'][0]
        live_details = item.get('liveStreamingDetails')
        snippet = item.get('snippet')

        if not live_details:
            return {"error": "이 비디오는 라이브 정보가 없습니다."}

        title = snippet.get('title', '제목 없음')
        channel_title = snippet.get('channelTitle', '채널 정보 없음')

        start_time_str = live_details.get('actualStartTime')
        end_time_str = live_details.get('actualEndTime')
        korea_tz = pytz.timezone('Asia/Seoul')
        start_dt_kst = end_dt_kst = total_duration = None

        if start_time_str:
            start_dt_utc = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            start_dt_kst = start_dt_utc.astimezone(korea_tz)
        if end_time_str:
            end_dt_utc = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            end_dt_kst = end_dt_utc.astimezone(korea_tz)

        if start_dt_kst and end_dt_kst:
            total_duration = end_dt_kst - start_dt_kst
        elif start_dt_kst and not end_dt_kst:
            current_dt_utc = datetime.now(pytz.utc)
            current_dt_kst = current_dt_utc.astimezone(korea_tz)
            total_duration = current_dt_kst - start_dt_kst

        result = {
            "video_id": video_id,
            "title": title,
            "channel_title": channel_title,
            "start_time": start_dt_kst.strftime('%Y-%m-%d %H:%M:%S') if start_dt_kst else "정보 없음",
            "end_time": end_dt_kst.strftime('%Y-%m-%d %H:%M:%S') if end_dt_kst else ("현재 라이브 중" if start_dt_kst else "정보 없음"),
            "total_duration_formatted": (f"{int(total_duration.total_seconds()) // 3600}시간 "
                                         f"{(int(total_duration.total_seconds()) % 3600) // 60}분 "
                                         f"{int(total_duration.total_seconds()) % 60}초") if total_duration else "계산 불가"
        }
        return result
    except Exception as e:
        return {"error": f"유튜브 API 호출 중 오류: {e}"}

def get_live_chat_id(video_id):
    try:
        request = YOUTUBE_SERVICE.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )
        response = request.execute()
        items = response.get('items', [])
        if not items:
            return None
        return items[0]['liveStreamingDetails'].get('activeLiveChatId')
    except Exception as e:
        print(f"Error getting live chat ID: {e}")
        return None
