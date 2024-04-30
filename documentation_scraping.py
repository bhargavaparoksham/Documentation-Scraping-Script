import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse

# List of allowed base URLs
allowed_bases = {
    'https://support.gitcoin.co',
    'https://www.gitcoin.co',
    'https://docs.passport.gitcoin.co',
    'https://allo.gitcoin.co',
    'https://docs.allo.gitcoin.co'
}

def is_allowed_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url in allowed_bases

def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # You might need to adjust the tag & class to find links correctly
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if is_allowed_url(urljoin(url, a['href']))]
    return links


def scrape_page(url, visited):
    if url in visited or not is_allowed_url(url):
        return
    visited.add(url)

    print(f"Scraping {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Adjust the tag & class to match the content sections
    content = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    with open('gitcoin_documentation_output.txt', 'a', encoding='utf-8') as file:
        for element in content:
            if element.name == 'h1':
                file.write('\n' + element.text + '\n')
            elif element.name in ['h2', 'h3', 'h4', 'h5', 'h6']:
                file.write(element.text + '\n')
            elif element.name == 'p':
                file.write(element.text + '\n')
            elif element.name == 'a':
                # Output format for links: text followed by URL
                file.write(element.text + ' - ' + element.get('href', '') + '\n')

    # Extract new links and recurse
    links = extract_links(url)
    for link in links:
        if link not in visited:
            scrape_page(link, visited)

# Start scraping from the main page
initial_url = 'https://support.gitcoin.co/gitcoin-knowledge-base'
visited_urls = set()
scrape_page(initial_url, visited_urls)
