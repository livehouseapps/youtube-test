from flask import Flask, render_template, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    query_words = ["", "", ""]
    exclude_words = ["", "", ""]
    search_mode = "OR"
    min_views = None
    max_views = None
    published_after = ""
    max_results = 50
    keep_input = False
    sort_order = "none"

    if request.method == 'POST':
        query_words = [request.form.get(f'query{i}', '') for i in range(1, 4)]
        exclude_words = [request.form.get(f'exclude{i}', '') for i in range(1, 4)]
        search_mode = request.form.get('search_mode', 'OR')
        min_views = request.form.get('min_views')
        max_views = request.form.get('max_views')
        published_after = request.form.get('published_after')
        max_results = int(request.form.get('max_results') or 50)
        keep_input = request.form.get('keep_input') == 'on'
        sort_order = request.form.get('sort_order', 'none')

        include_query = f" {search_mode} ".join([q for q in query_words if q])
        exclude_query = " ".join([f"-{w}" for w in exclude_words if w])
        full_query = (include_query + " " + exclude_query).strip()

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": full_query,
            "part": "snippet",
            "maxResults": min(max_results, 50),
            "type": "video",
            "order": "date",
            "publishedAfter": published_after + "T00:00:00Z" if published_after else "2024-01-01T00:00:00Z"
        }

        search_response = requests.get(url, params=params).json()

        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel_id = item["snippet"]["channelId"]
            channel = item["snippet"]["channelTitle"]
            publish_date = item["snippet"]["publishedAt"]
            thumbnail_url = item["snippet"]["thumbnails"]["medium"]["url"]

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()

            channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
            channel_response = requests.get(channel_url).json()

            try:
                view_count = int(stats_response["items"][0]["statistics"]["viewCount"])
                subscribers = int(channel_response["items"][0]["statistics"].get("subscriberCount", 0))
                description = channel_response["items"][0]["snippet"].get("description", "")

                if (not min_views or view_count >= int(min_views)) and (not max_views or view_count <= int(max_views)):
                    videos.append({
                        "title": title,
                        "channel": channel,
                        "channel_description": description,
                        "subscribers": subscribers,
                        "published": publish_date,
                        "views": view_count,
                        "thumbnail": thumbnail_url,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
            except:
                continue

        if sort_order == "views_desc":
            videos.sort(key=lambda x: x['views'], reverse=True)
        elif sort_order == "views_asc":
            videos.sort(key=lambda x: x['views'])
        elif sort_order == "date":
            videos.sort(key=lambda x: datetime.strptime(x['published'], "%Y-%m-%dT%H:%M:%SZ"), reverse=True)

    return render_template("index.html", videos=videos,
                           query_words=query_words,
                           exclude_words=exclude_words,
                           search_mode=search_mode,
                           min_views=min_views or "",
                           max_views=max_views or "",
                           published_after=published_after,
                           max_results=max_results,
                           keep_input=keep_input,
                           sort_order=sort_order)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
