import re
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

SOURCE_URL = "https://t.me/s/DHS_Dirham"
RATE_PATTERN = re.compile(
    r"#𝐃𝐢𝐫𝐡𝐚𝐦_𝐃𝐇𝐒\s*🇦🇪\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})\s*🇦🇪"
)


def read_rate():
    request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=20) as response:
        page = BeautifulSoup(response.read(), "html.parser")

    posts = page.select(".tgme_widget_message_text")
    for post in reversed(posts):
        match = RATE_PATTERN.search(post.get_text(" ", strip=True))
        if match:
            return int(match.group(1).replace(",", ""))

    raise SystemExit("No matching dirham rate found.")


if __name__ == "__main__":
    rate = read_rate()
    print(f"Source rate: {rate:,} toman")
    print(f"Calculated rate: {rate + 500:,} toman")
