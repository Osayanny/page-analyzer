from bs4 import BeautifulSoup
from urllib.parse import urlparse


def parse_url(url):
    parsed_url = urlparse(url)
    name = f'{parsed_url.scheme}://{parsed_url.netloc}'
    return name


def parse_response(response):

    tags = {}
    
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    h1 = soup.find('h1')
    title = soup.find('title')
    description = soup.find('meta', {'name': 'description'})

    if title:
        tags['title'] = title.text
    if h1:
        tags['h1'] = h1.text
    if description:
        tags['description'] = description.get('content')

    return tags