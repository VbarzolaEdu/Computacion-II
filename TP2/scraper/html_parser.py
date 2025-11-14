# scraper/html_parser.py
from bs4 import BeautifulSoup
from scraper.metadata_extractor import extract_metadata

def parse_html(html: str) -> dict:
    soup = BeautifulSoup(html, 'lxml')

    # Título
    title = soup.title.string if soup.title else None

    # Links
    links = [a['href'] for a in soup.find_all('a', href=True)]

    # Meta tags
    meta_tags = extract_metadata(html)
    for tag in soup.find_all('meta'):
        key = tag.get('name') or tag.get('property')
        if key and tag.get('content'):
            meta_tags[key] = tag.get('content')

    # Encabezados
    headers = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}

    # Imágenes
    images_count = len(soup.find_all('img'))

    return {
        'title': title,
        'links': links,
        'meta_tags': meta_tags,
        'structure': headers,
        'images_count': images_count
    }
