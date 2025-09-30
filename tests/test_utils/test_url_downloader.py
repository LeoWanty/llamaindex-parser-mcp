from unittest.mock import patch, MagicMock
from mcp_llamaindex.utils.downloader import PageDownloader


@patch("urllib.request.urlopen")
def test_save_as_markdown(mock_urlopen, tmp_path):
    url = "http://example.com"
    output_file = tmp_path / "test_page.md"
    html_content = "<html><body><h1>Hello</h1><p>This is a test.</p></body></html>"
    expected_markdown = "Hello\n=====\n\nThis is a test."

    # Mock the response from urlopen
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.return_value = html_content.encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    downloader = PageDownloader(url=url)
    downloader.save_as_markdown(output_file)
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")
    assert content.strip() == expected_markdown.strip()
