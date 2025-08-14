import asyncio
import json

from mcp_llamaindex.server import load_markdown_data

from conftest import GENERATED_EXAMPLES_DIR

def test_load_markdown_data_parses_content():
    # Call the tool
    a_result = load_markdown_data(GENERATED_EXAMPLES_DIR / "example_1.md")
    result = json.loads(asyncio.run(a_result))

    # Assert the result
    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["text"].startswith("# A Guide to the Solar System")
    assert all(p["text"].startswith("#") for p in result), "Expected all paragraphs are md titles, starting with #"
