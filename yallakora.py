#!/usr/bin/env python3
"""
YallaKora match scraper 
يجمع مباريات لِتاريخ معين من yallakora.com ويكتبها في matches.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from pyfiglet import Figlet

# ------- إعدادات ثابتة -------
BASE_URL = "https://www.yallakora.com/match-center"
OUTPUT_FILE = Path("matches.csv")
USER_AGENT = "Mozilla/5.0 (compatible; YallaKoraScraper/1.0; +https://example.local/)"
# -----------------------------

def clear_screen() -> None:
    print("\n" * 100)


def render_banner() -> None:
    f = Figlet(font="slant")
    print(f.renderText("X-Code-2"))


def validate_date(date_str: str) -> str:
    """تأكد من شكل التاريخ (mm/dd/YYYY) — إرجاع نفس النص إذا صح، وإلا يوقف البرنامج."""
    try:
        datetime.strptime(date_str, "%m/%d/%Y")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("التنسيق لازم يكون mm/dd/YYYY مثال: 11/13/2025")


def fetch_page(date_str: str, timeout: int = 10) -> requests.Response:
    """تحميل صفحة النتائج لتاريخ معين مع headers و timeouts."""
    params = {"date": date_str}
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(BASE_URL, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"فشل تحميل الصفحة: {e}")
    return resp


def _get_text_or_default(elem, default: str = "") -> str:
    return elem.get_text(strip=True) if elem else default


def parse_matches(html: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    match_cards = soup.select("div.matchCard")
    matches: List[Dict[str, str]] = []

    for card in match_cards:
        title_elem = card.find("h2")
        match_title = _get_text_or_default(title_elem, "غير محدد")

        items = card.select("div.item")
        for item in items:
            team_a = _get_text_or_default(item.select_one("div.teamA"))
            team_b = _get_text_or_default(item.select_one("div.teamB"))

            mresult = item.select_one("div.MResult")
            time_span = mresult.select_one("span.time") if mresult else None
            score_spans = mresult.select("span.score") if mresult else []

            match_time = _get_text_or_default(time_span, "غير معروف")
            if len(score_spans) >= 2:
                score = f"{_get_text_or_default(score_spans[0])} - {_get_text_or_default(score_spans[1])}"
            else:
                score = "غير متوفر"

            matches.append({
                "نوع المباراة": match_title,
                "الفريق الاول": team_a,
                "الفريق الثانى": team_b,
                "معاد المبارة": match_time,
                "نتيجة المباراة": score,
            })

    return matches


def write_csv(records: List[Dict[str, str]], dest: Path = OUTPUT_FILE) -> None:
    if not records:
        print("ما فيش مباريات لليوم ده أو لم يتم استخراج أي بيانات.")
        return

    # ترتيب الأعمدة حسب المفتاح من أول سجل
    fieldnames = list(records[0].keys())
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"File created: {dest.resolve()}")


def main(date_str: str) -> int:
    render_banner()
    print(f"جاري البحث عن مباريات بتاريخ: {date_str}\n")

    try:
        resp = fetch_page(date_str)
    except RuntimeError as e:
        print(e)
        return 1

    matches = parse_matches(resp.text)
    write_csv(matches)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape matches from yallakora.com for a given date.")
    parser.add_argument(
        "date",
        type=validate_date,
        help="Enter Match Date EX (mm/dd/YYYY) e.g. 11/13/2025"
    )
    args = parser.parse_args()
    clear_screen()
    sys.exit(main(args.date))
