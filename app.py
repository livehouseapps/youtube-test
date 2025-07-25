from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_details(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "key": YOUTUBE_API_KEY,
        "id": channel_id,
        "part": "snippet,statistics"
    }
    response = requests.get(url, params=params).json()
    if "items" in response and len(response["items"]) > 0:
        snippet = response["items"][0]["snippet"]
        statistics = response["items"][0]["statistics"]
        return {
            "description": snippet.get("description", ""),
            "subscribers": int(statistics.get("subscriberCount", 0))
        }
    return {"description": "", "subscribers": 0}

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    keep_input = True
    if request.method == 'POST':
        query_list = [request.form.get(f'query{i}', '') for i in range(1, 4)]
        exclude_words = request.form.get('exclude', '').split()
        min_views = int(request.form.get('min_views') or 0)
        max_views = int(request.form.get('max_views') or 10**12)
        published_after = request.form.get('published_after') or '2024-01-01'
        max_results = int(request.form.get('max_results') or 50)
        only_japanese = request.form.get('only_japanese') == 'on'
        keep_input = request.form.get('keep_input') == 'on'

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": " ".join(query_list),
            "part": "snippet",
            "maxResults": min(50, max_results),
            "type": "video",
            "order": "date",
            "publishedAfter": published_after + "T00:00:00Z"
        }

        search_response = requests.get(url, params=params).json()

        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]
            publish_date = item["snippet"]["publishedAt"]
            channel_id = item["snippet"]["channelId"]
            if exclude_words and any(ex in title for ex in exclude_words):
                continue

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                view_count = int(stats_response["items"][0]["statistics"]["viewCount"])
                if not (min_views <= view_count <= max_views):
                    continue
            except:
                continue

            channel_details = get_channel_details(channel_id)
            if only_japanese and not any('\u3040' <= c <= '\u30ff' for c in title):
                continue

            videos.append({
                "title": title,
                "channel": channel,
                "published": publish_date,
                "views": view_count,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                "channel_description": channel_details["description"],
                "subscribers": channel_details["subscribers"]
            })

    return render_template("index.html", videos=videos, keep_input=keep_input, form=request.form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
