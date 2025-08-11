import time
from typing import List
from selenium import webdriver
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from selenium.webdriver.common.by import By


class SeleniumScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        # self.driver.set_page_load_timeout(5)

    def scrapeGoogle(self, queries: List[str]) -> List["ArticlePage"]:
        articleLinks = []
        for query in queries:
            searchUrl = SeleniumScraper.buildSearchUrl(query)
            print(searchUrl)
            self.driver.get(searchUrl)
            time.sleep(5)

            searchResults = self.driver.find_elements(By.CLASS_NAME, "m5k28")

            for searchResult in searchResults:
                title = searchResult.find_element(By.CLASS_NAME, "JtKRv")
                if not title:
                    continue

                title = title.text
                print(title)

                articleUrl = searchResult.find_element(
                    By.CSS_SELECTOR, "a"
                ).get_attribute("href")

                if not articleUrl:
                    continue

                articleLink = ArticleLink(query, articleUrl, title)
                articleLinks.append(articleLink)

        articlePages = []
        for articleLink in articleLinks[:3]:
            try:
                print(articleLink.url)
                self.driver.get(articleLink.url)
                time.sleep(5)
                pSelectors = self.driver.find_elements(By.XPATH, "//body//p")
                listSelectors = self.driver.find_elements(
                    By.XPATH, "//body//ol | //body//ul"
                )
                text = "\n".join([item.text for item in pSelectors + listSelectors])
                if len(text) < 400:
                    text = "\n".join(
                        [
                            div.text
                            for div in self.driver.find_elements(
                                By.XPATH, "//body//div"
                            )
                        ]
                    )
                articlePages.append(ArticlePage(articleLink, text))
                print(text[:100])
            except Exception as e:
                print(e)

        self.driver.quit()

        return articlePages

    @classmethod
    def buildSearchUrl(cls, query: str) -> str:
        searchParams = {
            # Interface Language
            "hl": ["en-IN"],
            # Country of the document
            "gl": ["IN"],
            "ceid": ["IN:en"],
            "q": [query],
        }
        # ?hl=en-IN&gl=IN&ceid=IN%3Aen
        scheme, netloc, path, queryString, fragment = urlsplit(
            "https://news.google.com/search/"
        )
        queryParams = parse_qs(queryString)
        queryParams.update(searchParams)
        newQueryString = urlencode(queryParams)

        searchUrl = urlunsplit((scheme, netloc, path, newQueryString, fragment))
        return searchUrl


class ArticleLink:
    def __init__(self, query, url, title):
        self.query = query
        self.url = url
        self.title = title

    def __repr__(self):
        return str((self.query, self.url))


class ArticlePage:
    def __init__(self, articleLink, content):
        self.query = articleLink.query
        self.url = articleLink.url
        self.title = articleLink.title
        self.content = content

    def __repr__(self):
        return str((self.query, self.url))
