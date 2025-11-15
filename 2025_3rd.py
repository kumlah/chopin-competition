# 2025_3rd.py
import os
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

# YouTube APIキー（GitHub Actions では Secrets から渡す）
API_KEY = os.environ.get("YOUTUBE_API_KEY", "YOUR_API_KEY_HERE")

OUTPUT_FILE = Path("2025_3rd.json")
COMPETITORS_PATH = Path("competitors.json")

# competitors.json の「第3」列名
# 列名が違う場合はここを書き換えてください
ROUND_COLUMN = "第3"


def get_today_jst_date_str():
    """JSTの日付（YYYY-MM-DD）を返す。"""
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    return now_jst.strftime("%Y-%m-%d")


def load_video_ids_from_competitors():
    """
    competitors.json から「第3」列(ROUND_COLUMN)に動画IDが入っているものだけを抽出し、
    順番を保ったまま重複を取り除いたリストを返す。
    """
    if not COMPETITORS_PATH.exists():
        raise FileNotFoundError(f"{COMPETITORS_PATH} が見つかりません。")

    with COMPETITORS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("competitors.json の最上位はリスト形式を想定しています。")

    video_ids = []
    seen = set()

    for comp in data:
        vid = comp.get(ROUND_COLUMN)
        if not vid:
            continue
        if vid in seen:
            continue
        seen.add(vid)
        video_ids.append(vid)

    if not video_ids:
        raise ValueError(
            f"competitors.json に {ROUND_COLUMN} の動画IDが1件も見つかりませんでした。"
        )

    return video_ids


def fetch_video_data(video_ids):
    """
    与えられた video_ids の統計情報を YouTube Data API から取得して返す。
    タイトルは保存しない（title キーを持たせない）。
    """
    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    results = []

    # 念のため50件ずつに分割（YouTube APIのidパラメータ上限対策）
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i : i + chunk_size]

        params = {
            "part": "snippet,statistics",  # publishedAt を取るために snippet は残す
            "id": ",".join(chunk),
            "key": API_KEY,
            "maxResults": 50,
        }

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

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
                # title は保存しない
                "viewCount": int(stats.get("viewCount", 0)),
                "likeCount": like_count,
            }
            results.append(result)

    return results


def load_existing_history():
    """既存の2025_3rd.jsonを読み込んで、リストとして返す。なければ空リスト。"""
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

    # competitors.json から第3ラウンド動画ID一覧を取得
    video_ids = load_video_ids_from_competitors()

    # 動画情報を取得
    video_data = fetch_video_data(video_ids)

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

    print(
        f"{date_str} のデータとして {len(video_data)}件を履歴に追加し、{OUTPUT_FILE} を更新しました。"
    )


if __name__ == "__main__":
    main()
