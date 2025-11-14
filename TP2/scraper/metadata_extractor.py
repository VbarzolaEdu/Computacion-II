from bs4 import BeautifulSoup

def extract_metadata(html: str) -> dict:
    """
    Extrae metadatos relevantes desde el HTML.
    Incluye meta estándar, Open Graph y Twitter Cards.
    """
    soup = BeautifulSoup(html, "lxml")

    meta = {
        "description": None,
        "keywords": None,
        "author": None,
        "og_title": None,
        "og_description": None,
        "og_image": None,
        "twitter_title": None,
        "twitter_description": None,
    }

    # Meta por nombre
    for name in ["description", "keywords", "author"]:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            meta[name] = tag.get("content")

    # Open Graph (og:)
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_desc = soup.find("meta", attrs={"property": "og:description"})
    og_img = soup.find("meta", attrs={"property": "og:image"})

    if og_title:
        meta["og_title"] = og_title.get("content")
    if og_desc:
        meta["og_description"] = og_desc.get("content")
    if og_img:
        meta["og_image"] = og_img.get("content")

    # Twitter Cards
    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    tw_desc = soup.find("meta", attrs={"name": "twitter:description"})

    if tw_title:
        meta["twitter_title"] = tw_title.get("content")
    if tw_desc:
        meta["twitter_description"] = tw_desc.get("content")

    return meta
