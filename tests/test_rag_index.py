import pytest
from pathlib import Path

from mcp_llamaindex.rag_pipeline import DirectoryRagServer, RagConfig


@pytest.fixture
def rag_server(tmp_path: Path) -> DirectoryRagServer:
    """Fixture to create a DirectoryRagServer instance with a temporary data directory."""
    # Create a temporary data directory and some dummy markdown files
    data_dir = tmp_path / "md_documents"
    data_dir.mkdir()
    (data_dir / "file1.md").write_text("# File 1 Content")
    (data_dir / "file2.md").write_text("# File 2 Content")

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