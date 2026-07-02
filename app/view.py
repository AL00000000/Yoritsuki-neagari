from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
HTML_DIR = ROOT / "html"
HTML_DIR.mkdir(exist_ok=True)


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
        print(
            f"  {row['rank']}: {row['name']} ({row['code']}) - {row['market']} | "
            f"現在値 {row.get('current_price','')} | 前日比 {row.get('prev_change','')} | 寄付比 {row.get('prev_pct','')}"
        )


def export_html(snapshot: dict[str, Any], output_path: Path) -> None:
    rows = snapshot.get("rows", [])
    captured_at_jst = snapshot.get("captured_at_jst") or snapshot.get("captured_at", "Unknown")
    
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockWeather ランキング - {captured_at_jst}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        .info {{
            background-color: #e8f4f8;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #45a049;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .rank {{
            font-weight: 600;
            color: #4CAF50;
            width: 50px;
        }}
        .name {{
            font-weight: 500;
        }}
        .code {{
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }}
        .market {{
            font-size: 13px;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>StockWeather 株式ランキング（上昇率）</h1>
    <div class="info">
        <strong>取得日時（JST）:</strong> {captured_at_jst}<br>
        <strong>取得件数:</strong> {len(rows)} 件
    </div>
    <table>
        <thead>
            <tr>
                <th class="rank">順位</th>
                <th class="name">銘柄名</th>
                <th class="code">コード</th>
                <th class="market">市場</th>
                <th>現在値</th>
                <th>前日比</th>
                <th>寄付比</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for row in rows:
        html_content += f"""            <tr>
                <td class="rank">{row['rank']}</td>
                <td class="name">{row['name']}</td>
                <td class="code">{row['code']}</td>
                <td class="market">{row['market']}</td>
                <td>{row.get('current_price', '')}</td>
                <td>{row.get('prev_change', '')}</td>
                <td>{row.get('prev_pct', '')}</td>
            </tr>
"""
    
    html_content += """        </tbody>
    </table>
</body>
</html>
"""
    
    output_path.write_text(html_content, encoding="utf-8")
    print(f"HTML exported to: {output_path}")


def export_csv(snapshot: dict[str, Any], output_path: Path) -> None:
    rows = snapshot.get("rows", [])
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["順位", "銘柄名", "コード", "市場", "現在値", "前日比", "寄付比"])
        for row in rows:
            writer.writerow([
                row["rank"],
                row["name"],
                row["code"],
                row["market"],
                row.get("current_price", ""),
                row.get("prev_change", ""),
                row.get("prev_pct", ""),
            ])
    
    print(f"CSV exported to: {output_path}")


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
    parser.add_argument(
        "--html",
        action="store_true",
        help="Export as HTML table file.",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Export as CSV file.",
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
    
    if args.html:
        output_path = HTML_DIR / f"{snapshot_path.stem}.html"
        export_html(snapshot, output_path)
    elif args.csv:
        output_path = snapshot_path.parent / f"{snapshot_path.stem}.csv"
        export_csv(snapshot, output_path)
    else:
        print_snapshot_summary(snapshot, args.limit)


if __name__ == "__main__":
    main()
