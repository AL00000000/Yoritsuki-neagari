from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def list_snapshots() -> list[Path]:
    return sorted(DATA_DIR.glob("ranking-*.json"))


def load_snapshot(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def find_snapshot_by_date(date_str: str) -> Path | None:
    for path in list_snapshots():
        if path.name.startswith(f"ranking-{date_str}"):
            return path
    return None


def print_snapshot_summary(snapshot: dict[str, Any], row_limit: int) -> None:
    captured_at_jst = snapshot.get("captured_at_jst") or snapshot.get("captured_at")
    captured_at_utc = snapshot.get("captured_at_utc")
    print(f"Snapshot JST: {captured_at_jst}")
    if captured_at_utc:
        print(f"Snapshot UTC: {captured_at_utc}")
    print(f"Source URL: {snapshot['source_url']}")
    rows = snapshot.get("rows", [])
    print(f"Total rows: {len(rows)}")
    print()
    if not rows:
        print("No rows available in this snapshot.")
        return

    print(f"First {min(row_limit, len(rows))} rows:")
    for row in rows[:row_limit]:
        print(f"  {row['rank']}: {row['name']} ({row['code']}) - {row['market']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="View saved StockWeather ranking snapshots."
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Show the latest saved snapshot.",
    )
    parser.add_argument(
        "--today",
        action="store_true",
        help="Show today's snapshot using JST date.",
    )
    parser.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Show the snapshot saved for the given date.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of rows to show from the snapshot.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    snapshots = list_snapshots()

    if not snapshots:
        raise SystemExit("No snapshot files found in data/. Run python app/main.py first.")

    snapshot_path: Path | None = None
    if args.today:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        today_jst = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d")
        snapshot_path = find_snapshot_by_date(today_jst)
        if not snapshot_path:
            raise SystemExit(f"No snapshot found for today ({today_jst}).")
    elif args.date:
        snapshot_path = find_snapshot_by_date(args.date)
        if not snapshot_path:
            raise SystemExit(f"No snapshot found for date {args.date}")
    else:
        snapshot_path = snapshots[-1]
        if not args.latest:
            print("Showing latest snapshot by default. Use --today or --date YYYY-MM-DD to select a specific day.")

    snapshot = load_snapshot(snapshot_path)
    print_snapshot_summary(snapshot, args.limit)


if __name__ == "__main__":
    main()
