from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    query = ""
    min_views = 0
    max_views = None
    published_after = ""
    order = "date"
    max_results = 25
    exclude1 = ""
    exclude2 = ""
    exclude3 = ""
    keep_inputs = ""

    if request.method == 'POST':
        query = request.form.get('query', '')
        min_views = int(request.form.get('min_views') or 0)
        max_views = request.form.get('max_views')
        max_views = int(max_views) if max_views else None
        published_after = request.form.get('published_after', '')
        order = request.form.get('order', 'date')
        max_results = int(request.form.get('max_results') or 25)
        exclude1 = request.form.get('exclude1', '')
        exclude2 = request.form.get('exclude2', '')
        exclude3 = request.form.get('exclude3', '')
        keep_inputs = request.form.get('keep_inputs', '')

        exclude_words = [exclude1, exclude2, exclude3]
        exclude_words = [word.strip().lower() for word in exclude_words if word.strip()]

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part": "snippet",
            "maxResults": max_results,
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

            # 除外ワードチェック
            if any(word in title.lower() for word in exclude_words):
                continue

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                stats = stats_response["items"][0]["statistics"]
                snippet = stats_response["items"][0]["snippet"]
                view_count = int(stats["viewCount"])
                subscriber_count = int(snippet.get("channelSubscriberCount", 0))
                description = snippet.get("description", "")

                if view_count >= min_views and (max_views is None or view_count <= max_views):
                    videos.append({
                        "title": title,
                        "channel": channel,
                        "published": publish_date,
                        "views": view_count,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "description": description,
                        "subscribers": subscriber_count
                    })
            except:
                continue

        # 並べ替え
        if order == "viewcount":
            videos.sort(key=lambda x: x["views"], reverse=True)
        elif order == "viewcount_asc":
            videos.sort(key=lambda x: x["views"])
        elif order == "date":
            videos.sort(key=lambda x: x["published"], reverse=True)

    return render_template(
        "index.html",
        videos=videos,
        exclude_words=[exclude1, exclude2, exclude3],
        keep_inputs=keep_inputs or '',
        query=query,
        min_views=min_views,
        max_views=max_views,
        published_after=published_after,
        order=order,
        max_results=max_results
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
