#!env python3
###################################
#
# Web crawler to find letter frequencies
#
###################################
import requests
from bs4 import BeautifulSoup
import collections
import urllib
import string

#
# apt-get install python3-bs4 python3-requests
# or
# pip install beautifulsoup4
#

# todo: Find what language the page is in and have separate frequencies for different languages

# ---------------------------------------------------


def browse(url, max_depth, max_pages, frequencies = {}, seen_urls = []):
    print("Pages left {} Depth {}, Url:{}".format(max_pages, max_depth, url))

    if max_pages <= 0:
        return frequencies

    if url in seen_urls:
        return frequencies

    seen_urls.append(url)

    if max_depth <= 0:
        return frequencies

    parsed_url = urllib.parse.urlparse(url)

    r = requests.get(url)
    if not r.ok:
        return frequencies

    if r.headers['content-type'] and 'text/html' not in r.headers['content-type']:
        return frequencies

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
        npages = 0

        for link in links:
            if 'href' in link.attrs:
                href = link.attrs['href']
                if href.startswith('/'):
                    npages += 1
                    if npages > max_pages:
                        break
                    appended_frequencies = browse(parsed_url.scheme + '://' + parsed_url.netloc + href,
                                                  max_depth - 1, max_pages - npages, appended_frequencies, seen_urls)
                elif href.startswith('http'):
                    npages += 1
                    if npages > max_pages:
                        break
                    appended_frequencies = browse(href, max_depth - 1, max_pages - npages,
                                                  appended_frequencies, seen_urls)

    return appended_frequencies


# -------------------------------------------------------

frequencies = browse('https://en.wikipedia.org/wiki/Main_Page', 2, 5)
print(frequencies)

only_letters = {key: value for (key, value) in frequencies.items()
                if key not in string.punctuation and key not in string.whitespace}

only_capitals = {item: (frequencies[item] if item in frequencies else 0)
                 + (frequencies[item.lower()] if item.lower() in frequencies else 0)
                 for item in string.ascii_uppercase}

total_letters = sum(only_letters.values())
only_letters = {key: float(value) * 100 / total_letters for (key, value) in only_letters.items()}

total_capitals = sum(only_capitals.values())
only_capitals = {key: float(value) * 100 / total_capitals for (key, value) in only_capitals.items()}

print(only_capitals)
print(only_letters)

