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

    return latest_entry.get("date", ""), videos


def load_competitors():
    if not COMPETITORS_PATH.exists():
        return []

    with COMPETITORS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("competitors.json の最上位はリスト形式を想定しています。")

    return data


def to_int_safe(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def make_pianist_sort_key(name: str) -> str:
    if not name:
        return ""
    parts = name.strip().split()
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].lower()
    last = parts[-1].lower()
    rest = " ".join(parts[:-1]).lower()
    return f"{last}, {rest}"


def determine_final_result(comp):
    """
    A案：
      このファイナルページに登場するのは「ファイナルに動画がある人だけ」。
      しかし最終結果の表記は指定ルールに従って判定する。
    """

    fr_raw = comp.get("最終順位", "")
    prize = comp.get("賞", "") or ""
    has_final = bool(comp.get("ファイナル"))
    has_3 = bool(comp.get("第3"))
    has_2 = bool(comp.get("第2"))

    # 1) 最終順位あり
    if fr_raw not in ("", None):
        rank_num = to_int_safe(fr_raw, 999)
        if prize:
            text = f"{rank_num}位、{prize}"
        else:
            text = f"{rank_num}位"
        category = 0   # 最上位
        prize_order = 0 if prize else 1
        return text, category, rank_num, prize_order

    # 2) ファイナル進出（動画ある人）
    if has_final:
        text = "ファイナル進出"
        category = 1
        return text, category, 999, 1

    # 3) 第3進出
    if has_3:
        text = "第3ラウンド進出"
        category = 2
        return text, category, 999, 1

    # 4) 第2進出
    if has_2:
        text = "第2ラウンド進出"
        category = 3
        return text, category, 999, 1

    # 5) 第1のみ or 不明
    text = "-"
    category = 4
    return text, category, 999, 1


def main():
    target_date, videos_raw = load_latest_videos()
    competitors_raw = load_competitors()

    # videoId → stats
    stats_map = {}
    for v in videos_raw:
        vid = v.get("videoId") or v.get("id")
        if vid:
            stats_map[vid] = v

    # 日付表記
    try:
        dt = datetime.fromisoformat(target_date)
        weekday_ja = "月火水木金土日"[dt.weekday()]
        target_date_jp = dt.strftime("%Y年%m月%d日") + f"({weekday_ja})"
    except Exception:
        target_date_jp = target_date

    videos = []
    unmatched = 0

    # A案：ファイナル動画がある人だけ
    finalists = [c for c in competitors_raw if c.get("ファイナル")]

    for comp in finalists:
        video_id = comp.get("ファイナル")
        stats = stats_map.get(video_id)
        if stats is None:
            unmatched += 1
            stats = {}

        pianist = comp.get("名前", "") or ""
        country = comp.get("国", "") or ""

        # 最終結果ロジック
        result_text, cat, rank_num, prize_order = determine_final_result(comp)

        # 姓ソートキー
        sort_key = make_pianist_sort_key(pianist)

        videos.append(
            {
                "videoId": video_id,
                "url": stats.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "publishedAt": stats.get("publishedAt", ""),
                "viewCount": to_int_safe(stats.get("viewCount")),
                "likeCount": to_int_safe(stats.get("likeCount")),
                "pianist": pianist,
                "pianistSortKey": sort_key,
                "country": country,
                "finalResult": result_text,
                "finalSortCategory": cat,
                "finalSortRankNum": rank_num,
                "finalSortPrize": prize_order,
            }
        )

    videos_json = json.dumps(videos, ensure_ascii=False).replace("</", "<\\/")
    html = []

    html.append("<!DOCTYPE html>")
    html.append('<html lang="ja">')
    html.append("  <head>")
    html.append('    <meta charset="UTF-8">')
    html.append("    <title>2025ショパコン ファイナル集計</title>")
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1">')

    html.append(
        '    <link rel="stylesheet" href="/chopin-competition/assets/css/style.css">'
    )

    html.append("    <style>")
    html.append(
        "      table{ width:100%; border-collapse:collapse; margin-top:1rem; font-size:0.9rem; }"
    )
    html.append("      th,td{ border:1px solid #ccc; padding:0.4rem; }")
    html.append("      th{ background:#f0f0f0; }")
    html.append(
        "      .sort-icon{ cursor:pointer; margin-left:0.3rem; color:#555; }"
    )
    html.append("      .sort-icon.active{ font-weight:bold; color:#000; }")
    html.append(
        "      .thumb-img{ width:120px; aspect-ratio:16/9; object-fit:cover; }"
    )
    html.append("    </style>")

    html.append("  </head>")
    html.append("  <body>")

    html.append('    <header class="page-header">')
    html.append(
        '      <h1 class="project-name"><a href="/chopin-competition/" style="color:white;">ショパコン勝手にYouTube聴衆賞(非公式)</a></h1>'
    )
    html.append(
        '      <h2 class="project-tagline">ファイナルの再生回数を集計しています</h2>'
    )
    html.append("    </header>")

    html.append('    <main id="content" class="main-content">')
    if unmatched:
        html.append(
            f'<p style="color:#777;">※{unmatched}件の動画で再生数が取得できませんでした。</p>'
        )

    html.append("<h1>第19回(2025) ショパンコンクール ファイナル再生数</h1>")
    html.append(f"<p>集計日: {target_date_jp} ／ 対象: {len(videos)} 名</p>")

    html.append("      <table>")
    html.append("        <thead>")
    html.append("          <tr>")

    # 名前
    html.append(
        "            <th>名前"
        "              <span class='sort-icon' data-key='pianistSortKey' data-dir='asc' data-type='string'>▲</span>"
        "              <span class='sort-icon' data-key='pianistSortKey' data-dir='desc' data-type='string'>▼</span>"
        "            </th>"
    )

    # 再生回数
    html.append(
        "            <th>再生回数"
        "              <span class='sort-icon' data-key='viewCount' data-dir='asc' data-type='number'>▲</span>"
        "              <span class='sort-icon' data-key='viewCount' data-dir='desc' data-type='number'>▼</span>"
        "            </th>"
    )

    # 高評価数
    html.append(
        "            <th>高評価数"
        "              <span class='sort-icon' data-key='likeCount' data-dir='asc' data-type='number'>▲</span>"
        "              <span class='sort-icon' data-key='likeCount' data-dir='desc' data-type='number'>▼</span>"
        "            </th>"
    )

    # 最終結果（名称変更済）
    html.append(
        "            <th>最終結果"
        "              <span class='sort-icon' data-key='finalSortCategory' data-dir='asc' data-type='number'>▲</span>"
        "              <span class='sort-icon' data-key='finalSortCategory' data-dir='desc' data-type='number'>▼</span>"
        "            </th>"
    )

    # 動画
    html.append("            <th>動画</th>")

    html.append("          </tr>")
    html.append("        </thead>")
    html.append("        <tbody id='ranking-body'></tbody>")
    html.append("      </table>")

    html.append("      <footer class='site-footer'>©ショパコン勝手にYouTube聴衆賞(非公式)</footer>")
    html.append("    </main>")

    # JS
    html.append("    <script>")
    html.append(f"const videos = {videos_json};")

    html.append(
        r"""
function formatNumber(n){
  if(n===null || n===undefined) return "";
  return n.toLocaleString('ja-JP');
}

function renderTable(list){
  const tbody = document.getElementById('ranking-body');
  tbody.innerHTML = "";

  list.forEach(v=>{
    const videoUrl = v.url || `https://www.youtube.com/watch?v=${v.videoId}`;
    const thumb = `https://img.youtube.com/vi/${v.videoId}/mqdefault.jpg`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${v.pianist}</td>
      <td>${formatNumber(v.viewCount)}</td>
      <td>${formatNumber(v.likeCount)}</td>
      <td>${v.finalResult}</td>
      <td>
        <a href="${videoUrl}" target="_blank" rel="noopener noreferrer">
          <img src="${thumb}" class="thumb-img">
        </a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function sortList(key,dir,type){
  const sorted = [...videos].sort((a,b)=>{
    let va = a[key], vb = b[key];

    // 最終結果ソートの場合は複合キーを優先
    if(key==="finalSortCategory"){
      const A = [a.finalSortCategory, a.finalSortRankNum, a.finalSortPrize, a.pianistSortKey];
      const B = [b.finalSortCategory, b.finalSortRankNum, b.finalSortPrize, b.pianistSortKey];
      return dir==="asc"
        ? A.toString().localeCompare(B.toString(),"ja")
        : B.toString().localeCompare(A.toString(),"ja");
    }

    if(type==="number"){
      va = parseFloat(va)||0;
      vb = parseFloat(vb)||0;
      return dir==="asc" ? va - vb : vb - va;
    }else{
      return dir==="asc"
        ? String(va).localeCompare(String(vb),"ja")
        : String(vb).localeCompare(String(va),"ja");
    }
  });

  renderTable(sorted);
}

function initSort(){
  const icons = document.querySelectorAll(".sort-icon");
  icons.forEach(ic=>{
    ic.addEventListener("click",()=>{
      icons.forEach(i=>i.classList.remove("active"));
      ic.classList.add("active");

      const key = ic.getAttribute("data-key");
      const dir = ic.getAttribute("data-dir");
      const type = ic.getAttribute("data-type");
      sortList(key,dir,type);
    });
  });
}

// 初期表示：再生回数降順
document.addEventListener("DOMContentLoaded",()=>{
  initSort();
  sortList("viewCount","desc","number");
});
"""
    )

    html.append("    </script>")
    html.append("  </body>")
    html.append("</html>")

    HTML_PATH.write_text("\n".join(html), encoding="utf-8")
    print(f"{HTML_PATH} を更新しました。")


if __name__ == "__main__":
    main()
