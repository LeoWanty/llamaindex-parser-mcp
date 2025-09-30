import pytest
import requests
from unittest.mock import MagicMock, patch

from mcp_llamaindex.utils.crawler import url_to_filename, explore_website

@pytest.mark.parametrize("url, expected_filename", [
    ("https://example.com", "example-com"),
    ("https://example.com/path/to/page", "example-com_path_to_page"),
    ("https://example.com/path/with%20spaces", "example-com_path_with-spaces"),
    ("https://example.com/path?query=param", "example-com_path"),
    ("http://localhost:8000", "localhost:8000"),
    ("https://example.com/", "example-com"),
    ("https://example.com/page.html", "example-com_page-html"),
    ("https://example.com/a/b.c/d.e.f", "example-com_a_b-c_d-e-f"),
    ("", "index"),
])
def test_url_to_filename(url, expected_filename):
    assert url_to_filename(url) == expected_filename

@patch('requests.get')
def test_explore_website_single_level(mock_get):
    """Tests that explore_website correctly extracts links from a single page."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <a href="/page1">Page 1</a>
            <a href="https://example.com/page2">Page 2</a>
            <a href="https://external.com/page3">External</a>
            <a href="#section">Section anchor</a>
        </body>
    </html>
    """
    mock_get.return_value = mock_response

    hierarchy = explore_website("https://example.com", max_depth=0)

    expected_links = sorted([
        "https://example.com/page1",
        "https://example.com/page2"
    ])

    assert list(hierarchy.keys()) == ["https://example.com"]
    assert hierarchy["https://example.com"]["links"] == expected_links
    assert hierarchy["https://example.com"]["children"] == {}
    mock_get.assert_called_once_with("https://example.com")


def mock_requests_get(url, **kwargs):
    responses = {
        "https://example.com/": MagicMock(status_code=200, text='<html><body><a href="/page1">Page 1</a></body></html>'),
        "https://example.com/page1": MagicMock(status_code=200, text='<html><body><a href="/">Home</a><a href="/page2">Page 2</a></body></html>'),
        "https://example.com/page2": MagicMock(status_code=200, text='<html><body><p>No links here.</p></body></html>')
    }

    # Normalize URL to handle trailing slashes
    normalized_url = url
    if not url.endswith('/') and "page" not in url:
        normalized_url = url + "/"

    return responses.get(normalized_url, MagicMock(status_code=404, text="Not Found"))


@patch('requests.get', side_effect=mock_requests_get)
def test_explore_website_recursive(mock_get):
    """Tests the recursive exploration of the website."""
    hierarchy = explore_website("https://example.com/", max_depth=2)

    expected_hierarchy = {
        "https://example.com/": {
            "links": ["https://example.com/page1"],
            "children": {
                "https://example.com/page1": {
                    "links": sorted(["https://example.com/", "https://example.com/page2"]),
                    "children": {
                         "https://example.com/page2": {
                            "links": [],
                            "children": {}
                        }
                    }
                }
            }
        }
    }
    assert hierarchy == expected_hierarchy


@patch('requests.get')
def test_explore_website_avoids_cycles(mock_get):
    """Tests that the crawler avoids getting into infinite loops."""
    responses = {
        "https://example.com/": MagicMock(status_code=200, text='<html><body><a href="/page1">Page 1</a></body></html>'),
        "https://example.com/page1": MagicMock(status_code=200, text='<html><body><a href="/">Home</a></body></html>'),
    }
    mock_get.side_effect = lambda url, **kwargs: responses.get(url, MagicMock(status_code=404, text="Not Found"))

    hierarchy = explore_website("https://example.com/", max_depth=3) # High depth to test cycle break

    expected_hierarchy = {
        "https://example.com/": {
            "links": ["https://example.com/page1"],
            "children": {
                "https://example.com/page1": {
                    "links": ["https://example.com/"],
                    "children": {} # Should not re-crawl example.com
                }
            }
        }
    }
    assert hierarchy == expected_hierarchy


@patch('requests.get')
def test_explore_website_handles_request_error(mock_get):
    """Tests that the function handles request errors gracefully."""
    mock_get.side_effect = requests.exceptions.RequestException("Test connection error")
    hierarchy = explore_website("https://example.com")
    assert hierarchy == {}