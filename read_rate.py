import re
import sys
import unicodedata
from time import time_ns
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SOURCE_URL = "https://t.me/s/DHS_Dirham"
RATE_PATTERN = re.compile(
    r"#Dirham_DHS\s*🇦🇪\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})\s*🇦🇪",
    re.IGNORECASE,
)
POST_PATTERN = re.compile(r"DHS_Dirham/([0-9]+)", re.IGNORECASE)


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
        text = unicodedata.normalize("NFKC", post.get_text(" ", strip=True))
        rate_match = RATE_PATTERN.search(text)
        message = post.find_parent(attrs={"data-post": True})
        if not rate_match or message is None:
            continue

        post_match = POST_PATTERN.fullmatch(message["data-post"])
        if not post_match:
            continue

        post_id = int(post_match.group(1))
        if post_id > latest_post_id:
            latest_post_id = post_id
            latest_rate = int(rate_match.group(1).replace(",", ""))

    if latest_rate is None:
        raise SystemExit("No matching dirham rate found.")

    print(f"Source post: https://t.me/DHS_Dirham/{latest_post_id}")
    print(f"Read source post {latest_post_id}, rate {latest_rate:,} toman", file=sys.stderr)
    return latest_rate


if __name__ == "__main__":
    rate = read_rate()
    print(f"Source rate: {rate:,} toman")
    print(f"Calculated rate: {rate + 500:,} toman")
