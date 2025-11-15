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


def find_competitor_for_title(title: str, competitors: list[dict]) -> dict | None:
    """
    動画タイトルに含まれる名前（大文字小文字無視）を手がかりに competitor を1件返す。
    最初にマッチしたものを採用。
    """
    if not title:
        return None

    title_lower = title.lower()
    for comp in competitors:
        name = comp.get("名前")
        if not name:
            continue
        if name.lower() in title_lower:
            return comp

    return None


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

    # JS に渡す用のクリーンな配列を作る
    videos = []
    unmatched_count = 0

    for v in videos_raw:
        title = v.get("title", "") or ""
        comp = find_competitor_for_title(title, competitors_raw)

        if comp is None:
            unmatched_count += 1

        # competitors.json 由来の情報（見つからなければ空文字）
        pianist = comp.get("名前", "") if comp else ""
        country = comp.get("国", "") if comp else ""
        final_rank_raw = comp.get("最終順位", "") if comp else ""
        if final_rank_raw in (None, ""):
            final_rank = ""
            final_rank_num = 999  # 順位なしはソート時に末尾へ
        else:
            final_rank = str(final_rank_raw)
            final_rank_num = to_int_safe(final_rank_raw, 999)
        prize = comp.get("賞", "") if comp else ""

        videos.append(
            {
                "videoId": v.get("videoId", ""),
                "url": v.get("url", ""),
                "publishedAt": v.get("publishedAt", ""),
                "rawTitle": title,  # デバッグ・将来用（表には出さない）
                "viewCount": to_int_safe(v.get("viewCount")),
                "likeCount": to_int_safe(v.get("likeCount")),
                "pianist": pianist,
                "country": country,
                "finalRank": final_rank,
                "finalRankNum": final_rank_num,
                "prize": prize,
            }
        )

    # JSON を埋め込む。"</script" 問題を避けるため軽くエスケープ
    videos_json = json.dumps(videos, ensure_ascii=False)
    videos_json_safe = videos_json.replace("</", "<\\/")

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
    html_lines.append(
        f"  <div class=\"meta\">集計日: {target_date_jp} ／ 対象動画数: {len(videos)} 本</div>"
    )
    html_lines.append(
        "  <div class=\"note\">※ 2025_final.json と competitors.json をもとに、動画タイトルに含まれる名前から自動的に出演者情報を紐づけています。</div>"
    )
    if unmatched_count > 0:
        html_lines.append(
            f"  <div class=\"note small\">※ 注意: {unmatched_count} 本の動画はタイトルから出演者名を特定できませんでした（名前・国・順位などが空欄になっています）。</div>"
        )

    # テーブル本体（タイトル・GitHub上の順位列などは出さない）
    html_lines.append("  <table>")
    html_lines.append("    <thead>")
    html_lines.append("      <tr>")
    html_lines.append("        <th>名前</th>")
    html_lines.append("        <th style=\"width:10em;\">国</th>")
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
    html_lines.append(
        "        <th style=\"width:6em;\">最終順位"
        "          <span class=\"sort-icons\">"
        "            <span class=\"sort-icon\" data-key=\"finalRankNum\" data-dir=\"asc\" title=\"最終順位 昇順\">▲</span>"
        "            <span class=\"sort-icon\" data-key=\"finalRankNum\" data-dir=\"desc\" title=\"最終順位 降順\">▼</span>"
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

    # データとスクリプト
    html_lines.append("  <script>")
    html_lines.append(f"    const videos = {videos_json_safe};")
    html_lines.append("")
    html_lines.append("    function formatNumber(n) {")
    html_lines.append("      return n.toLocaleString('ja-JP');")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    function renderTable(list) {")
    html_lines.append("      const tbody = document.getElementById('ranking-body');")
    html_lines.append("      tbody.innerHTML = '';")
    html_lines.append("      list.forEach((v) => {")
    html_lines.append("        const finalRank = v.finalRank && v.finalRank !== '' ? v.finalRank : '—';")
    html_lines.append("        const tr = document.createElement('tr');")
    html_lines.append("        tr.innerHTML = `")
    html_lines.append("          <td>${v.pianist || ''}</td>")
    html_lines.append("          <td>${v.country || ''}</td>")
    html_lines.append("          <td class=\"num-col\">${formatNumber(v.viewCount)}</td>")
    html_lines.append("          <td class=\"num-col\">${formatNumber(v.likeCount)}</td>")
    html_lines.append("          <td class=\"rank-col\">${finalRank}</td>")
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
    html_lines.append("    function setupSortIcons() {")
    html_lines.append("      const icons = document.querySelectorAll('.sort-icon');")
    html_lines.append("      icons.forEach(icon => {")
    html_lines.append("        icon.addEventListener('click', () => {")
    html_lines.append("          const key = icon.getAttribute('data-key');")
    html_lines.append("          const dir = icon.getAttribute('data-dir');")
    html_lines.append("          icons.forEach(i => i.classList.remove('active'));")
    html_lines.append("          icon.classList.add('active');")
    html_lines.append("          sortAndRender(key, dir);")
    html_lines.append("        });")
    html_lines.append("      });")
    html_lines.append("    }")
    html_lines.append("")
    html_lines.append("    // 初期表示: 再生回数 多い順（▼ をデフォルトアクティブ）")
    html_lines.append("    document.addEventListener('DOMContentLoaded', () => {")
    html_lines.append("      setupSortIcons();")
    html_lines.append("      const defaultIcon = document.querySelector('.sort-icon[data-key=\"viewCount\"][data-dir=\"desc\"]');")
    html_lines.append("      if (defaultIcon) {")
    html_lines.append("        defaultIcon.classList.add('active');")
    html_lines.append("      }")
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
