import re
from urllib.parse import urlparse, unquote


def url_to_filename(url: str) -> str:
    """Converts a URL to a human-readable filename.

    Args:
        url: The URL to convert.

    Returns:
        A string that can be used as a filename.
    """
    parsed_url = urlparse(url)
    # Combine network location (domain), path and query
    path = unquote(parsed_url.path)
    filename = parsed_url.netloc + path
    # Do not take query parameters into account

    # Replace / and invalid filename characters (like ?) with underscores.
    filename = re.sub(r'[\\/*?"<>|]', "_", filename)

    # Replace path separators and other common separators with hyphens
    filename = re.sub(r"[\s/.]+", "-", filename)

    # Remove trailing hyphens or underscores
    filename = filename.strip("-_")

    # Ensure the filename is not empty
    if not filename:
        return "index"

    return filename


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def explore_website(base_url: str, max_depth: int = 2, visited: set = None) -> dict:
    """
    Recursively explores a website from a base URL to a specified maximum depth,
    collecting all unique internal links.

    Args:
        base_url (str): The starting URL to explore.
        max_depth (int): The maximum depth of exploration.
        visited (set): A set of already visited URLs to avoid re-crawling.

    Returns:
        A dictionary representing the site hierarchy.
    """
    if visited is None:
        visited = set()

    if max_depth < 0 or base_url in visited:
        return {}

    visited.add(base_url)
    netloc = urlparse(base_url).netloc

    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        print(f"Error fetching {base_url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')

    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href')
        if not href or href.startswith('#'):
            continue

        # Join the URL to handle relative paths
        full_url = urljoin(base_url, href)
        # Parse the URL and remove fragment identifiers
        parsed_url = urlparse(full_url)
        full_url = parsed_url._replace(fragment="").geturl()

        # Check if the link is within the same domain
        if urlparse(full_url).netloc == netloc:
            links.add(full_url)

    sorted_links = sorted(list(links))
    hierarchy = {base_url: {"links": sorted_links, "children": {}}}

    if max_depth > 0:
        for link in sorted_links:
            if link != base_url:
                # Recursively explore the link
                child_hierarchy = explore_website(link, max_depth - 1, visited)
                if child_hierarchy:
                    hierarchy[base_url]["children"].update(child_hierarchy)

    return hierarchy