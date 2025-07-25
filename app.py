from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        query = request.form.get('query') or ""
        query2 = request.form.get('query2') or ""
        query3 = request.form.get('query3') or ""
        exclude = request.form.get('exclude') or ""
        logic = request.form.get('logic') or "AND"
        min_views = int(request.form.get('min_views') or 0)
        max_views = int(request.form.get('max_views') or 10**12)
        published_after = request.form.get('published_after') or "2024-01-01"
        max_results = int(request.form.get('max_results') or 25)
        only_jp = request.form.get('only_jp') == 'on'

        final_query = [query, query2, query3]
        final_query = [q for q in final_query if q]
        if logic == "AND":
            search_query = " ".join(final_query)
        else:
            search_query = "|".join(final_query)

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "q": search_query,
            "part": "snippet",
            "maxResults": min(50, max_results),  # maxResults上限50
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
            thumbnail = item["snippet"]["thumbnails"]["high"]["url"]

            if exclude and exclude.lower() in title.lower():
                continue

            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_id}&key={YOUTUBE_API_KEY}"
            stats_response = requests.get(stats_url).json()
            try:
                video_data = stats_response["items"][0]
                view_count = int(video_data["statistics"]["viewCount"])
                description = video_data["snippet"]["description"]
                channel_id = video_data["snippet"]["channelId"]

                if not (min_views <= view_count <= max_views):
                    continue

                # チャンネル情報取得
                channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
                channel_response = requests.get(channel_url).json()
                channel_data = channel_response["items"][0]
                subscriber_count = channel_data["statistics"].get("subscriberCount", "非公開")
                channel_description = channel_data["snippet"]["description"]
                country = channel_data["snippet"].get("country", "")

                if only_jp and country not in ["JP", ""]:
                    continue

                videos.append({
                    "title": title,
                    "channel": channel,
                    "published": publish_date,
                    "views": view_count,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": thumbnail,
                    "channel_description": channel_description,
                    "subscribers": subscriber_count
                })
            except:
                continue
    return render_template("index.html", videos=videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
