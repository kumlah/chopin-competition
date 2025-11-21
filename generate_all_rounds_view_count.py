#!/usr/bin/env python
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

# 入力：competitors.json（例：ファイナル / 第3 / 第2 / 第1 に動画IDが入っている想定）
COMPETITORS_PATH = Path("competitors.json")

# 出力：全ラウンド統合
OUTPUT_PATH = Path("all_rounds_view_count.json")

ROUND_KEYS = {
    "1st": "第1",
    "2nd": "第2",
    "3rd": "第3",
    "final": "ファイナル"
}


def load_video_ids_from_competitors():
    """
    competitors.json から、各ラウンドごとの動画IDリストを取得し、
    重複を除いた全動画ID一覧を返す。
    """
    if not COMPETITORS_PATH.exists():
        raise FileNotFoundError("competitors.json が見つかりません。")

    with COMPETITORS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    rounds = {rk: [] for rk in ROUND_KEYS.keys()}
    all_ids = []

    for person in data:
        for out_key, json_key in ROUND_KEYS.items():
            vid = person.get(json_key, "")
            if isinstance(vid, str) and vid.strip():
                rounds[out_key].append(vid)
                all_ids.append(vid)

    # 重複除去
    all_ids = list(dict.fromkeys(all_ids))
    return rounds, all_ids


def chunk_list(lst, size=50):
    """リストを size ごとに分割して返す。"""
    for i in range(0, len(lst), size):
        yield lst[i:i+size]


def fetch_video_stats(video_ids):
    """
    YouTube Data APIから viewCount / likeCount を取得して返す。
    publishedAt は取得しない。
    """
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    result = {}
    for item in data.get("items", []):
        vid = item["id"]
        stats = item.get("statistics", {})
        result[vid] = {
            "viewCount": int(stats.get("viewCount", 0)),
            "likeCount": int(stats.get("likeCount", 0))
        }
    return result


def main():
    rounds, all_ids = load_video_ids_from_competitors()

    videos = {}

    # 50件ずつ API に投げる
    for chunk in chunk_list(all_ids, 50):
        stats = fetch_video_stats(chunk)
        videos.update(stats)

    # JSON 書き出し
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y-%m-%d")

    output = {
        "date": today,
        "videos": videos,
        "rounds": rounds
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
