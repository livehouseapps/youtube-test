from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        query = request.form.get('query', '')
        exclude1 = request.form.get('exclude1', '')
        exclude2 = request.form.get('exclude2', '')
        exclude3 = request.form.get('exclude3', '')
        lang_filter = request.form.get('lang_filter')
        keep_inputs = request.form.get('keep_inputs')
        min_views = int(request.form.get('min_views') or 0)
        max_views = int(request.form.get('max_views') or 10**12)
        published_after = request.form.get('published_after')
        order = request.form.get('order') or 'date'
        max_results = int(request.form.get('max_results') or 50)

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",
            "maxResults": min(max_results, 50),
            "type": "video",
            "order": order,
            "publishedAfter": published_after + "T00:00:00Z" if published_after else "2024-01-01T00:00:00Z"
        }

        search_response = requests.get(url, params=params).json()
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            publish_date = item["snippet"]["publishedAt"]
            description = item["snippet"]["description"]

            # 除外ワードチェック
            excluded = any(exclude in title for exclude in [exclude1, exclude2, exclude3] if exclude)
            if excluded:
                continue

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                item_stats = stats_response["items"][0]
                view_count = int(item_stats["statistics"]["viewCount"])
                subscriber_count = int(item_stats["snippet"].get("channelSubscriberCount", 0))
                channel_description = item_stats["snippet"].get("description", "")

                if lang_filter and any(x in channel_description.lower() for x in ["k-pop", "bts", "official", "eng", "viet"]):
                    continue

                if min_views <= view_count <= max_views:
                    videos.append({
                        "title": title,
                        "channel": channel,
                        "published": publish_date,
                        "views": view_count,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "subscribers": subscriber_count,
                        "description": channel_description
                    })
            except:
                continue

        # 並び替え
        if order == "viewCount":
            videos.sort(key=lambda x: x["views"], reverse=True)
        elif order == "viewCount_asc":
            videos.sort(key=lambda x: x["views"])
        elif order == "date":
            videos.sort(key=lambda x: x["published"], reverse=True)

    return render_template("index.html", videos=videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
