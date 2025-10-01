import logging
import re
import requests
from urllib.parse import urlparse, unquote, urljoin

from bs4 import BeautifulSoup
from pydantic import BaseModel


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


class WebsiteCrawler(BaseModel):
    base_url: str
    max_depth: int = 2
    visited: set = set()
    links: set = set()

    def _crawl_and_gather_links(self, url: str) -> set[str]:
        """
        For one url, get all new links not previously visited.
        Args:
            url: url to crawl

        Returns:
            set of new links
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.warning(f"Error fetching {url}: {e}")
            return set()

        soup = BeautifulSoup(response.text, "html.parser")

        netloc = urlparse(url).netloc
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href")
            if not href or href.startswith("#"):
                continue

            # Handle relative paths
            link_url = urljoin(url, href)
            parsed_url = urlparse(link_url)
            full_url = parsed_url._replace(fragment="").geturl()

            # Check if the link is within the same domain
            if urlparse(full_url).netloc == netloc:
                links.add(full_url)

        return links

    def _iterative_crawl(self, current_url: str, current_depth=0) -> None:
        """
        Recursively explores a website from a base URL to a specified maximum depth,
        collecting all unique internal links.

        Args:
            current_url: url to explore
            current_depth: current depth of exploration

        Returns:
            None, updates self.links and self.visited with new links found during the crawl.
        """
        # Init
        self.links.add(current_url)  # The current URL is of interest
        _links = self._crawl_and_gather_links(current_url)
        self.links.update(_links)
        self.visited.add(current_url)

        # Iterations
        for link in _links:
            if current_depth < self.max_depth and link not in self.visited:
                self._iterative_crawl(link, current_depth + 1)

    def crawl(self) -> set[str]:
        self._iterative_crawl(self.base_url)
        return self.links
