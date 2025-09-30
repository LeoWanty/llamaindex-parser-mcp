import logging
import urllib.request
from pydantic import BaseModel

from html2text import HTML2Text


class PageDownloader(BaseModel):
    url: str
    encoding: str = "utf-8"

    @property
    def html_content(self) -> str:
        logging.info(f"Downloading page: {self.url}")
        return self._download_page()

    @property
    def markdown_content(self) -> str:
        return self._convert_to_markdown()

    def _download_page(self) -> str:
        """Downloads the HTML content of the page."""
        try:
            with urllib.request.urlopen(self.url) as response:
                if response.getcode() == 200:
                    return response.read().decode(self.encoding)
                else:
                    print(
                        f"Error: Failed to download page, status code: {response.getcode()}"
                    )
        except Exception as e:
            print(f"An error occurred: {e}")

    def _convert_to_markdown(self):
        """Converts the HTML content to Markdown."""
        return HTML2Text().handle(self.html_content)
