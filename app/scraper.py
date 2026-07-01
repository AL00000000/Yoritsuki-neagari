import re
import unicodedata
from typing import Any

from playwright.sync_api import sync_playwright


def _normalize_stock_name(value: str) -> str:
    value = value.replace("", "").replace("◆", "").replace("・", "")
    value = value.strip()
    value = re.sub(r"^[^\wぁ-んァ-ン一-龯]+", "", value)
    value = re.sub(r"[^\wぁ-んァ-ン一-龯]+$", "", value)
    value = value.replace(" ", "").replace("　", "")
    value = unicodedata.normalize("NFKC", value)
    return value


def fetch_rendered_ranking(url: str) -> list[dict[str, Any]]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        rows_data = page.evaluate(r"""
            () => {
                const table = document.querySelector('table');
                if (!table) return [];

                return Array.from(table.querySelectorAll('tr'))
                    .slice(1)
                    .filter((row) => row.querySelectorAll('td,th').length > 0)
                    .map((row) => {
                        const cells = Array.from(row.querySelectorAll('td,th'));
                        const nameCell = cells[1];
                        const rawCode = nameCell?.querySelector('span.small')?.textContent.trim() ?? '';
                        const fallbackCodeMatch = nameCell?.textContent.match(/[（(]([A-Za-z0-9]+)[）)]/);
                        const code = rawCode.replace(/[（）()]/g, '').trim() || (fallbackCodeMatch ? fallbackCodeMatch[1].trim() : '');
                        return {
                            rank: cells[0]?.textContent.trim() ?? '',
                            name: nameCell?.querySelector('a')?.textContent.trim() ?? nameCell?.textContent.trim() ?? '',
                            code,
                            market: cells[2]?.textContent.trim() ?? '',
                        };
                    });
            }
            """)
        browser.close()

    rows: list[dict[str, Any]] = []
    for row in rows_data:
        rank = str(row.get("rank", ""))
        if not re.match(r"^(\d+)$", rank):
            continue

        code = str(row.get("code", ""))
        if not code:
            continue

        name = _normalize_stock_name(str(row.get("name", "")))
        if not name:
            continue

        rows.append(
            {
                "rank": int(rank),
                "name": name,
                "code": code,
                "market": str(row.get("market", "")),
            }
        )
    return rows


def parse_ranking_text(text: str) -> list[dict[str, Any]]:
    """Parse the ranking table text from StockWeather into a list of rows."""
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3:
            continue

        rank_match = re.match(r"^(\d+)$", cells[0])
        if not rank_match:
            continue

        name_cell = cells[1]
        code_match = re.search(r"（(\d{4})）|\((\d{4})\)", name_cell)
        if not code_match:
            continue

        code = code_match.group(1) or code_match.group(2)
        name = _normalize_stock_name(re.sub(r"\s*[（(].*$", "", name_cell))
        if not name or not code:
            continue

        rows.append(
            {
                "rank": int(rank_match.group(1)),
                "name": name,
                "code": code,
                "market": cells[2] if len(cells) > 2 else "",
            }
        )

    return rows
