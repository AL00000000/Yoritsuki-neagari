from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scraper import fetch_rendered_ranking, parse_ranking_text
from app.view import export_html

ROOT = Path(__file__).resolve().parent.parent
HTML_DIR = ROOT / "html"
HTML_DIR.mkdir(exist_ok=True)


def fetch_ranking_html(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def save_ranking_html(rows: list[dict[str, Any]], source_url: str) -> Path:
    now_utc = datetime.now(timezone.utc)
    now_jst = now_utc.astimezone(ZoneInfo("Asia/Tokyo"))
    date_str = now_jst.strftime("%Y-%m-%d")
    path = HTML_DIR / f"ranking-{date_str}.html"
    payload = {
        "captured_at_utc": now_utc.strftime("%Y-%m-%dT%H-%M-%SZ"),
        "captured_at_jst": now_jst.strftime("%Y-%m-%dT%H-%M-%S"),
        "source_url": source_url,
        "rows": rows,
    }
    export_html(payload, path)
    return path


def run() -> None:
    url = "https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=1&cat=0000&type=2"
    html = fetch_ranking_html(url)
    rows = fetch_rendered_ranking(url)
    if not rows:
        rows = parse_ranking_text(html)
    if not rows:
        raise RuntimeError("No ranking rows were parsed")

    html_path = save_ranking_html(rows, url)
    print(f"Saved daily HTML output to {html_path}")


if __name__ == "__main__":
    run()
