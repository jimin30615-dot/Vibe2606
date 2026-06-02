import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def extract_news_links(search_html: str) -> list[str]:
    soup = BeautifulSoup(search_html, "html.parser")
    links = []

    # 검색 결과에서 뉴스 기사 제목 링크를 우선적으로 추출합니다.
    title_anchors = soup.select(
        'div.fds-news-item-list-desk a[data-heatmap-target=".tit"], '
        'div.fds-news-item-list-desk a[data-heatmap-target=".body"], '
        'div.fds-news-item-list-desk a[data-heatmap-target=".img"]'
    )

    if not title_anchors:
        title_anchors = soup.select(
            'a[data-heatmap-target=".tit"], '
            'a[data-heatmap-target=".body"], '
            'a[data-heatmap-target=".img"]'
        )

    for anchor in title_anchors:
        href = anchor.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = urljoin("https://search.naver.com", href)
        if href.startswith("http") and "search.naver.com" not in href and href not in links:
            links.append(href)

    # fallback: 검색 결과 페이지 내 모든 기사 후보 링크를 추가 검사합니다.
    if not links:
        for anchor in soup.select("div.fds-news-item-list-desk a[href]"):
            href = anchor.get("href")
            if not href:
                continue
            if href.startswith("/"):
                href = urljoin("https://search.naver.com", href)
            if href.startswith("http") and "search.naver.com" not in href and href not in links:
                links.append(href)

    return links


def extract_article_text(article_html: str) -> str:
    soup = BeautifulSoup(article_html, "html.parser")

    body_selectors = [
        "#articleBodyContents",
        "#articeBody",
        "#newsEndContents",
        "div#news_end_contents",
        "div#dic_area",
    ]

    for selector in body_selectors:
        article_body = soup.select_one(selector)
        if article_body:
            for tag in article_body(["script", "style", "iframe", "ins", "a"]):
                tag.decompose()
            text = article_body.get_text(separator="\n", strip=True)
            if text:
                return text

    # fallback: extract paragraphs from the main document
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    return "\n\n".join(paragraphs)


def main():
    search_url = (
        "https://search.naver.com/search.naver?sm=tab_hty.top&where=nexearch&ssc=tab.nx.all"
        "&query=%EB%B0%98%EB%8F%84%EC%B2%B4&oquery=AI&tqi=jm09Nlqps2wsslu0d5h-071911&ackey=fsmh1uje"
    )

    print("검색 페이지 가져오는 중...")
    search_html = fetch_html(search_url)

    print("뉴스 기사 링크 추출 중...")
    news_links = extract_news_links(search_html)
    if not news_links:
        print("뉴스 기사 링크를 찾지 못했습니다.")
        return

    print(f"{len(news_links)}개의 뉴스 링크를 찾았습니다. 첫 번째 기사 크롤링 중...")
    first_link = news_links[0]
    print("기사 URL:", first_link)

    article_html = fetch_html(first_link)
    article_text = extract_article_text(article_html)

    print("\n=== 기사 본문 ===\n")
    print(article_text)


if __name__ == "__main__":
    main()
