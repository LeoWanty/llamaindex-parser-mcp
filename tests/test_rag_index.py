import pytest
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

from mcp_llamaindex.rag_pipeline import DirectoryRagServer, RagConfig


@pytest.fixture
def rag_server(tmp_path: Path) -> DirectoryRagServer:
    """Fixture to create a DirectoryRagServer instance with a temporary data directory."""
    # Create a temporary data directory and some dummy markdown files
    data_dir = tmp_path / "md_documents"
    data_dir.mkdir()
    (data_dir / "file1.md").write_text("# File 1 Content")
    (data_dir / "file2.md").write_text("# File 2 Content")
    (data_dir / "not_a_markdown_file.txt").write_text("This is not a markdown file.")

    # Create a temporary persist directory
    persist_dir = tmp_path / "vector_store"
    persist_dir.mkdir()

    # Instantiate the server
    rag_config = RagConfig(persist_dir=persist_dir, data_dir=data_dir)
    server = DirectoryRagServer(rag_config=rag_config)

    # Ensure the index is created for the test
    _ = server.index

    yield server


def test_get_indexed_files(rag_server: DirectoryRagServer):
    """Test that get_indexed_files returns the correct list of indexed files."""
    indexed_files = rag_server.get_indexed_files()

    assert isinstance(indexed_files, list)
    assert len(indexed_files) == 2
    assert "file1.md" in indexed_files
    assert "file2.md" in indexed_files


def test_list_markdown_files(rag_server: DirectoryRagServer):
    """Test that list_markdown_files returns only markdown files."""
    markdown_files = rag_server.list_markdown_files()
    assert isinstance(markdown_files, list)
    assert len(markdown_files) == 2
    assert "file1.md" in markdown_files
    assert "file2.md" in markdown_files
    assert "not_a_markdown_file.txt" not in markdown_files


def test_query_and_get_nodes_mocked(rag_server: DirectoryRagServer, monkeypatch):
    """Test query_and_get_nodes with a mocked query engine."""
    # Mock the response from the query engine
    mock_response = MagicMock()
    mock_response.source_nodes = [
        MagicMock(
            node=MagicMock(
                metadata={"file_name": "file1.md"}, get_content=lambda: "content1"
            ),
            score=0.9,
        ),
        MagicMock(
            node=MagicMock(
                metadata={"file_name": "file2.md"}, get_content=lambda: "content2"
            ),
            score=0.8,
        ),
    ]
    mock_response.__str__.return_value = "Mocked answer"

    # Mock the query engine itself
    mock_query_engine = MagicMock()
    mock_query_engine.query.return_value = mock_response

    # Use monkeypatch to replace the property with our mock
    monkeypatch.setattr(
        DirectoryRagServer,
        "rag_query_engine",
        PropertyMock(return_value=mock_query_engine),
    )

    answer, nodes = rag_server.query_and_get_nodes("test query")

    assert answer == "Mocked answer"
    assert len(nodes) == 2
    assert nodes[0]["score"] == 0.9
    assert nodes[1]["node"]["metadata"]["file_name"] == "file2.md"
    assert nodes[1]["node"]["text"] == "content2"

    # Verify that the query method was called
    mock_query_engine.query.assert_called_once_with("test query")


@patch("mcp_llamaindex.rag_pipeline.WebsiteCrawler")
def test_get_website_links(mock_crawler, rag_server: DirectoryRagServer):
    """Test that get_website_links returns a sorted list of unique links."""
    mock_instance = mock_crawler.return_value
    mock_instance.crawl.return_value = {
        "http://example.com",
        "http://example.com/page1",
        "http://example.com/page2",
        "http://example.com/page1",  # Duplicate
    }

    links = rag_server.get_website_links("http://example.com")

    assert links == [
        "http://example.com",
        "http://example.com/page1",
        "http://example.com/page2",
    ]
    mock_crawler.assert_called_once_with(base_url="http://example.com", max_depth=1)
    mock_instance.crawl.assert_called_once()


@patch("mcp_llamaindex.rag_pipeline.PageDownloader")
@patch("mcp_llamaindex.rag_pipeline.SimpleDirectoryReader")
@patch("mcp_llamaindex.rag_pipeline.url_to_filename")
def test_crawl_and_download_pages(
    mock_url_to_filename,
    mock_reader,
    mock_downloader,
    rag_server: DirectoryRagServer,
    tmp_path: Path,
):
    """Test downloading pages, saving them, and adding them to the index."""
    directory_name = "test_downloads"
    pages_to_download = ["http://example.com/page1", "http://example.com/page2"]

    # Mock url_to_filename to return predictable filenames
    mock_url_to_filename.side_effect = lambda url: url.split("/")[-1]

    # Mock PageDownloader
    mock_downloader_instance = mock_downloader.return_value
    mock_downloader_instance.save_as_markdown.return_value = None

    # Mock SimpleDirectoryReader
    mock_document = MagicMock()
    mock_document.metadata = {}
    mock_reader.return_value.load_data.return_value = [mock_document]

    # Mock the index's insert method
    rag_server.index.insert = MagicMock()

    result = rag_server.crawl_and_download_pages(directory_name, pages_to_download)

    assert "Successfully downloaded and indexed 2 page(s)." in result
    assert mock_downloader.call_count == 2
    assert mock_reader.return_value.load_data.call_count == 2
    assert rag_server.index.insert.call_count == 2

    # Check that files were "saved" in the correct directory
    download_dir = rag_server.rag_config.data_dir / directory_name
    mock_downloader_instance.save_as_markdown.assert_any_call(
        download_dir / "page1.md"
    )
    mock_downloader_instance.save_as_markdown.assert_any_call(
        download_dir / "page2.md"
    )

    # Check that the document metadata was updated
    assert mock_document.metadata["source_directory"] == directory_name