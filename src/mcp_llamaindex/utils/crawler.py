import logging
import re
import requests
from urllib.parse import urlparse, unquote, urljoin

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field


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
    """
    Crawl a website to get all internal links up to a specific depth.
    """

    base_url: str
    max_depth: int = Field(
        0,
        ge=0,
        description="Maximum depth of exploration. "
        "0 for crawling targeted page only. "
        "1 for crawling links referenced from the targeted page. "
        "2 for crawling links referenced in second depth level. etc.",
    )
    css_selector: str | None = Field(
        None,
        description="CSS selector to extract the links from the page. "
        "If None or empty string, extract from the full page.",
    )
    only_domain_links: bool = Field(
        True,
        description="Only include links within the same domain as the base URL.",
    )

    _visited: set = set()
    _links: set = set()

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
        if self.css_selector:
            selected_section = soup.select_one(self.css_selector)
            if selected_section:
                soup = selected_section
            else:
                logging.warning(
                    f"The CSS selector {self.css_selector} did not match any Tag from {url}."
                    "Searching links from the full page instead."
                )

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

            if not self.only_domain_links or urlparse(full_url).netloc == netloc:
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
        self._links.add(current_url)  # The current URL is of interest
        _links = self._crawl_and_gather_links(current_url)
        self._links.update(_links)
        self._visited.add(current_url)

        # Iterations
        for link in _links:
            if current_depth < self.max_depth and link not in self._visited:
                self._iterative_crawl(link, current_depth + 1)

    def crawl(self) -> set[str]:
        self._iterative_crawl(self.base_url)
        return self._links


def get_website_links(url: str, max_depth: int = 1) -> list[str]:
    """
    Crawls a website to get all internal links up to a specific depth.

    Args:
        url (str): The base URL to start crawling from.
        max_depth (int): The maximum depth to crawl.

    Returns:
        list[str]: A list of unique internal links found on the website.
    """
    if not url:
        return []
    crawler = WebsiteCrawler(base_url=url, max_depth=max_depth)
    links = crawler.crawl()
    return sorted(list(links))
