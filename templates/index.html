from flask import Flask, render_template, request
import isodate
import requests
import os
import re

app = Flask(__name__)

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_DETAILS_URL = "https://www.googleapis.com/youtube/v3/channels"


@app.route("/", methods=["GET", "POST"])
def index():
    videos = []
    search_words = ["", "", ""]
    exclude_words = ["", "", ""]
    min_views = ""
    max_views = ""
    sort_option = ""
    search_type = "video"
    search_limit = 50
    include_social = False

    if request.method == "POST":
        search_words = [request.form.get(f"keyword{i+1}", "") for i in range(3)]
        exclude_words = [request.form.get(f"exclude{i+1}", "") for i in range(3)]
        min_views = request.form.get("min_views", "")
        max_views = request.form.get("max_views", "")
        sort_option = request.form.get("sort", "")
        search_type = request.form.get("search_type", "video")
        search_limit = int(request.form.get("search_limit", 50))
        include_social = request.form.get("include_social") == "on"

        query = " ".join([w for w in search_words if w.strip()])

        params = {
            "key": YOUTUBE_API_KEY,
            "part": "snippet",
            "q": query,
            "type": search_type,
            "maxResults": 50,
        }

        all_video_ids = []
        all_channel_ids = set()
        next_page_token = None
        fetched = 0

        while fetched < search_limit:
            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(YOUTUBE_SEARCH_URL, params=params)
            items = response.json().get("items", [])

            for item in items:
                if search_type == "video":
                    all_video_ids.append(item["id"]["videoId"])
                elif search_type == "channel":
                    all_channel_ids.add(item["id"]["channelId"])
                fetched += 1
                if fetched >= search_limit:
                    break

            next_page_token = response.json().get("nextPageToken")
            if not next_page_token:
                break

        if search_type == "video" and all_video_ids:
            video_params = {
                "key": YOUTUBE_API_KEY,
                "part": "snippet,statistics",
                "id": ",".join(all_video_ids),
            }
            video_response = requests.get(YOUTUBE_VIDEO_DETAILS_URL, params=video_params)
            video_items = video_response.json().get("items", [])

            for item in video_items:
                snippet = item["snippet"]
                statistics = item.get("statistics", {})
                view_count = int(statistics.get("viewCount", 0))
                title = snippet["title"]

                if any(w.lower() in title.lower() for w in exclude_words if w):
                    continue

                if min_views and view_count < int(min_views):
                    continue
                if max_views and view_count > int(max_views):
                    continue

                channel_id = snippet["channelId"]
                all_channel_ids.add(channel_id)

                videos.append({
                    "title": title,
                    "video_id": item["id"],
                    "thumbnail": snippet["thumbnails"]["medium"]["url"],
                    "view_count": view_count,
                    "channel_id": channel_id,
                })

        channel_profiles = {}
        if all_channel_ids:
            channel_params = {
                "key": YOUTUBE_API_KEY,
                "part": "snippet,statistics",
                "id": ",".join(all_channel_ids),
            }
            channel_response = requests.get(YOUTUBE_CHANNEL_DETAILS_URL, params=channel_params)
            for item in channel_response.json().get("items", []):
                cid = item["id"]
                description = item["snippet"].get("description", "")
                subscribers = item["statistics"].get("subscriberCount", "0")

                if include_social and not ("@" in description or re.search(r"https?://|\.com|\.jp", description)):
                    continue

                channel_profiles[cid] = {
                    "description": description,
                    "subscribers": int(subscribers),
                }

        for v in videos:
            profile = channel_profiles.get(v["channel_id"], {})
            v["channel_description"] = profile.get("description", "")
            v["subscribers"] = profile.get("subscribers", 0)

        if sort_option == "views_desc":
            videos.sort(key=lambda x: x["view_count"], reverse=True)
        elif sort_option == "views_asc":
            videos.sort(key=lambda x: x["view_count"])
        elif sort_option == "newest":
            pass  # Not implemented

    return render_template("index.html", videos=videos, 
                           search_words=search_words, 
                           exclude_words=exclude_words,
                           min_views=min_views, max_views=max_views,
                           sort_option=sort_option, 
                           search_type=search_type,
                           search_limit=search_limit,
                           include_social=include_social)


if __name__ == "__main__":
    app.run(debug=True)
