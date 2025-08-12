import pytest
import asyncio
import json
from server import load_markdown_data

def test_load_markdown_data_parses_content(tmp_path):
    # Create a dummy markdown file
    md_content = "# Title\n\nSome text."
    md_file = tmp_path / "test.md"
    md_file.write_text(md_content)

    # Call the tool
    result_json = asyncio.run(load_markdown_data(str(tmp_path)))
    result = json.loads(result_json)

    # Assert the result
    assert isinstance(result, list)
    assert len(result) > 0
    # MarkdownNodeParser creates a node for the header and another for the text
    # The exact number of nodes can vary based on the parser's logic, so we check for content
    all_text = "".join([item["text"] for item in result])
    assert "Title" in all_text
    assert "Some text" in all_text
