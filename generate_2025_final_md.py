#!/usr/bin/env python
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

JSON_PATH = Path("2025_final.json")
MD_PATH = Path("2025_final.md")


def load_latest_videos():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"{JSON_PATH} が見つかりません。パスを確認してください。")

    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError("2025_final.json の最上位が空でないリストになっていないようです。")

    # date フィールドが "YYYY-MM-DD" 形式で入っている想定
    # 複数日分が溜まったときに一番新しい日付を選ぶ
    def parse_date(entry):
        s = entry.get("date", "")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            # フォーマットがおかしい時は最小値扱い
            return datetime.min

    latest_entry = max(data, key=parse_date)

    videos = latest_entry.get("videos", [])
    if not isinstance(videos, list):
        raise ValueError("latest_entry['videos'] がリストではないようです。")

    latest_date = latest_entry.get("date", "")

    return latest_date, videos


def to_int_safe(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main():
    target_date, videos = load_latest_videos()

    # viewCount / likeCount を int 化しておく
    for v in videos:
        v["viewCount_int"] = to_int_safe(v.get("viewCount"))
        v["likeCount_int"] = to_int_safe(v.get("likeCount"))

    # 再生回数で降順ソート
    sorted_videos = sorted(videos, key=lambda x: x["viewCount_int"], reverse=True)

    # タイムスタンプ（JST）
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")

    lines = []

    # 見出し
    lines.append("# ショパコン勝手にYouTube聴衆賞 2025 決勝集計")
    lines.append("")
    lines.append(f"- 集計日: {target_date} 時点")
    lines.append(f"- 最終更新（JST）: {now_jst}")
    lines.append(f"- 対象動画数: {len(sorted_videos)} 本")
    lines.append("")
    lines.append("※ 2025_final.json をもとに自動生成されたランキングです。")
    lines.append("")

    # テーブルヘッダ
    lines.append("| 順位 | ピアニスト / タイトル | 動画ID | 投稿日時 (UTC) | 再生回数 | 高評価数 | URL |")
    lines.append("| ---- | --------------------- | ------ | -------------- | -------- | -------- | --- |")

    # テーブル本体
    for rank, v in enumerate(sorted_videos, start=1):
        video_id = v.get("videoId", "")
        url = v.get("url", f"https://www.youtube.com/watch?v={video_id}" if video_id else "")
        published_at = v.get("publishedAt", "")
        title = v.get("title", "")
        view_count = v.get("viewCount_int", 0)
        like_count = v.get("likeCount_int", 0)

        view_str = f"{view_count:,}"
        like_str = f"{like_count:,}"

        lines.append(
            f"| {rank} | {title} | `{video_id}` | {published_at} | {view_str} | {like_str} | [リンク]({url}) |"
        )

    content = "\n".join(lines)

    with MD_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"{MD_PATH} を更新しました。")


if __name__ == "__main__":
    main()
