import requests
from bs4 import BeautifulSoup
import collections
import urllib


#
# apt-get install python3-bs4
# or
# pip install beautifulsoup4
#

# ---------------------------------------------------


def browse(url, max_depth, frequencies = {}, seen_urls = []):
    print("Depth {}, Url:{}".format(max_depth, url))

    if url in seen_urls:
        return frequencies, seen_urls

    appended_urls = seen_urls.append(url)

    if max_depth <= 0:
        return frequencies, appended_urls

    parsed_url = urllib.parse.urlparse(url)

    r = requests.get(url)
    if not r.ok:
        return frequencies, appended_urls

    if r.headers['content-type'] and 'text/html' not in r.headers['content-type']:
        return frequencies, appended_urls

    soup = BeautifulSoup(r.content, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text(" ", strip=True)
    page_frequencies = collections.Counter(text)

    appended_frequencies = {key: (value + frequencies[key] if key in frequencies else value)
                            for (key, value) in page_frequencies.items()}

    if max_depth > 1:
        links = soup.find_all('a')
        print("{} links".format(len(links)))

        for link in links:
            if 'href' in link.attrs:
                href = link.attrs['href']
                if href.startswith('/'):
                    appended_frequencies, appended_urls = browse(parsed_url.scheme + '://' + parsed_url.netloc + href,
                                                  max_depth - 1, appended_frequencies, appended_urls)
                elif href.startswith('http'):
                    appended_frequencies, appended_urls = browse(href, max_depth - 1,
                                                                 appended_frequencies, appended_urls)

    return appended_frequencies, appended_urls


# -------------------------------------------------------

frequencies, urls = browse('https://en.wikipedia.org/wiki/Main_Page', 2)
print(frequencies)
