import csv
import json
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen, URLError


# ここでは APIキーはコードに書かず、
# 環境変数 YOUTUBE_API_KEY から読み込みます（GitHub ActionsのSecretsでセット）
API_KEY_ENV_NAME = "YOUTUBE_API_KEY"

# ここに調べたい動画IDを並べる
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
    # 必要に応じて追加
]

# 出力するCSVファイル名
OUTPUT_CSV = "2025final.csv"


def get_api_key():
    """環境変数からAPIキーを取得。なかったら例外を投げる。"""
    api_key = os.environ.get(API_KEY_ENV_NAME)
    if not api_key:
        raise RuntimeError(
            f"環境変数 {API_KEY_ENV_NAME} が設定されていません。"
            " GitHub Actions の Secrets に設定し、env で渡してください。"
        )
    return api_key


def get_jst_now_str():
    """日本時間の現在日時を文字列で返す"""
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    # 例: 2025-11-14 23:59:59
    return now_jst.strftime("%Y-%m-%d")


def fetch_video_stats(api_key, video_ids):
    """
    YouTube Data API から動画情報を取得する
    戻り値: {videoId: {publishedAt, viewCount, likeCount}} の辞書
    """
    if not video_ids:
        return {}

    base_url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": api_key,
        "maxResults": 50,  # videos.list の仕様上最大50
    }

    url = f"{base_url}?{urlencode(params)}"

    try:
        with urlopen(url) as response:
            data = json.load(response)
    except URLError as e:
        raise RuntimeError(f"YouTube APIへのリクエストに失敗しました: {e}") from e

    result = {}
    for item in data.get("items", []):
        vid = item.get("id")
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        published_at = snippet.get("publishedAt", "")

        # 再生回数・いいね数は「統計情報がない」「いいね非表示」などの場合もあるので get で取る
        view_count = stats.get("viewCount")
        like_count = stats.get("likeCount")

        # None の場合は空文字にしておく（CSVで扱いやすい）
        if view_count is None:
            view_count = ""
        if like_count is None:
            like_count = ""

        result[vid] = {
            "publishedAt": published_at,
            "viewCount": view_count,
            "likeCount": like_count,
        }

    return result


def write_csv(filename, video_ids, video_data, retrieved_at_jst):
    """
    CSVを書き出す
    列：
    retrieved_at_jst, video_id, published_at, view_count, like_count
    """
    header = ["retrieved_at_jst", "video_id", "published_at", "view_count", "like_count"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for vid in video_ids:
            info = video_data.get(vid, {})
            writer.writerow(
                [
                    retrieved_at_jst,
                    vid,
                    info.get("publishedAt", ""),
                    info.get("viewCount", ""),
                    info.get("likeCount", ""),
                ]
            )


def main():
    api_key = get_api_key()
    retrieved_at_jst = get_jst_now_str()
    video_data = fetch_video_stats(api_key, VIDEO_IDS)
    write_csv(OUTPUT_CSV, VIDEO_IDS, video_data, retrieved_at_jst)
    print(f"CSVを書き出しました: {OUTPUT_CSV}")
    print(f"取得日時（JST）: {retrieved_at_jst}")


if __name__ == "__main__":
    main()