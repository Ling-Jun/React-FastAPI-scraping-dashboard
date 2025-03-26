from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import re
from utils.config import DriverPath, PARSER, WarningMessages

# import spacy
# from concurrent.futures import ThreadPoolExecutor
# from urllib.parse import urljoin, urlparse
# from urllib.robotparser import RobotFileParser


# ==================================================================================================================================================
#                                                         Initializers
# ==================================================================================================================================================
def _init_driver(
    driverMode="auto",
    extra_options: list[str] = [
        "--headless",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        '--js-flags="--max-old-space-size=4096"',
        "--disable-images",
        "--disable-javascript",
        "--disable-gpu",
        "--enable-unsafe-swiftshader",
    ],
):
    chrome_options = Options()
    for option in extra_options:
        chrome_options.add_argument(option)

    if driverMode == "auto":
        return webdriver.Chrome(options=chrome_options)
        # from webdriver_manager.chrome import ChromeDriverManager
        # service = Service(executable_path=ChromeDriverManager(driver_version="129.0.6668.90").install())
        # return webdriver.Chrome(service=service, options=chrome_options)
    elif driverMode == "manual":
        print(f"Driver path: {DriverPath.CHROME_DRIVER.value}\n\n")
        service = Service(executable_path=DriverPath.CHROME_DRIVER.value)
        return webdriver.Chrome(service=service, options=chrome_options)


# ==================================================================================================================================================
#                                                         Extractors
# ==================================================================================================================================================
# def find_sitemap_in_robots(base_url: str) -> list:
#     """
#     Attempts to find sitemap URLs specified in the robots.txt file of the given base URL.
#     Returns a list of sitemap URLs if found; otherwise, returns an empty list.
#     """
#     parsed_url = urlparse(base_url)
#     robots_url = urljoin(f"{parsed_url.scheme}://{parsed_url.netloc}", "/robots.txt")
#     rp = RobotFileParser()
#     rp.set_url(robots_url)
#     try:
#         rp.read()
#         return rp.site_maps() or []
#     except Exception:
#         return []


# def check_sitemaps(urls: list[str]) -> dict:
#     """
#     Checks for the existence of sitemaps for a list of base URLs.
#     Returns a dictionary mapping each base URL to its sitemap URL if found, otherwise None.
#     """
#     common_sitemap_paths = [
#         "sitemap.xml",
#         "sitemap_index.xml",
#         "sitemap/sitemap.xml",
#         "sitemap/index.xml",
#         "sitemap1.xml",
#         "sitemap.xml.gz",
#         "sitemap.txt",
#         "wp-sitemap.xml",
#         "sitemap/",
#     ]
#     results = {}
#     for base_url in urls:
#         base_url = add_protocol2url(base_url)
#         for sitemap_url in find_sitemap_in_robots(base_url):
#             try:
#                 response = requests.head(sitemap_url, allow_redirects=True)
#                 if response.status_code == 200:
#                     results[base_url] = sitemap_url
#                     break
#             except requests.RequestException:
#                 continue
#         else:
#             for path in common_sitemap_paths:
#                 sitemap_url = urljoin(base_url, path)
#                 try:
#                     response = requests.head(sitemap_url, allow_redirects=True)
#                     if response.status_code == 200:
#                         results[base_url] = sitemap_url
#                         break
#                 except requests.RequestException:
#                     continue
#             else:
#                 results[base_url] = None
#     return results


def extract_page2txt(
    url,
    parser=PARSER.SELENIUM.value,
    selenium_wait_seconds=2,
    timeout=12,
):
    url = add_protocol2url(url=url)
    if is_url(url):
        print("URL is valid!\n")
    else:
        print(WarningMessages.URLNotValid.value)
        return WarningMessages.URLNotValid.value

    try:
        if parser == PARSER.BS4.value:
            print(f"Choosing parser: {parser}!\n")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                # "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raises HTTPError for bad responses
            # print(f"Response status: {response.status_code}\n")
            soup = BeautifulSoup(response.text, "html.parser")
            main_tag = soup.find("main")
            if main_tag:
                page_content = main_tag.get_text(strip=True)
            else:
                page_content = soup.get_text(separator="\n", strip=True)
        elif parser == PARSER.SELENIUM.value:
            print(f"Choosing parser: {parser}!\n")
            driver = _init_driver()
            driver.get(url)
            # page_raw_html = driver.page_source
            time.sleep(selenium_wait_seconds)
            try:
                page_content = driver.find_element(by="tag name", value="main").text
            except:
                page_content = driver.find_element(by="tag name", value="body").text

    except Exception as e:
        print(f"The ERROR is: {e}\n")
        print(WarningMessages.ContentNotValid.value)
        if parser == PARSER.BS4.value:
            print("Switching to Selenium as a fallback...\n")
            return extract_page2txt(url, PARSER.SELENIUM.value, selenium_wait_seconds)
        return WarningMessages.ContentNotValid.value

    finally:
        if parser == PARSER.SELENIUM.value:
            try:
                driver.quit()
            except Exception as e:
                print(f"ERROR quitting Chrome Driver: {e}!\n")
    return page_content


# def _extract_links(html_content, base_url):
#     """
#     extract hyperlinks from a webpage

#     a_tag is of type <class 'bs4.element.Tag'>
#     requests.compat.urljoin() is the same as importing urljoin from urlparse package
#     """
#     soup = BeautifulSoup(html_content, "html.parser")
#     links = set()
#     for a_tag in soup.find_all("a", href=True):
#         # print(f"type(a_tag): {type(a_tag)}; a_tag: {a_tag}; \n")
#         href = a_tag["href"]  # href is a str
#         # print(f"type(href):{type(href)}; href; {href}\n")
#         if href.startswith("http"):
#             links.add(href)
#         else:
#             print("This is a relative URL!!\n")
#             full_url = requests.compat.urljoin(base_url, href)
#             links.add(full_url)
#     return links


# ==================================================================================================================================================
#                                                         Chunking
# ==================================================================================================================================================
# def extract_propositions(text):
#     """
#     Propositional chunking involves breaking down text into atomic units called propositions, each representing a distinct fact or idea.

#     Returns a list of propositions.
#     """
#     nlp = spacy.load("en_core_web_sm")
#     doc = nlp(text)
#     propositions = []

#     for sent in doc.sents:
#         for token in sent:
#             if token.dep_ in ("ROOT", "conj"):
#                 proposition = " ".join([w.text for w in token.subtree])
#                 propositions.append(proposition)

#     return propositions


# ==================================================================================================================================================
#                                                         Get Nested URLs
# ==================================================================================================================================================
# def getNestedURLofCurrentLayer(
#     url, parser=PARSER.SELENIUM.value, selenium_wait_seconds=2
# ):
#     if parser == PARSER.BS4.value:
#         response = requests.get(url)
#         soup = BeautifulSoup(response.text, "html.parser")
#         page_html = str(soup.find("main"))
#     elif parser == PARSER.SELENIUM.value:
#         driver = _init_driver()
#         driver.get(url)
#         time.sleep(selenium_wait_seconds)
#         element = driver.find_element(by="tag name", value="main")
#         page_html = element.get_attribute("outerHTML")
#         driver.quit()
#     # page_content = _extract_text_from_htmlContent(page_html)
#     # summary = summarize_text(page_content)
#     # import spacy
#     # nlp = spacy.load("en_core_web_sm")
#     # key_phrases = [chunk.text for chunk in nlp(page_content).noun_chunks]
#     # print(f"\nURL: {url}")
#     # print(f"Summary: {summary}")
#     # print(f"Key Phrases: {key_phrases}")

#     # print(f"page_html: {page_html}\n")
#     nested_links = _extract_links(page_html, base_url=url)
#     return nested_links


# def getNestedURLofAllLayers(
#     urls, max_workers=5, deepestNestedLayer=2, numOfLinksToExploreWithinLayer=2
# ):
#     """
#     This function explores the URLs within URLs.

#     The initial URLs can have sub-hyperlinks, and the sub-hyperlinks can have their sub-hyperlinks.

#     This is what we call layers after layers of nested links.
#     - "deepestNestedLayer" sets the max layer of sub-hyperlinks to explore.

#     There could also be any number of hyperlinks within a layer.
#     - "numOfLinksToExploreWithinLayer" restricts on how many links (chosen at random) within this layer we would explore.

#     Since there could be hundres of links in a layer, we can't explore them all.
#     """
#     visited_urls = set()
#     url_queue = set(urls)

#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         nested_layer = 1
#         while url_queue and nested_layer < deepestNestedLayer + 1:
#             print(f"Beginning url_queue: {url_queue}\n")
#             futures = []
#             for url in list(url_queue):
#                 if url not in visited_urls and is_url(url):
#                     futures.append(executor.submit(getNestedURLofCurrentLayer, url))
#                     visited_urls.add(url)
#                     url_queue.remove(url)

#             for future_number, future in enumerate(futures):
#                 try:
#                     nested_links = future.result()
#                     nested_links = set(
#                         list(nested_links)[:numOfLinksToExploreWithinLayer]
#                     )
#                     print(
#                         f"The nested_links for link number {future_number+1} are: {nested_links}\n"
#                     )
#                     url_queue.update(nested_links - visited_urls)
#                 except Exception as e:
#                     print(f"Error processing URL: {e}")
#             print(f"Visited urls in the layer: {visited_urls}\n")
#             print(f"Expected futures in the layer: {futures}\n")
#             print(f"New layer's url_queue: {url_queue}\n")
#             print(f"End of layer: {nested_layer}\n")

#             if len(url_queue) == 0:
#                 break

#             nested_layer = nested_layer + 1

#     return url_queue


# ==================================================================================================================================================
#                                                         Validators
# ==================================================================================================================================================


def is_url(string):
    # url_pattern = r"^(http|https|ftp)://[^\s/$.?#].[^\s]*$"
    url_pattern = r"^(http|https|ftp)?(:\/\/)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})([^\s]*)$"
    return re.match(url_pattern, string) is not None


def add_protocol2url(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        # print(f"URL with protocol is: {url}")
    # if not url.endswith("/"):
    #     url += "/"
    return url
