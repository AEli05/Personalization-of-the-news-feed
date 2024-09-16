from pprint import pprint

import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """Extract news from a given web page"""
    news_list = []

    heads_list = []
    for head in parser.find_all(class_="titleline"):
        head = head.find("a").contents[0]
        heads_list.append(head)

    authors_list = []
    for author in parser.find_all("a", class_="hnuser"):
        author = author.contents[0]
        authors_list.append(author)

    score_list = []
    for score in parser.find_all(class_="score"):
        score = score.contents[0].split()[0]
        score_list.append(score)

    links_list = []
    for link in parser.find_all(class_="titleline"):
        link = link.find("a")
        link = link["href"]
        links_list.append(link)

    comments_list = []
    for comment in parser.find_all("a"):
        if comment["href"]:
            if "item?id" in comment["href"]:
                comment = comment.contents[0]
                if (
                    "minutes" in comment
                    or "minute" in comment
                    or "hours" in comment
                    or "seconds" in comment
                    or "years" in comment
                ):
                    continue
                if comment == "discuss":
                    comment = 0
                    comments_list.append(comment)
                    continue
                if "comment" in comment:
                    comment = comment.split()[0]
                    comments_list.append(comment)

    for i in range(30):
        news = {}
        news["author"] = authors_list[i]
        news["comments"] = comments_list[i]
        news["points"] = score_list[i]
        news["title"] = heads_list[i]
        news["url"] = links_list[i]
        news_list.append(news)
    return news_list


def extract_next_page(parser):
    """Extract next page URL"""
    n_page = parser.find("a", class_="morelink")
    n_page = n_page["href"]
    return n_page


def get_news(url, n_pages=1):
    """Collect news from a given web page"""
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news


if __name__ == "__main__":
    news = get_news(url="https://news.ycombinator.com/newest", n_pages=2)
    pprint(news[:5])
