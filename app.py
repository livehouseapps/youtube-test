from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        query = request.form['query']
        min_views = int(request.form['min_views'] or 0)
        max_views = int(request.form['max_views'] or 1_000_000_000)  # デフォルト上限大きめ
        published_after = request.form['published_after']
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",
            "maxResults": 25,
            "type": "video",
            "order": "date",
            "publishedAfter": published_after + "T00:00:00Z" if published_after else "2024-01-01T00:00:00Z"
        }
        search_response = requests.get(url, params=params).json()
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            publish_date = item["snippet"]["publishedAt"]
            thumbnail = item["snippet"]["thumbnails"]["default"]["url"]
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                view_count = int(stats_response["items"][0]["statistics"]["viewCount"])
                if min_views <= view_count <= max_views:
                    videos.append({
                        "title": title,
                        "channel": channel,
                        "published": publish_date,
                        "views": view_count,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": thumbnail
                    })
            except:
                continue
    return render_template("index.html", videos=videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
