# 2025_final.py
import os
import json
import sys
import requests

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


def check_api_key():
    # ① そもそもAPIキーが入っているかチェック
    if (API_KEY is None) or (API_KEY.strip() == "") or (API_KEY == "YOUR_API_KEY_HERE"):
        print("【エラー】APIキーが設定されていません。")
        print("環境変数 YOUTUBE_API_KEY を設定するか、コード内の API_KEY に直接キーを入れてください。")
        sys.exit(1)


def fetch_video_data():
    url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,statistics",
        "id": ",".join(VIDEO_IDS),
        "key": API_KEY,
        "maxResults": 50,
    }

    resp = requests.get(url, params=params)

    # ステータスコードだけ先に出す
    print("HTTP STATUS:", resp.status_code)

    if resp.status_code != 200:
        # ② エラーの中身をできるだけ日本語で説明
        try:
            data = resp.json()
        except Exception:
            print("【エラー】YouTube APIのレスポンスがJSONとして読めませんでした。")
            print("レスポンス本文:", resp.text)
            sys.exit(1)

        err = data.get("error", {})
        msg = err.get("message", "エラーメッセージなし")
        status = err.get("status", "不明")
        reason = None
        if isinstance(err.get("errors"), list) and err["errors"]:
            reason = err["errors"][0].get("reason")

        print("【YouTube API からのエラー】")
        print("  status :", status)
        print("  reason :", reason)
        print("  message:", msg)

        # よくあるパターンを軽く日本語解説
        if reason == "accessNotConfigured":
            print("\n→ YouTube Data API v3 が有効化されていない可能性があります。")
            print("   Google Cloud Console で対象プロジェクトの YouTube Data API v3 を有効にしてください。")
        elif "API key not valid" in msg:
            print("\n→ APIキーが間違っているか、このプロジェクトのキーではない可能性があります。")
        elif reason == "dailyLimitExceeded" or reason == "quotaExceeded":
            print("\n→ クォータ（API使用量）の上限を超えています。時間をおくか、クォータ設定を確認してください。")
        elif reason == "ipRefererBlocked":
            print("\n→ APIキーの『アプリケーション制限』が現在の実行環境と合っていない可能性があります。")

        sys.exit(1)

    # 正常なときはこちら
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


def main():
    check_api_key()

    video_data = fetch_video_data()
    output_file = "2025_final.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

    print(f"{len(video_data)}件の動画情報を {output_file} に保存しました。")


if __name__ == "__main__":
    main()
