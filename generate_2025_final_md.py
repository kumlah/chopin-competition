#!/usr/bin/env python
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

JSON_PATH = Path("2025_final.json")
MD_PATH = Path("2025_final.md")


def load_data():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"{JSON_PATH} が見つかりません。パスを確認してください。")

    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("2025_final.json の最上位がリストになっていないようです。")

    return data


def to_int_safe(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main():
    data = load_data()

    # ここでは、以前のスクリプトで作った JSON が
    # videoId / publishedAt / viewCount / likeCount / url
    # を持っている想定で処理します。
    # （キー名が違う場合は、ここを合わせてください）
    for item in data:
        item["viewCount_int"] = to_int_safe(item.get("viewCount"))
        item["likeCount_int"] = to_int_safe(item.get("likeCount"))

    # 再生回数で降順ソート
    sorted_data = sorted(data, key=lambda x: x["viewCount_int"], reverse=True)

    # タイムスタンプ（JST）
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    # 見出し
    lines.append("# ショパコン勝手にYouTube聴衆賞 2025 決勝集計")
    lines.append("")
    lines.append(f"- 最終更新（JST）: {now_jst}")
    lines.append("")
    lines.append("※ 2025_final.json をもとに自動生成されたランキングです。")
    lines.append("")

    # テーブルヘッダ
    lines.append("| 順位 | 動画ID | 投稿日時 | 再生回数 | 高評価数 | URL |")
    lines.append("| ---- | ------ | -------- | -------- | -------- | --- |")

    # テーブル本体
    for rank, item in enumerate(sorted_data, start=1):
        video_id = item.get("videoId", "")
        published_at = item.get("publishedAt", "")
        view_count = item.get("viewCount_int", 0)
        like_count = item.get("likeCount_int", 0)
        url = item.get("url", f"https://www.youtube.com/watch?v={video_id}" if video_id else "")

        # カンマ区切りで見やすく
        view_str = f"{view_count:,}"
        like_str = f"{like_count:,}"

        lines.append(
            f"| {rank} | `{video_id}` | {published_at} | {view_str} | {like_str} | [リンク]({url}) |"
        )

    content = "\n".join(lines)

    with MD_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"{MD_PATH} を更新しました。")


if __name__ == "__main__":
    main()
