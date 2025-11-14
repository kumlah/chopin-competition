# 2025final.py
import os
import json
import requests

# YouTube Data API v3 の APIキー
# 環境変数 YOUTUBE_API_KEY に入れておくのがおすすめ
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

# 取得したい動画ID一覧
VIDEO_IDS = [
    "BOCTW4qyDqY",
    "_QgvXbaLFPs",
    "QklhpTBNp3s",
    "8gphqTkmnR8",
    "tYfpS1jt8ck",
    "GFTHzzFA-TQ",
    "_G0TBsTYjvQ",
    "xsVgT3vtruM",
    "1WdkvGV7sBY",
    "omqTpiBXfnA",
    "5duUDPKSrKk",
]

def fetch_video_data():
    url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,statistics",
        "id": ",".join(VIDEO_IDS),
        "key": API_KEY,
        "maxResults": 50,
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    results = []

    for item in data.get("items", []):
        vid = item.get("id")
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        # likeCount は非公開設定だと返ってこないことがあるので None 許容
        like_count = stats.get("likeCount")
        if like_count is not None:
            like_count = int(like_count)

        result = {
            "videoId": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "publishedAt": snippet.get("publishedAt"),   # ISO8601文字列
            "title": snippet.get("title"),
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": like_count,
        }
        results.append(result)

    return results


def main():
    video_data = fetch_video_data()
    output_file = "2025final.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    print(f"{len(video_data)}件の動画情報を {output_file} に保存しました。")


if __name__ == "__main__":
    main()
