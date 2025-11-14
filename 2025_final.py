# 2025_final.py
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

# YouTube APIキー（GitHub Actions では Secrets から渡す）
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

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

OUTPUT_FILE = Path("2025_final.json")


def get_today_jst_date_str():
    """JSTの日付（YYYY-MM-DD）を返す。"""
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    return now_jst.strftime("%Y-%m-%d")


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

        like_count = stats.get("likeCount")
        if like_count is not None:
            like_count = int(like_count)

        result = {
            "videoId": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "publishedAt": snippet.get("publishedAt"),
            "title": snippet.get("title"),
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": like_count,
        }
        results.append(result)

    return results


def load_existing_history():
    """既存の2025_final.jsonを読み込んで、リストとして返す。なければ空リスト。"""
    if not OUTPUT_FILE.exists():
        return []

    try:
        with OUTPUT_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        else:
            print("注意: 既存のJSONがリストではありません。新規に作り直します。")
            return []
    except Exception as e:
        print(f"注意: 既存JSONの読み込みに失敗しました: {e}")
        return []


def main():
    # JSTの日付
    date_str = get_today_jst_date_str()

    # 動画情報を取得
    video_data = fetch_video_data()

    # 既存履歴を読み込み
    history = load_existing_history()

    # 今回分のエントリ
    entry = {
        "date": date_str,
        "videos": video_data,
    }

    # 既存履歴に追加（同じ日付が既にあっても今回は気にせず追記）
    history.append(entry)

    # JSONとして保存
    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"{date_str} のデータとして {len(video_data)}件を履歴に追加し、{OUTPUT_FILE} を更新しました。")


if __name__ == "__main__":
    main()
