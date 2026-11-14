import re
import sys
import unicodedata
from time import time_ns
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SOURCE_URL = "https://t.me/s/DHS_Dirham"
RATE_PATTERN = re.compile(
    r"#Dirham_DHS\s*🇦🇪\s*([0-9]{1,3}(?:[,٬][0-9]{3})+|[0-9]{4,})\s*🇦🇪",
    re.IGNORECASE,
)
POST_PATTERN = re.compile(r"DHS_Dirham/([0-9]+)", re.IGNORECASE)
INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u200e\u200f\ufe0f"))


def read_rate():
    candidates = {}
    pages = {
        "Channel": {},
        "Hashtag search": {"q": "#𝐃𝐢𝐫𝐡𝐚𝐦_𝐃𝐇𝐒"},
    }

    for label, params in pages.items():
        query = urlencode({**params, "_": time_ns()})
        request = Request(
            f"{SOURCE_URL}?{query}",
            headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"},
        )
        try:
            with urlopen(request, timeout=20) as response:
                page = BeautifulSoup(response.read(), "html.parser")
        except (URLError, TimeoutError) as error:
            print(f"{label}: {error}", file=sys.stderr)
            continue

        visible_ids = []
        matched_ids = []

        for message in page.select(".tgme_widget_message[data-post]"):
            post_match = POST_PATTERN.fullmatch(message["data-post"])
            if not post_match:
                continue

            post_id = int(post_match.group(1))
            visible_ids.append(post_id)
            post = message.select_one(".tgme_widget_message_text")
            if post is None:
                continue

            raw_text = post.get_text(" ", strip=True)
            normalized = unicodedata.normalize("NFKC", raw_text).translate(INVISIBLE)
            rate_match = RATE_PATTERN.search(normalized)
            if rate_match:
                digits = rate_match.group(1).replace(",", "").replace("٬", "")
                candidates[post_id] = int(digits)
                matched_ids.append(post_id)

        print(
            f"{label}: newest visible post {max(visible_ids, default=None)}, "
            f"newest rate post {max(matched_ids, default=None)}",
            file=sys.stderr,
        )

    if not candidates:
        raise SystemExit("No matching dirham rate found.")

    post_id = max(candidates)
    rate = candidates[post_id]
    print(f"Source post: https://t.me/DHS_Dirham/{post_id}")
    print(f"Read source post {post_id}, rate {rate:,} toman", file=sys.stderr)
    return rate


if __name__ == "__main__":
    rate = read_rate()
    print(f"Source rate: {rate:,} toman")
    print(f"Calculated rate: {rate + 500:,} toman")
