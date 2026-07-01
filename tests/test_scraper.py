import unittest

from app.scraper import parse_ranking_text


class ScraperTests(unittest.TestCase):
    def test_parse_ranking_text_extracts_ranked_stocks(self) -> None:
        sample_text = """
        ※優先市場のみが対象となります。  市場   業種   寄付からの値上がり率　ランキング 更新日時：2026/07/01 15:30
        | 1 |  ＳＵＭＣＯ （3436） | 東証プライム | 4,729.0 | +700.0 | +17.37% | 11.91% |
        | 2 |  芝浦 （6590） | 東証プライム | 5,320.0 | +700.0 | +15.15% | 10.53% |
        | 3 |  ニチコン （6996） | 東証プライム | 4,770.0 | +620.0 | +14.94% | 10.06% |
        """

        rows = parse_ranking_text(sample_text)

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["rank"], 1)
        self.assertEqual(rows[0]["name"], "SUMCO")
        self.assertEqual(rows[0]["code"], "3436")
        self.assertEqual(rows[0]["market"], "東証プライム")


if __name__ == "__main__":
    unittest.main()
