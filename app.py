from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def build_query(keywords, logic):
    words = [w.strip() for w in keywords if w.strip()]
    if logic == 'and':
        return " ".join(words)
    elif logic == 'or':
        return "|".join(words)
    return ""

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        include_keywords = [request.form.get(f'include{i}', '') for i in range(3)]
        exclude_keywords = [request.form.get(f'exclude{i}', '') for i in range(3)]
        logic = request.form.get('logic', 'and')
        min_views = int(request.form['min_views'] or 0)
        max_views = int(request.form['max_views'] or 1e10)
        published_after = request.form['published_after']
        region_filter = request.form.get('region', '') == 'jp'
        max_results = int(request.form['max_results'] or 25)
        fetch_all = request.form.get('fetch_all', '') == 'true'

        query = build_query(include_keywords, logic)
        if any(exclude_keywords):
            query += " " + " ".join(f"-{word}" for word in exclude_keywords if word)

        url = "https://www.googleapis.com/youtube/v3/search"
        videos_collected = 0
        page_token = None

        while True:
            params = {
                "key": YOUTUBE_API_KEY,
                "q": query,
                "part": "snippet",
                "maxResults": min(50, max_results - videos_collected),
                "type": "video",
                "order": "date",
                "publishedAfter": published_after + "T00:00:00Z" if published_after else "2024-01-01T00:00:00Z"
            }
            if region_filter:
                params["regionCode"] = "JP"
            if page_token:
                params["pageToken"] = page_token

            search_response = requests.get(url, params=params).json()
            for item in search_response.get("items", []):
                video_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                channel = item["snippet"]["channelTitle"]
                publish_date = item["snippet"]["publishedAt"]
                thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

                stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
                stats_response = requests.get(stats_url).json()
                try:
                    data = stats_response["items"][0]
                    view_count = int(data["statistics"]["viewCount"])
                    channel_desc = data["snippet"].get("channelTitle", "")
                    if min_views <= view_count <= max_views:
                        videos.append({
                            "title": title,
                            "channel": channel,
                            "published": publish_date,
                            "views": view_count,
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "thumbnail": thumbnail,
                            "desc": channel_desc
                        })
                        videos_collected += 1
                except:
                    continue

            page_token = search_response.get("nextPageToken")
            if not fetch_all or not page_token or videos_collected >= max_results:
                break

    return render_template("index.html", videos=videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
