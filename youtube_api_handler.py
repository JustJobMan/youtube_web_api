# youtube_api_handler.py
import os
from datetime import datetime, timedelta
import re
import pytz
import googleapiclient.discovery
import googleapiclient.errors

def get_youtube_service_instance():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY 환경 변수가 설정되지 않았습니다.")
    return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

YOUTUBE_SERVICE = get_youtube_service_instance()

# 방송 시간 가져오기
def get_live_stream_details(youtube_url: str):
    video_id = None
    match = re.search(r'(?:v=|youtu\.be/|live/)([a-zA-Z0-9_-]{11})', youtube_url)
    if match:
        video_id = match.group(1)
    if not video_id:
        return {"error": "유효한 유튜브 링크 주소를 찾을 수 없습니다."}

    try:
        request = YOUTUBE_SERVICE.videos().list(
            part="liveStreamingDetails,snippet",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            return {"error": f"해당 ID({video_id})에 대한 유튜브 비디오 정보를 찾을 수 없습니다."}

        item = response['items'][0]
        live_details = item.get('liveStreamingDetails')
        snippet = item.get('snippet')

        if not live_details:
            return {"error": "이 비디오는 라이브 스트리밍 정보가 없는 것 같습니다. 라이브 스트림만 지원합니다."}

        title = snippet.get('title', '제목 없음')
        channel_title = snippet.get('channelTitle', '채널 정보 없음')

        start_time_str = live_details.get('actualStartTime')
        end_time_str = live_details.get('actualEndTime')

        korea_tz = pytz.timezone('Asia/Seoul')

        start_dt_kst = None
        end_dt_kst = None
        total_duration = None

        if start_time_str:
            start_dt_utc = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            start_dt_kst = start_dt_utc.astimezone(korea_tz)
        if end_time_str:
            end_dt_utc = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
            end_dt_kst = end_dt_utc.astimezone(korea_tz)
        if start_dt_kst and end_dt_kst:
            total_duration = end_dt_kst - start_dt_kst
        elif start_dt_kst:
            current_dt_utc = datetime.now(pytz.utc)
            current_dt_kst = current_dt_utc.astimezone(korea_tz)
            total_duration = current_dt_kst - start_dt_kst

        result = {
            "title": title,
            "channel_title": channel_title,
            "start_time": start_dt_kst.strftime('%Y-%m-%d %H:%M:%S') if start_dt_kst else "정보 없음",
            "end_time": end_dt_kst.strftime('%Y-%m-%d %H:%M:%S') if end_dt_kst else ("현재 라이브 중" if start_dt_kst else "정보 없음"),
            "total_duration_formatted": f"{int(total_duration.total_seconds()) // 3600}시간 " +
                                        f"{(int(total_duration.total_seconds()) % 3600) // 60}분 " +
                                        f"{int(total_duration.total_seconds()) % 60}초" if total_duration else "계산 불가"
        }
        return result

    except googleapiclient.errors.HttpError as e:
        return {"error": f"유튜브 API 오류: {e}"}
    except Exception as e:
        return {"error": f"알 수 없는 오류: {e}"}

# --- 실시간 채팅 관련 ---
def get_live_chat_id(video_id):
    request = YOUTUBE_SERVICE.videos().list(
        part="liveStreamingDetails",
        id=video_id
    )
    response = request.execute()
    items = response.get('items')
    if not items:
        return None
    live_details = items[0].get('liveStreamingDetails', {})
    return live_details.get('activeLiveChatId')

def get_live_chat_messages(live_chat_id, page_token=None):
    request = YOUTUBE_SERVICE.liveChatMessages().list(
        liveChatId=live_chat_id,
        part="snippet,authorDetails",
        maxResults=200,
        pageToken=page_token
    )
    response = request.execute()
    messages = []
    for item in response.get('items', []):
        msg = item['snippet']['displayMessage']
        author = item['authorDetails']['displayName']
        messages.append(f"{author}: {msg}")
    next_page_token = response.get('nextPageToken')
    polling_interval = response.get('pollingIntervalMillis', 5000) / 1000
    return messages, next_page_token, polling_interval
