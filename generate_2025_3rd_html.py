#!/usr/bin/env python
import json
from datetime import datetime
from pathlib import Path

JSON_PATH = Path("2025_3rd.json")
HTML_PATH = Path("2025_3rd.html")
COMPETITORS_PATH = Path("competitors.json")

# ★ コンクール年齢基準日（第19回ショパンコンクール：2025年10月1日時点）
CONTEST_REF_DATE = datetime(2025, 10, 1)


def load_latest_videos():
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"{JSON_PATH} が見つかりません。パスを確認してください。")

    with JSON_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or not data:
        raise ValueError("2025_3rd.json の最上位が空でないリストになっていないようです。")

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


def get_flag_filename(country: str) -> str:
    """国名→国旗ファイル名（無い国は '' を返す）"""
    mapping = {
        "United States of America": "usa.png",
        "Canada": "canada.png",
        "China": "china.png",
        "Japan": "japan.png",
        "Poland": "poland.png",
        "Malaysia": "malaysia.png",
        "Georgia": "georgia.png",
    }
    return mapping.get(country, "")


def make_pianist_sort_key(name: str) -> str:
    """
    姓でソートするためのキーを作る。
    - スペース区切りで分割
    - 最後の単語を姓とみなす
    - 'lastname, other parts' を小文字で返す
    """
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
    最終結果テキストとソート用キーを決める。
    ルール:
      1) 最終順位あり        → 「n位」「n位、◯◯賞」
      2) 最終順位空 & ファイナルあり → 「ファイナリスト」
      3) ファイナル空 & 第3あり     → 「第3ラウンド進出」
      4) 第3空 & 第2あり           → 「第2ラウンド進出」
      5) それ以外                  → 「-」
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
        category = 0
        prize_order = 0 if prize else 1
        return text, category, rank_num, prize_order

    # 2) ファイナリスト
    if has_final:
        text = "ファイナリスト"
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

    # 5) それ以外（第1のみなど）
    text = "-"
    category = 4
    return text, category, 999, 1


def calc_age_from_birthdate(birth_str: str, ref_dt: datetime):
    """
    生年月日文字列(YYYY-MM-DD)と基準日(ref_dt)から年齢(歳)を返す。
    パースできなければ (None, '') を返す。
    """
    if not birth_str or not ref_dt:
        return None, ""
    try:
        birth = datetime.fromisoformat(birth_str).date()
    except Exception:
        return None, ""
    ref_date = ref_dt.date()
    age = ref_date.year - birth.year
    if (ref_date.month, ref_date.day) < (birth.month, birth.day):
        age -= 1
    return age, birth_str


def main():
    target_date, videos_raw = load_latest_videos()
    competitors_raw = load_competitors()

    # 2025_3rd.json 側の統計: videoId → 統計 dict
    stats_map = {}
    for v in videos_raw:
        vid = v.get("videoId") or v.get("id")
        if vid:
            stats_map[vid] = v

    # 日付を "YYYY年MM月DD日(曜)" に整形（集計日表示用）
    dt = None
    try:
        dt = datetime.fromisoformat(target_date)
        weekday_ja = "月火水木金土日"[dt.weekday()]
        target_date_jp = dt.strftime("%Y年%m月%d日") + f"({weekday_ja})"
    except Exception:
        target_date_jp = target_date

    videos = []
    unmatched_count = 0  # 統計が見つからなかった第3ラウンド動画の本数

    # ★ 第3ラウンド動画IDが入っている人だけ対象にする
    third_rounders = [c for c in competitors_raw if c.get("第3")]

    for comp in third_rounders:
        video_id = comp.get("第3", "")
        stats = stats_map.get(video_id)
        if stats is None:
            unmatched_count += 1
            stats = {}

        pianist = comp.get("名前", "") or ""
        country = comp.get("国", "") or ""

        # 最終結果テキストとソート用キー
        final_result_text, cat, rank_num, prize_order = determine_final_result(comp)

        # 国旗
        flag_file = get_flag_filename(country)
        flag_path = f"img/flag/{flag_file}" if flag_file else ""

        # 姓ソートキー
        pianist_sort_key = make_pianist_sort_key(pianist)

        # 生年月日と年齢
        birth_str = comp.get("生年月日", "") or ""
        age_years, birth_for_sort = calc_age_from_birthdate(birth_str, CONTEST_REF_DATE)

        videos.append(
            {
                "videoId": video_id,
                "url": stats.get("url") or f"https://www.youtube.com/watch?v={video_id}",
                "publishedAt": stats.get("publishedAt", ""),
                "viewCount": to_int_safe(stats.get("viewCount")),
                "likeCount": to_int_safe(stats.get("likeCount")),
                "pianist": pianist,
                "pianistSortKey": pianist_sort_key,
                "country": country,
                "finalResult": final_result_text,
                "finalSortCategory": cat,
                "finalSortRankNum": rank_num,
                "finalSortPrize": prize_order,
                "flagPath": flag_path,
                "birthDate": birth_for_sort,
                "ageYears": age_years,
            }
        )

    videos_json_safe = json.dumps(videos, ensure_ascii=False).replace("</", "<\\/")

    html = []
    html.append("<!DOCTYPE html>")
    html.append('<html lang="ja">')
    html.append("  <head>")
    html.append('    <meta charset="UTF-8">')

    html.append(
        "    <title>ショパコン勝手にYouTube聴衆賞(非公式) | 2025第3次予選集計</title>"
    )
    html.append(
        '    <meta name="description" content="ショパン国際ピアノコンクール2025第3次予選のYouTube再生回数を個人的にまとめた非公式メモです。順位と関係なく伸びているコンテスタントの存在を可視化するためのページです。">'
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
        '    <link rel="stylesheet" href="/chopin-competition/assets/css/style.css?v=76ba7eec5aa7918590041e6c94a14363f6b580e6">'
    )

    html.append("    <style>")
    html.append(
        "      table { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-top: 0.5rem; }"
    )
    html.append("      th, td { border: 1px solid #ddd; padding: 0.4rem 0.5rem; }")
    html.append("      th { background: #f0f0f0; }")
    html.append("      tbody tr:nth-child(even) { background: #fafafa; }")
    html.append("      .num-col { text-align: right; white-space: nowrap; }")
    html.append("      .rank-col { text-align: right; white-space: nowrap; }")
    html.append(
        "      .sort-icons { margin-left: 0.25rem; font-size: 0.75rem; white-space: nowrap; }"
    )
    html.append("      .sort-icon { cursor: pointer; margin-left: 0.1rem; color: #888; }")
    html.append("      .sort-icon.active { color: #000; font-weight: bold; }")
    html.append(
        "      .flag-icon { width: 20px; height: 14px; object-fit: cover; vertical-align: middle; }"
    )
    html.append(
        "      .thumb-img { width: 120px; aspect-ratio: 16/9; object-fit: cover; display: block; }"
    )
    html.append("    </style>")

    html.append("  </head>")
    html.append("  <body>")

    html.append('    <a id="skip-to-content" href="#content">Skip to the content.</a>')
    html.append('    <header class="page-header" role="banner">')
    html.append(
        '      <h1 class="project-name"><a href="/chopin-competition/" style="color:#fff;">ショパコン勝手にYouTube聴衆賞(非公式)</a></h1>'
    )
    html.append(
        '      <h2 class="project-tagline">ショパン国際ピアノコンクールのYouTube再生数を個人的にまとめた非公式メモです。順位と関係なく再生回数が伸びているコンテスタントの存在が気になってしまったのでまとめました🥰</h2>'
    )
    html.append("    </header>")

    html.append('    <main id="content" class="main-content" role="main">')

    if unmatched_count > 0:
        html.append(
            f'      <p style="color:#777;font-size:0.85rem;">※ {unmatched_count} 本は再生数データが見つかりませんでした（再生回数などが 0 として表示されます）。</p>'
        )

    html.append("      <h1>第19回(2025)ショパン国際ピアノコンクール 第3次予選再生数ランキング</h1>")
    html.append(
        f"      <p>集計日: {target_date_jp} ／ 対象動画数: {len(videos)} 本 ／ 年齢は2025年10月1日時点</p>"
    )

    html.append("      <table>")
    html.append("        <thead>")
    html.append("          <tr>")
    html.append(
        "            <th>名前"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='pianistSortKey' data-dir='asc' data-type='string'>▲</span>"
        "                <span class='sort-icon' data-key='pianistSortKey' data-dir='desc' data-type='string'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append(
        "            <th style='width:6em;'>国"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='country' data-dir='asc' data-type='string'>▲</span>"
        "                <span class='sort-icon' data-key='country' data-dir='desc' data-type='string'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append(
        "            <th style='width:5em;'>年齢"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='age' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='age' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append(
        "            <th style='width:8em;'>再生回数"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='viewCount' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='viewCount' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append(
        "            <th style='width:8em;'>高評価数"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='likeCount' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='likeCount' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append(
        "            <th style='width:8em;'>最終結果"
        "              <span class='sort-icons'>"
        "                <span class='sort-icon' data-key='finalSortCategory' data-dir='asc' data-type='number'>▲</span>"
        "                <span class='sort-icon' data-key='finalSortCategory' data-dir='desc' data-type='number'>▼</span>"
        "              </span>"
        "            </th>"
    )
    html.append("            <th style='width:11em;'>動画</th>")
    html.append("          </tr>")
    html.append("        </thead>")
    html.append("        <tbody id='ranking-body'></tbody>")
    html.append("      </table>")

    html.append('      <footer class="site-footer">')
    html.append('          <span class="site-footer-owner">©ショパコン勝手にYouTube聴衆賞(非公式)</span>')
    html.append("      </footer>")

    html.append("    </main>")

    html.append("    <script>")
    html.append(f"const videos = {videos_json_safe};")
    html.append(
        r"""
function formatNumber(n){
  if (n === null || n === undefined) return '';
  return n.toLocaleString('ja-JP');
}

function renderTable(list){
  const tbody = document.getElementById('ranking-body');
  tbody.innerHTML = '';

  list.forEach(v=>{
    const finalText = v.finalResult || '—';

    let countryCellHtml = '';
    if (v.flagPath){
      countryCellHtml = `<img src="${v.flagPath}" alt="${v.country}" title="${v.country}" class="flag-icon">`;
    } else {
      countryCellHtml = v.country || '';
    }

    const thumbUrl = `https://img.youtube.com/vi/${v.videoId}/mqdefault.jpg`;
    const videoUrl  = v.url || `https://www.youtube.com/watch?v=${v.videoId}`;

    const ageText = (v.ageYears !== null && v.ageYears !== undefined) ? v.ageYears : '';

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${v.pianist || ''}</td>
      <td>${countryCellHtml}</td>
      <td class="num-col">${ageText}</td>
      <td class="num-col">${formatNumber(v.viewCount)}</td>
      <td class="num-col">${formatNumber(v.likeCount)}</td>
      <td class="rank-col">${finalText}</td>
      <td>
        <a href="${videoUrl}" target="_blank" rel="noopener noreferrer">
          <img src="${thumbUrl}" alt="YouTube thumbnail" class="thumb-img">
        </a>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function sortAndRender(key, dir, type){
  const sorted = [...videos].sort((a,b)=>{
    if (key === 'finalSortCategory'){
      if (a.finalSortCategory !== b.finalSortCategory){
        return dir === 'asc'
          ? a.finalSortCategory - b.finalSortCategory
          : b.finalSortCategory - a.finalSortCategory;
      }
      if (a.finalSortRankNum !== b.finalSortRankNum){
        return dir === 'asc'
          ? a.finalSortRankNum - b.finalSortRankNum
          : b.finalSortRankNum - a.finalSortRankNum;
      }
      if (a.finalSortPrize !== b.finalSortPrize){
        return dir === 'asc'
          ? a.finalSortPrize - b.finalSortPrize
          : b.finalSortPrize - a.finalSortPrize;
      }
      return dir === 'asc'
        ? (a.pianistSortKey || '').localeCompare(b.pianistSortKey || '', 'ja')
        : (b.pianistSortKey || '').localeCompare(a.pianistSortKey || '', 'ja');
    }

    if (key === 'age'){
      const na = (typeof a.ageYears === 'number') ? a.ageYears : 999;
      const nb = (typeof b.ageYears === 'number') ? b.ageYears : 999;
      if (na !== nb){
        return dir === 'asc' ? na - nb : nb - na;
      }
      const da = a.birthDate || '';
      const db = b.birthDate || '';
      return dir === 'asc'
        ? da.localeCompare(db, 'ja')
        : db.localeCompare(da, 'ja');
    }

    const va = a[key];
    const vb = b[key];

    if(type === 'number'){
      const na = (typeof va === 'number') ? va : (parseFloat(va) || 0);
      const nb = (typeof vb === 'number') ? vb : (parseFloat(vb) || 0);
      return dir === 'asc' ? na - nb : nb - na;
    } else {
      const sa = (va ?? '').toString();
      const sb = (vb ?? '').toString();
      return dir === 'asc'
        ? sa.localeCompare(sb, 'ja')
        : sb.localeCompare(sa, 'ja');
    }
  });

  renderTable(sorted);
}

function setupSortIcons(){
  const icons = document.querySelectorAll('.sort-icon');
  icons.forEach(icon=>{
    icon.addEventListener('click',()=>{
      icons.forEach(i=>i.classList.remove('active'));
      icon.classList.add('active');
      const key = icon.getAttribute('data-key');
      const dir = icon.getAttribute('data-dir');
      const type = icon.getAttribute('data-type') || 'number';
      sortAndRender(key, dir, type);
    });
  });
}

document.addEventListener('DOMContentLoaded', ()=>{
  setupSortIcons();
  const defaultIcon = document.querySelector('.sort-icon[data-key="viewCount"][data-dir="desc"]');
  if(defaultIcon){
    defaultIcon.classList.add('active');
  }
  sortAndRender('viewCount','desc','number');
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
