import logging
import urllib.request
from pathlib import Path

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
                    logging.warning(
                        f"Failed to download page, status code: {response.getcode()}"
                    )
        except Exception as e:
            logging.warning(f"An error occurred: {e}")

    def _convert_to_markdown(self):
        """Converts the HTML content to Markdown."""
        return HTML2Text().handle(self.html_content)

    def save_as_markdown(self, output_path: str | Path) -> None:
        """Saves the Markdown content to a file.

        Args:
            output_path (str): The path to save the markdown file.
        """
        output_path = Path(output_path)
        if output_path.suffix != ".md":
            raise ValueError(
                f"Output file must be a Markdown file with the .md extension. Got {output_path.suffix} instead."
            )

        output_path.parent.mkdir(exist_ok=True, parents=True)
        output_path.write_text(self.markdown_content, encoding="utf-8")
        logging.info(f"Page content saved as Markdown to {output_path}")
