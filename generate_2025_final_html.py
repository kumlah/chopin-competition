#!/usr/bin/env python
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

JSON_PATH = Path("2025_final.json")
HTML_PATH = Path("2025_final.html")


def load_latest_videos():
    if not JSON_PATH.exists():
        raise FileNotFoundError("{JSON_PATH} が見つかりません。パスを確認してください。")

    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError("2025_final.json の最上位が空でないリストになっていないようです。")

    # date フィールドが "YYYY-MM-DD" 形式で入っている想定
    def parse_date(entry):
        s = entry.get("date", "")
        try:
            return datetime.fromisoformat(s)
        except Exception:
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
    target_date, videos_raw = load_latest_videos()

    # 日付を "YYYY年MM月DD日" に整形
    try:
        dt = datetime.fromisoformat(target_date)
        target_date_jp = dt.strftime("%Y年%m月%d日")
    except Exception:
        target_date_jp = target_date

    # JS に渡す用のクリーンな配列を作る（必要な項目だけ）
    videos = []
    for v in videos_raw:
        videos.append(
            {
                "videoId": v.get("videoId", ""),
                "url": v.get("url", ""),
                "publishedAt": v.get("publishedAt", ""),
                "title": v.get("title", ""),
                "viewCount": to_int_safe(v.get("viewCount")),
                "likeCount": to_int_safe(v.get("likeCount")),
            }
        )

    # JSON を埋め込む。"</script" 問題を避けるため軽くエスケープ
    data_json = json.dumps(videos, ensure_ascii=False)
    data_json_safe = data_json.replace("</", "<\\/")

    html_lines = []

    html_lines.append("<!DOCTYPE html>")
    html_lines.append("<html lang=\"ja\">")
    html_lines.append("<head>")
    html_lines.append("  <meta charset=\"UTF-8\">")
    html_lines.append("  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
    html_lines.append("  <title>ショパコン勝手にYouTube聴衆賞 2025 決勝集計</title>")
    # ちょっとだけ見やすくするCSS
    html_lines.append("  <style>")
    html_lines.append("    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;")
    html_lines.append("           max-width: 1000px; margin: 1.5rem auto; padding: 0 1rem; line-height: 1.6; }")
    html_lines.append("    h1 { font-size: 1.6rem; margin-bottom: 0.5rem; }")
    html_lines.append("    .meta { font-size: 0.9rem; color: #555; margin-bottom: 1rem; }")
    html_lines.append("    .note { font-size: 0.9rem; margin-bottom: 1rem; }")
    html_lines.append("    .controls { margin: 1rem 0; }")
    html_lines.append("    .controls button { margin: 0.2rem; padding: 0.4rem 0.8rem; border-radius: 4px; border: 1px solid #ccc; cursor: pointer; background: #f5f5f5; }")
    html_lines.append("    .controls button.active { background: #333; color: #fff; border-color: #333; }")
    html_lines.append("    table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.9rem; }")
    html_lines.append("    th, td { border: 1px solid #ddd; padding: 0.4rem 0.5rem; }")
    html_lines.append("    th { background: #f0f0f0; }")
    html_lines.append("    tbody tr:nth-child(even) { background: #fafafa; }")
    html_lines.append("    code { font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }")
    html_lines.append("    .rank-col { text-align: right; }")
    html_lines.append("    .num-col { text-align: right; white-space: nowrap; }")
    html_lines.append("    .small { font-size: 0.8rem; color: #777; }")
    html_lines.append("  </style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    html_lines.append("  <h1>ショパコン勝手にYouTube聴衆賞 2025 決勝集計</h1>")
    html_lines.append(f"  <div class=\"meta\">集計日: {target_date_jp} ／ 対象動画数: {len(videos)} 本</div>")

    # 並べ替えボタン
    html_lines.append("  <div class=\"controls\">")
    html_lines.append("    <span class=\"small\">並べ替え: </span>")
    html_lines.append("    <button data-key=\"viewCount\" data-dir=\"desc\" class=\"active\">再生回数 多い順</button>")
    html_lines.append("    <button data-key=\"viewCount\" data-dir=\"asc\">再生回数 少ない順</button>")
    html_lines.append("    <button data-key=\"likeCount\" data-dir=\"desc\">高評価 多い順</button>")
    html_lines.append("    <button data-key=\"likeCount\" data-dir=\"asc\">高評価 少ない順</button>")
    html_lines.append("  </div>")

    # テーブル本体
    html_lines.append("  <table>")
    html_lines.append("    <thead>")
    html_lines.append("      <tr>")
    html_lines.append("        <th style=\"width:3em;\">順位</th>")
    html_lines.append("        <th>ピアニスト / タイトル</th>")
    html_lines.append("        <th style=\"width:8em;\">動画ID</th>")
    html_lines.append("        <th style=\"width:12em;\">投稿日 (UTC)</th>")
    html_lines.append("        <th style=\"width:8em;\">再生回数</th>")
    html_lines.append("        <th style=\"width:8em;\">高評価数</th>")
    html_lines.append("        <th style=\"width:5em;\">URL</th>")
    html_lines.append("      </tr>")
    html_lines.append("    </thead>")
    html_lines.append("    <tbody id=\"ranking-body\">")
    html_lines.append("      <!-- JavaScript で埋め込み -->")
    html_lines.append("    </tbody>")
    html_lines.append("  </table>")

    # データとスクリプト
    html_lines.append("  <script>")
    html_lines.append(f"    const videos = {data_json_safe};")
    html_lines.append("")
    html_lines.append("    function formatNumber(n) {")
    html_lines.append("      return n.toLocaleString('ja-JP');")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    function renderTable(list) {")
    html_lines.append("      const tbody = document.getElementById('ranking-body');")
    html_lines.append("      tbody.innerHTML = '';")
    html_lines.append("      list.forEach((v, index) => {")
    html_lines.append("        const tr = document.createElement('tr');")
    html_lines.append("        tr.innerHTML = `")
    html_lines.append("          <td class=\"rank-col\">${index + 1}</td>")
    html_lines.append("          <td>${v.title}</td>")
    html_lines.append("          <td><code>${v.videoId}</code></td>")
    html_lines.append("          <td>${v.publishedAt}</td>")
    html_lines.append("          <td class=\"num-col\">${formatNumber(v.viewCount)}</td>")
    html_lines.append("          <td class=\"num-col\">${formatNumber(v.likeCount)}</td>")
    html_lines.append("          <td><a href=\"${v.url}\" target=\"_blank\" rel=\"noopener noreferrer\">リンク</a></td>")
    html_lines.append("        `;")
    html_lines.append("        tbody.appendChild(tr);")
    html_lines.append("      });")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    function sortAndRender(key, dir) {")
    html_lines.append("      const sorted = [...videos].sort((a, b) => {")
    html_lines.append("        const va = a[key] ?? 0;")
    html_lines.append("        const vb = b[key] ?? 0;")
    html_lines.append("        if (dir === 'asc') {")
    html_lines.append("          return va - vb;")
    html_lines.append("        } else {")
    html_lines.append("          return vb - va;")
    html_lines.append("        }")
    html_lines.append("      });")
    html_lines.append("      renderTable(sorted);")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    function setupControls() {")
    html_lines.append("      const buttons = document.querySelectorAll('.controls button');")
    html_lines.append("      buttons.forEach(btn => {")
    html_lines.append("        btn.addEventListener('click', () => {")
    html_lines.append("          buttons.forEach(b => b.classList.remove('active'));")
    html_lines.append("          btn.classList.add('active');")
    html_lines.append("          const key = btn.getAttribute('data-key');")
    html_lines.append("          const dir = btn.getAttribute('data-dir');")
    html_lines.append("          sortAndRender(key, dir);")
    html_lines.append("        });")
    html_lines.append("      });")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    // 初期表示: 再生回数 多い順")
    html_lines.append("    document.addEventListener('DOMContentLoaded', () => {")
    html_lines.append("      setupControls();")
    html_lines.append("      sortAndRender('viewCount', 'desc');")
    html_lines.append("    });")
    html_lines.append("  </script>")
    html_lines.append("</body>")
    html_lines.append("</html>")

    html_content = "\n".join(html_lines)

    with HTML_PATH.open("w", encoding="utf-8", newline="\n") as f:
        f.write(html_content)

    print(f"{HTML_PATH} を更新しました。")


if __name__ == "__main__":
    main()
