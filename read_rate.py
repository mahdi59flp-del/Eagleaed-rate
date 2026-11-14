import re
import unicodedata
from time import time_ns
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SOURCE_URL = "https://t.me/s/DHS_Dirham"
POST_PATTERN = re.compile(r"DHS_Dirham/([0-9]+)", re.IGNORECASE)
RATE_PATTERN = re.compile(
    r"#Dirham_DHS\s*(?:🇦🇪\s*)?"
    r"(\d{1,3}(?:[,٬]\d{3})+|\d{4,})(?![\d,٬])",
    re.IGNORECASE,
)
INVISIBLE_MARKS = dict.fromkeys(
    map(ord, "\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
)


def read_rate():
    request = Request(
        f"{SOURCE_URL}?_={time_ns()}",
        headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"},
    )
    with urlopen(request, timeout=20) as response:
        page = BeautifulSoup(response.read(), "html.parser")

    latest_post_id = 0
    latest_rate = None

    for post in page.select(".tgme_widget_message_text"):
        message = post.find_parent(attrs={"data-post": True})
        if message is None:
            continue

        post_match = POST_PATTERN.fullmatch(message["data-post"])
        if not post_match:
            continue

        text = unicodedata.normalize("NFKC", post.get_text(" ", strip=True))
        rate_match = RATE_PATTERN.search(text.translate(INVISIBLE_MARKS))
        post_id = int(post_match.group(1))

        if rate_match and post_id > latest_post_id:
            latest_post_id = post_id
            latest_rate = int(rate_match.group(1).replace(",", "").replace("٬", ""))

    if latest_rate is None:
        raise SystemExit("No matching dirham rate found.")

    print(f"Source post: https://t.me/DHS_Dirham/{latest_post_id}")
    return latest_rate


if __name__ == "__main__":
    rate = read_rate()
    print(f"Source rate: {rate:,} toman")
    print(f"Calculated rate: {rate + 500:,} toman")
