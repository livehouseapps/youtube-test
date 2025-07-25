from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    query = ""
    exclude_words = ["", "", ""]
    min_views = 0
    max_views = None
    published_after = ""
    max_results = 25
    lang_filter = False
    keep_inputs = False
    sort_method = ""

    if request.method == 'POST':
        query = request.form.get('query', "")
        exclude_words = [
            request.form.get('exclude1', ""),
            request.form.get('exclude2', ""),
            request.form.get('exclude3', "")
        ]
        min_views = int(request.form.get('min_views') or 0)
        max_views_input = request.form.get('max_views')
        max_views = int(max_views_input) if max_views_input else None
        published_after = request.form.get('published_after', "")
        max_results = int(request.form.get('max_results') or 25)
        lang_filter = request.form.get('lang_filter') == "on"
        keep_inputs = request.form.get('keep_inputs') == "on"
        sort_method = request.form.get('sort_method', "")

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",
            "maxResults": 50 if max_results > 50 else max_results,
            "type": "video",
            "order": "date",
            "publishedAfter": published_after + "T00:00:00Z" if published_after else "2024-01-01T00:00:00Z"
        }

        search_response = requests.get(url, params=params).json()
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            channel_id = item["snippet"]["channelId"]
            publish_date = item["snippet"]["publishedAt"]
            description = item["snippet"]["description"]

            # チャンネル情報
            channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
            channel_response = requests.get(channel_url).json()
            try:
                subscriber_count = int(channel_response["items"][0]["statistics"].get("subscriberCount", 0))
                channel_description = channel_response["items"][0]["snippet"].get("description", "")
                country = channel_response["items"][0]["snippet"].get("country", "N/A")
            except:
                subscriber_count = 0
                channel_description = ""
                country = "N/A"

            # 統計情報
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                view_count = int(stats_response["items"][0]["statistics"]["viewCount"])
            except:
                continue

            # 除外ワードチェック
            if any(word.lower() in title.lower() for word in exclude_words if word):
                continue

            # 言語フィルタ（日本以外除外）
            if lang_filter and country not in ["JP", "日本"]:
                continue

            # 再生数フィルタ
            if view_count < min_views:
                continue
            if max_views is not None and view_count > max_views:
                continue

            videos.append({
                "title": title,
                "channel": channel,
                "channel_description": channel_description,
                "subscriber_count": subscriber_count,
                "published": publish_date,
                "views": view_count,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
            })

        # 並べ替え
        if sort_method == "views_desc":
            videos.sort(key=lambda x: x["views"], reverse=True)
        elif sort_method == "views_asc":
            videos.sort(key=lambda x: x["views"])
        elif sort_method == "date":
            videos.sort(key=lambda x: x["published"], reverse=True)

    return render_template("index.html", videos=videos,
                           query=query,
                           exclude_words=exclude_words,
                           min_views=min_views,
                           max_views=max_views_input or "",
                           published_after=published_after,
                           max_results=max_results,
                           lang_filter=lang_filter,
                           keep_inputs=keep_inputs,
                           sort_method=sort_method)
