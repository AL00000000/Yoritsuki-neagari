from __future__ import annotations

import json
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


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_ranking_html(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def save_ranking_snapshot(rows: list[dict[str, Any]], source_url: str) -> Path:
    now_utc = datetime.now(timezone.utc)
    now_jst = now_utc.astimezone(ZoneInfo("Asia/Tokyo"))
    timestamp_utc = now_utc.strftime("%Y-%m-%dT%H-%M-%SZ")
    timestamp_jst = now_jst.strftime("%Y-%m-%dT%H-%M-%S")
    path = DATA_DIR / f"ranking-{timestamp_jst}JST.json"
    payload = {
        "captured_at_utc": timestamp_utc,
        "captured_at_jst": timestamp_jst,
        "source_url": source_url,
        "rows": rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run() -> None:
    url = "https://finance.stockweather.co.jp/contents/ranking.aspx?mkt=1&cat=0000&type=2"
    html = fetch_ranking_html(url)
    rows = fetch_rendered_ranking(url)
    if not rows:
        rows = parse_ranking_text(html)
    if not rows:
        raise RuntimeError("No ranking rows were parsed")

    path = save_ranking_snapshot(rows, url)
    print(f"Saved {len(rows)} rows to {path}")


if __name__ == "__main__":
    run()
