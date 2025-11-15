#!/usr/bin/env python
import json
from datetime import datetime
from pathlib import Path

JSON_PATH = Path("2025_final.json")
HTML_PATH = Path("2025_final.html")
COMPETITORS_PATH = Path("competitors.json")


def load_latest_videos():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"{JSON_PATH} が見つかりません。パスを確認してください。")

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


def load_competitors():
    """
    competitors.json をそのまま読み込む。
    期待フォーマット（実データ）:
    [
      {
        "名前": "Eric Lu",
        "国": "United States of America",
        "最終順位": 1,
        "賞": "",
        "ファイナル": "〇",
        "第3": "",
        "第2": "",
        "第1": ""
      },
      ...
    ]
    """
    if not COMPETITORS_PATH.exists():
        # 無くてもエラーにはせず、空リスト
        return []

    with COMPETITORS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("competitors.json の最上位はリスト形式を想定しています。")

    return data


def to_int_safe(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main():
    target_date, videos_raw = load_latest_videos()
    competitors_raw = load_competitors()

    # 日付を "YYYY年MM月DD日(曜)" に整形
    try:
        dt = datetime.fromisoformat(target_date)
        weekday_ja = "月火水木金土日"[dt.weekday()]  # 0=月, 6=日
        target_date_jp = dt.strftime("%Y年%m月%d日") + f"({weekday_ja})"
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
    videos_json = json.dumps(videos, ensure_ascii=False)
    videos_json_safe = videos_json.replace("</", "<\\/")

    competitors_json = json.dumps(competitors_raw, ensure_ascii=False)
    competitors_json_safe = competitors_json.replace("</", "<\\/")

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
    html_lines.append("    h2 { font-size: 1.3rem; margin-top: 2rem; margin-bottom: 0.5rem; }")
    html_lines.append("    .meta { font-size: 0.9rem; color: #555; margin-bottom: 1rem; }")
    html_lines.append("    .note { font-size: 0.9rem; margin-bottom: 1rem; }")
    html_lines.append("    table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.9rem; }")
    html_lines.append("    th, td { border: 1px solid #ddd; padding: 0.4rem 0.5rem; }")
    html_lines.append("    th { background: #f0f0f0; }")
    html_lines.append("    tbody tr:nth-child(even) { background: #fafafa; }")
    html_lines.append("    code { font-family: SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }")
    html_lines.append("    .rank-col { text-align: right; }")
    html_lines.append("    .num-col { text-align: right; white-space: nowrap; }")
    html_lines.append("    .small { font-size: 0.8rem; color: #777; }")
    html_lines.append("    .sort-icons { margin-left: 0.25rem; white-space: nowrap; font-size: 0.75rem; }")
    html_lines.append("    .sort-icon { cursor: pointer; margin-left: 0.1rem; color: #888; }")
    html_lines.append("    .sort-icon.active { color: #000; font-weight: bold; }")
    html_lines.append("  </style>")
    html_lines.append("</head>")
    html_lines.append("<body>")
    html_lines.append("  <h1>ショパコン勝手にYouTube聴衆賞 2025 決勝集計</h1>")
    html_lines.append(f"  <div class=\"meta\">集計日: {target_date_jp} ／ 対象動画数: {len(videos)} 本</div>")
    html_lines.append("  <div class=\"note\">※ 2025_final.json をもとに自動生成された YouTube ランキングです。</div>")

    # ① YouTube ランキングテーブル
    html_lines.append("  <h2>YouTube 再生数ランキング（決勝）</h2>")
    html_lines.append("  <table>")
    html_lines.append("    <thead>")
    html_lines.append("      <tr>")
    html_lines.append("        <th style=\"width:3em;\">順位</th>")
    html_lines.append("        <th>ピアニスト / タイトル</th>")
    html_lines.append("        <th style=\"width:8em;\">動画ID</th>")
    html_lines.append("        <th style=\"width:12em;\">投稿日 (UTC)</th>")
    html_lines.append(
        "        <th style=\"width:8em;\">再生回数"
        "          <span class=\"sort-icons\">"
        "            <span class=\"sort-icon\" data-key=\"viewCount\" data-dir=\"asc\" title=\"再生回数 少ない順\">▲</span>"
        "            <span class=\"sort-icon\" data-key=\"viewCount\" data-dir=\"desc\" title=\"再生回数 多い順\">▼</span>"
        "          </span>"
        "        </th>"
    )
    html_lines.append(
        "        <th style=\"width:8em;\">高評価数"
        "          <span class=\"sort-icons\">"
        "            <span class=\"sort-icon\" data-key=\"likeCount\" data-dir=\"asc\" title=\"高評価 少ない順\">▲</span>"
        "            <span class=\"sort-icon\" data-key=\"likeCount\" data-dir=\"desc\" title=\"高評価 多い順\">▼</span>"
        "          </span>"
        "        </th>"
    )
    html_lines.append("        <th style=\"width:5em;\">URL</th>")
    html_lines.append("      </tr>")
    html_lines.append("    </thead>")
    html_lines.append("    <tbody id=\"ranking-body\">")
    html_lines.append("      <!-- JavaScript で埋め込み -->")
    html_lines.append("    </tbody>")
    html_lines.append("  </table>")

    # ② 公式結果テーブル（competitors.json）
    html_lines.append("  <h2>公式結果（ファイナル出場者一覧）</h2>")
    html_lines.append("  <div class=\"note small\">※ competitors.json の内容をそのまま反映しています（最終順位のない人は順不同で表示）。</div>")
    html_lines.append("  <table>")
    html_lines.append("    <thead>")
    html_lines.append("      <tr>")
    html_lines.append("        <th style=\"width:3em;\">順位</th>")
    html_lines.append("        <th>名前</th>")
    html_lines.append("        <th style=\"width:10em;\">国</th>")
    html_lines.append("        <th style=\"width:8em;\">賞</th>")
    html_lines.append("        <th style=\"width:5em;\">ファイナル</th>")
    html_lines.append("        <th style=\"width:4em;\">第3</th>")
    html_lines.append("        <th style=\"width:4em;\">第2</th>")
    html_lines.append("        <th style=\"width:4em;\">第1</th>")
    html_lines.append("      </tr>")
    html_lines.append("    </thead>")
    html_lines.append("    <tbody id=\"competitors-body\">")
    html_lines.append("      <!-- JavaScript で埋め込み -->")
    html_lines.append("    </tbody>")
    html_lines.append("  </table>")

    # データとスクリプト
    html_lines.append("  <script>")
    html_lines.append(f"    const videos = {videos_json_safe};")
    html_lines.append(f"    const competitors = {competitors_json_safe};")
    html_lines.append("")
    html_lines.append("    function formatNumber(n) {")
    html_lines.append("      return n.toLocaleString('ja-JP');")
    html_lines.append("    }")
    html_lines.append("")
    # YouTube ランキング描画
    html_lines.append("    function renderVideoTable(list) {")
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
    html_lines.append("    function sortAndRenderVideos(key, dir) {")
    html_lines.append("      const sorted = [...videos].sort((a, b) => {")
    html_lines.append("        const va = a[key] ?? 0;")
    html_lines.append("        const vb = b[key] ?? 0;")
    html_lines.append("        if (dir === 'asc') {")
    html_lines.append("          return va - vb;")
    html_lines.append("        } else {")
    html_lines.append("          return vb - va;")
    html_lines.append("        }")
    html_lines.append("      });")
    html_lines.append("      renderVideoTable(sorted);")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    function setupSortIcons() {")
    html_lines.append("      const icons = document.querySelectorAll('.sort-icon');")
    html_lines.append("      icons.forEach(icon => {")
    html_lines.append("        icon.addEventListener('click', () => {")
    html_lines.append("          const key = icon.getAttribute('data-key');")
    html_lines.append("          const dir = icon.getAttribute('data-dir');")
    html_lines.append("          icons.forEach(i => i.classList.remove('active'));")
    html_lines.append("          icon.classList.add('active');")
    html_lines.append("          sortAndRenderVideos(key, dir);")
    html_lines.append("        });")
    html_lines.append("      });")
    html_lines.append("    }")
    html_lines.append("")
    # competitors.json テーブル描画
    html_lines.append("    function renderCompetitorsTable(data) {")
    html_lines.append("      const tbody = document.getElementById('competitors-body');")
    html_lines.append("      tbody.innerHTML = '';")
    html_lines.append("")
    html_lines.append("      // 最終順位のある人を先に、無い人を後ろにする")
    html_lines.append("      const sorted = [...data].sort((a, b) => {")
    html_lines.append("        const aRankRaw = a['最終順位'];")
    html_lines.append("        const bRankRaw = b['最終順位'];")
    html_lines.append("        const aRank = parseInt(aRankRaw, 10);")
    html_lines.append("        const bRank = parseInt(bRankRaw, 10);")
    html_lines.append("        const aNaN = Number.isNaN(aRank);")
    html_lines.append("        const bNaN = Number.isNaN(bRank);")
    html_lines.append("        if (aNaN && bNaN) return 0;")
    html_lines.append("        if (aNaN) return 1;  // 順位なしは後ろ")
    html_lines.append("        if (bNaN) return -1;")
    html_lines.append("        return aRank - bRank;")
    html_lines.append("      });")
    html_lines.append("")
    html_lines.append("      sorted.forEach((c) => {")
    html_lines.append("        const rankRaw = c['最終順位'];")
    html_lines.append("        const rankText = (rankRaw === '' || rankRaw === null || typeof rankRaw === 'undefined')")
    html_lines.append("          ? '—'"
    html_lines.append("          : rankRaw;")
    html_lines.append("        const tr = document.createElement('tr');")
    html_lines.append("        tr.innerHTML = `")
    html_lines.append("          <td class=\"rank-col\">${rankText}</td>")
    html_lines.append("          <td>${c['名前'] ?? ''}</td>")
    html_lines.append("          <td>${c['国'] ?? ''}</td>")
    html_lines.append("          <td>${c['賞'] ?? ''}</td>")
    html_lines.append("          <td>${c['ファイナル'] ?? ''}</td>")
    html_lines.append("          <td>${c['第3'] ?? ''}</td>")
    html_lines.append("          <td>${c['第2'] ?? ''}</td>")
    html_lines.append("          <td>${c['第1'] ?? ''}</td>")
    html_lines.append("        `;")
    html_lines.append("        tbody.appendChild(tr);")
    html_lines.append("      });")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    // 初期表示")
    html_lines.append("    document.addEventListener('DOMContentLoaded', () => {")
    html_lines.append("      setupSortIcons();")
    html_lines.append("      const defaultIcon = document.querySelector('.sort-icon[data-key=\"viewCount\"][data-dir=\"desc\"]');")
    html_lines.append("      if (defaultIcon) {")
    html_lines.append("        defaultIcon.classList.add('active');")
    html_lines.append("      }")
    html_lines.append("      sortAndRenderVideos('viewCount', 'desc');")
    html_lines.append("      renderCompetitorsTable(competitors);")
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
