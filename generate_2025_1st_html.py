#!/usr/bin/env python
from pathlib import Path

HTML_PATH = Path("2025_1st.html")

# ラウンド設定
ROUND_KEY = "第1"
ROUND_LABEL = "第1ラウンド"

# 年齢基準日
CONTEST_REF_DATE_ISO = "2025-10-01"


def main():
    html = []
    html.append("<!DOCTYPE html>")
    html.append('<html lang="ja">')
    html.append("  <head>")
    html.append('    <meta charset="UTF-8">')
    html.append("    <title>ショパコン勝手にYouTube聴衆賞(非公式) | 2025第1ラウンド集計</title>")
    html.append(
        '    <meta name="description" content="ショパン国際ピアノコンクール2025第1ラウンドのYouTube再生回数を個人的にまとめた非公式メモです。順位と関係なく伸びているコンテスタントの存在を可視化するためのページです。">'
    )
    html.append('    <link rel="preconnect" href="https://fonts.gstatic.com">')
    html.append(
        '    <link rel="preload" href="https://fonts.googleapis.com/css?family=Open+Sans:400,700&display=swap" as="style" type="text/css" crossorigin>'
    )
    html.append('    <meta name="viewport" content="width=device-width, initial-scale=1">')
    html.append('    <meta name="theme-color" content="#157878">')
    html.append(
        '    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
    )
    html.append(
        '    <link rel="stylesheet" href="/chopin-competition/assets/css/style.css">'
    )

    # ★ sticky対応CSS 完全版
    html.append("    <style>")
    html.append("      table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }")
    html.append("      th, td { border: 1px solid #ddd; padding: 0.4rem 0.5rem; }")
    html.append("      th { background: #f0f0f0; }")
    html.append("      tbody tr:nth-child(even) { background: #fafafa; }")
    html.append("      .num-col { text-align: right; white-space: nowrap; }")
    html.append("      .rank-col { text-align: right; white-space: nowrap; }")
    html.append("      .sort-icons { margin-left: 0.25rem; font-size: 0.75rem; white-space: nowrap; }")
    html.append("      .sort-icon { cursor: pointer; margin-left: 0.1rem; color: #888; }")
    html.append("      .sort-icon.active { color: #000; font-weight: bold; }")
    html.append("      .flag-icon { width: 20px; height: 14px; object-fit: cover; vertical-align: middle; }")
    html.append("      .thumb-img { width: 120px; aspect-ratio: 16/9; object-fit: cover; display: block; }")
    html.append("      .muted { color:#777; font-size:0.85rem; }")

    # ★ stickyに必要なスクロールコンテナ
    html.append("      .table-wrap{")
    html.append("        width: 100%;")
    html.append("        height: 80vh;")          # ←固定高さにし、縦スクロールを強制
    html.append("        overflow: auto;")
    html.append("        border: 1px solid #ddd;")
    html.append("        position: relative;")     # stickyの基準を安定
    html.append("      }")

    # ★ ヘッダー行固定（GitHub CSS に負けないよう important）
    html.append("      .table-wrap thead th{")
    html.append("        position: sticky !important;")
    html.append("        top: 0 !important;")
    html.append("        z-index: 5;")
    html.append("        background: #f0f0f0;")
    html.append("      }")

    # ★ 先頭列固定
    html.append("      .table-wrap th:first-child,")
    html.append("      .table-wrap td:first-child{")
    html.append("        position: sticky !important;")
    html.append("        left: 0 !important;")
    html.append("        z-index: 4;")
    html.append("        background: #fff;")
    html.append("      }")

    # ★ 左上セル（行×列の交差点）
    html.append("      .table-wrap thead th:first-child{")
    html.append("        z-index: 6;")
    html.append("        background: #f0f0f0;")
    html.append("      }")

    html.append("    </style>")
    html.append("  </head>")

    html.append("  <body>")
    html.append('    <a id="skip-to-content" href="#content">Skip to the content.</a>')

    html.append('    <header class="page-header" role="banner">')
    html.append(
        '      <h1 class="project-name"><a href="/chopin-competition/" style="color:#fff;">ショパコン勝手にYouTube聴衆賞(非公式)</a></h1>'
    )
    html.append(
        '      <h2 class="project-tagline">ショパン国際ピアノコンクールのYouTube再生数を個人的にまとめた非公式メモです。</h2>'
    )
    html.append("    </header>")

    html.append('    <main id="content" class="main-content" role="main">')

    html.append(f"      <h1>第19回(2025)ショパン国際ピアノコンクール {ROUND_LABEL}再生数ランキング</h1>")
    html.append('      <p id="summary-line" class="muted">読み込み中…</p>')
    html.append('      <p id="unmatched-line" class="muted"></p>')

    # ★ テーブルをスクロール可能ボックスに入れる
    html.append('      <div class="table-wrap">')
    html.append("      <table>")
    html.append("        <thead>")
    html.append("          <tr>")

    # 名前列（先頭列固定対象）
    html.append(
        "            <th>名前"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='pianistSortKey' data-dir='asc' data-type='string'>▲</span>"
        "                <span class='sort-icon' data-key='pianistSortKey' data-dir='desc' data-type='string'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 国
    html.append(
        "            <th style='width:6em;'>国"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='country' data-dir='asc' data-type='string'>▲</span>"
        "                <span class='sort-icon' data-key='country' data-dir='desc' data-type='string'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 年齢
    html.append(
        "            <th style='width:5em;'>年齢"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='age' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='age' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 再生回数
    html.append(
        "            <th style='width:8em;'>再生回数"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='viewCount' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='viewCount' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 高評価数
    html.append(
        "            <th style='width:8em;'>高評価数"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='likeCount' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='likeCount' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 最終結果
    html.append(
        "            <th style='width:8em;'>最終結果"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='finalSortCategory' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='finalSortCategory' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )

    # 動画
    html.append("            <th style='width:11em;'>動画</th>")

    html.append("          </tr>")
    html.append("        </thead>")
    html.append("        <tbody id='ranking-body'></tbody>")
    html.append("      </table>")
    html.append("      </div>")  # end table-wrap

    html.append('      <footer class="site-footer">')
    html.append('          <span class="site-footer-owner">©ショパコン勝手にYouTube聴衆賞(非公式)</span>')
    html.append("      </footer>")
    html.append("    </main>")

    # ★ fetch + 描画 JS（sticky対応そのまま動く）
    html.append("    <script>")
    html.append(f"const ROUND_KEY = {ROUND_KEY!r};")
    html.append(f"const ROUND_LABEL = {ROUND_LABEL!r};")
    html.append(f"const CONTEST_REF_DATE_ISO = {CONTEST_REF_DATE_ISO!r};")

    html.append(r"""
let videos = [];

function toIntSafe(v, def=0){
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : def;
}

function formatNumber(n){
  return (n === null || n === undefined) ? "" : Number(n).toLocaleString("ja-JP");
}

function getFlagFilename(country){
  const mapping = {
    "United States of America": "usa.png",
    "Canada": "canada.png",
    "China": "china.png",
    "Japan": "japan.png",
    "Poland": "poland.png",
    "Malaysia": "malaysia.png",
    "Georgia": "georgia.png",
  };
  return mapping[country] || "";
}

function makePianistSortKey(name){
  if (!name) return "";
  const p = name.trim().split(/\s+/);
  if (p.length === 1) return p[0].toLowerCase();
  const last = p[p.length - 1].toLowerCase();
  const rest = p.slice(0, -1).join(" ").toLowerCase();
  return `${last}, ${rest}`;
}

function determineFinalResult(c){
  const frRaw = c["最終順位"];
  const prize = c["賞"] || "";
  const hasFinal = Boolean(c["ファイナル"]);
  const has3 = Boolean(c["第3"]);
  const has2 = Boolean(c["第2"]);

  if (frRaw !== "" && frRaw !== null && frRaw !== undefined){
    const rankNum = toIntSafe(frRaw, 999);
    return { text: prize ? `${rankNum}位、${prize}` : `${rankNum}位`, category:0, rankNum, prizeOrder: prize ? 0:1 };
  }
  if (hasFinal) return { text:"ファイナリスト", category:1, rankNum:999, prizeOrder:1 };
  if (has3) return { text:"第3ラウンド進出", category:2, rankNum:999, prizeOrder:1 };
  if (has2) return { text:"第2ラウンド進出", category:3, rankNum:999, prizeOrder:1 };
  return { text:"-", category:4, rankNum:999, prizeOrder:1 };
}

function calcAge(birthStr){
  if (!birthStr) return {age:null, birthForSort:""};
  const b = new Date(birthStr);
  if (Number.isNaN(b.getTime())) return {age:null, birthForSort:""};
  const r = new Date(CONTEST_REF_DATE_ISO);
  let age = r.getFullYear() - b.getFullYear();
  const md = r.getMonth() - b.getMonth();
  if (md < 0 || (md===0 && r.getDate() < b.getDate())) age--;
  return { age, birthForSort:birthStr };
}

function renderTable(list){
  const tbody = document.getElementById("ranking-body");
  tbody.innerHTML = "";

  list.forEach(v=>{
    const tr = document.createElement("tr");
    const thumb = `https://img.youtube.com/vi/${v.videoId}/mqdefault.jpg`;
    const link = v.url;

    let countryHtml = v.country;
    if (v.flagPath){
      countryHtml = `<img src="${v.flagPath}" class="flag-icon" alt="${v.country}" title="${v.country}">`;
    }

    tr.innerHTML = `
      <td>${v.pianist}</td>
      <td>${countryHtml}</td>
      <td class="num-col">${v.ageYears ?? ""}</td>
      <td class="num-col">${formatNumber(v.viewCount)}</td>
      <td class="num-col">${formatNumber(v.likeCount)}</td>
      <td class="rank-col">${v.finalResult}</td>
      <td><a href="${link}" target="_blank"><img src="${thumb}" class="thumb-img"></a></td>
    `;
    tbody.appendChild(tr);
  });
}

function sortAndRender(key, dir, type){
  const sorted = [...videos].sort((a,b)=>{

    if (key==="finalSortCategory"){
      if (a.finalSortCategory !== b.finalSortCategory)
        return (dir==="asc") ? a.finalSortCategory-b.finalSortCategory : b.finalSortCategory-a.finalSortCategory;

      if (a.finalSortRankNum !== b.finalSortRankNum)
        return (dir==="asc") ? a.finalSortRankNum-b.finalSortRankNum : b.finalSortRankNum-a.finalSortRankNum;

      if (a.finalSortPrize !== b.finalSortPrize)
        return (dir==="asc") ? a.finalSortPrize-b.finalSortPrize : b.finalSortPrize-a.finalSortPrize;

      return (dir==="asc")
        ? (a.pianistSortKey||"").localeCompare(b.pianistSortKey||"","ja")
        : (b.pianistSortKey||"").localeCompare(a.pianistSortKey||"","ja");
    }

    if (key==="age"){
      const na = (typeof a.ageYears==="number") ? a.ageYears:999;
      const nb = (typeof b.ageYears==="number") ? b.ageYears:999;
      if (na!==nb) return (dir==="asc") ? na-nb : nb-na;

      return (dir==="asc")
        ? (a.birthDate||"").localeCompare(b.birthDate||"","ja")
        : (b.birthDate||"").localeCompare(a.birthDate||"","ja");
    }

    const va = a[key];
    const vb = b[key];
    if (type==="number"){
      const na = Number(va)||0;
      const nb = Number(vb)||0;
      return (dir==="asc") ? na-nb : nb-na;
    }
    return (dir==="asc")
      ? String(va||"").localeCompare(String(vb||""),"ja")
      : String(vb||"").localeCompare(String(va||""),"ja");
  });

  renderTable(sorted);
}

function setupSortIcons(){
  document.querySelectorAll(".sort-icon").forEach(ic=>{
    ic.addEventListener("click",()=>{
      document.querySelectorAll(".sort-icon").forEach(i=>i.classList.remove("active"));
      ic.classList.add("active");
      sortAndRender(ic.dataset.key, ic.dataset.dir, ic.dataset.type);
    });
  });
}

function formatTargetDateJp(iso){
  try{
    const d = new Date(iso);
    const wd = "月火水木金土日"[d.getDay()===0?6:d.getDay()-1];
    return `${d.getFullYear()}年${String(d.getMonth()+1).padStart(2,"0")}月${String(d.getDate()).padStart(2,"0")}日(${wd})`;
  }catch(e){ return iso; }
}

async function loadAndBuild(){
  const [roundRes, compRes] = await Promise.all([
    fetch("all_rounds_view_count.json",{cache:"no-store"}),
    fetch("competitors.json",{cache:"no-store"})
  ]);

  const rd = await roundRes.json();
  const comps = await compRes.json();

  const videosMap = rd.videos || {};
  let unmatched = 0;

  videos = comps.filter(c=>c[ROUND_KEY]).map(c=>{
    const vid = c[ROUND_KEY];
    const st = videosMap[vid];
    if (!st) unmatched++;

    const fr = determineFinalResult(c);
    const flag = getFlagFilename(c["国"]||"");
    const age = calcAge(c["生年月日"]||"");

    return {
      videoId: vid,
      url: `https://www.youtube.com/watch?v=${vid}`,
      pianist: c["名前"]||"",
      pianistSortKey: makePianistSortKey(c["名前"]||""),
      country: c["国"]||"",
      flagPath: flag ? `img/flag/${flag}`:"",
      finalResult: fr.text,
      finalSortCategory: fr.category,
      finalSortRankNum: fr.rankNum,
      finalSortPrize: fr.prizeOrder,
      viewCount: st ? st.viewCount:0,
      likeCount: st ? st.likeCount:0,
      birthDate: age.birthForSort,
      ageYears: age.age
    };
  });

  document.getElementById("summary-line").textContent =
    `集計日: ${formatTargetDateJp(rd.date||"")} ／ 対象動画数: ${videos.length} 本 ／ 年齢は2025年10月1日時点`;

  if (unmatched>0){
    document.getElementById("unmatched-line").textContent =
      `※ ${unmatched} 本は再生数データが見つかりません（0 として表示）。`;
  }

  setupSortIcons();
  const def = document.querySelector('.sort-icon[data-key="viewCount"][data-dir="desc"]');
  if (def) def.classList.add("active");

  sortAndRender("viewCount","desc","number");
}

document.addEventListener("DOMContentLoaded",()=>{
  loadAndBuild().catch(e=>{
    document.getElementById("summary-line").textContent="読み込みエラー";
    console.error(e);
  });
});
""")

    html.append("    </script>")
    html.append("  </body>")
    html.append("</html>")

    HTML_PATH.write_text("\n".join(html), encoding="utf-8")
    print(f"{HTML_PATH} を更新しました。")


if __name__ == "__main__":
    main()
