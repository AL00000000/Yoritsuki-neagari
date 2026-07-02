# Yoritsuki-neagari

This project saves the daily top-100 stock ranking from StockWeather into JSON snapshots.

## How it works

- Fetches the ranking page from StockWeather.
- Extracts ranks, stock names, codes, and markets.
- Saves a timestamped JSON file under the data directory.

## Run locally

```bash
pip install -r requirements.txt
python -m playwright install chromium
python app/main.py
```

## View saved snapshots

### Display in terminal

```bash
python app/view.py --latest
python app/view.py --today
python app/view.py --date 2026-07-01
python app/view.py --limit 20
```

### Export as HTML table (open in browser)

```bash
python app/view.py --today --html
# Creates: data/ranking-2026-07-01T17-00-00JST.html
```

### Export as CSV (open in Excel)

```bash
python app/view.py --today --csv
# Creates: data/ranking-2026-07-01T17-00-00JST.csv
```

## Next steps

- Add GitHub integration to commit the JSON files automatically.
- Add GitHub Actions scheduling for daily execution at 16:00 JST.
- Add a small web UI or notebook for reviewing the saved snapshots.
