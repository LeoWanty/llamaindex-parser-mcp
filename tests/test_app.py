from unittest.mock import patch
from mcp_llamaindex.app import format_retrieved_nodes, respond


def test_format_retrieved_nodes_empty():
    """Test formatting with no nodes."""
    assert format_retrieved_nodes([]) == "No nodes retrieved."


def test_format_retrieved_nodes_with_content():
    """Test formatting with a list of nodes."""
    nodes = [
        {
            "score": 0.95,
            "node": {
                "text": "This is the content of the first node.",
                "metadata": {"file_name": "doc1.md"},
            },
        },
        {
            "score": 0.88,
            "node": {
                "text": "This is the content of the second node.",
                "metadata": {"file_name": "doc2.md"},
            },
        },
    ]
    formatted_output = format_retrieved_nodes(nodes)
    assert "**File:** `doc1.md`" in formatted_output
    assert "Node score: 0.95" in formatted_output
    assert "This is the content of the first node." in formatted_output
    assert "**File:** `doc2.md`" in formatted_output
    assert "Node score: 0.88" in formatted_output
    assert "This is the content of the second node." in formatted_output


def test_format_retrieved_nodes_missing_keys():
    """Test formatting with nodes that have missing keys."""
    nodes = [{"node": {"text": "Content without score or file name."}}]
    formatted_output = format_retrieved_nodes(nodes)
    assert "**File:** `N/A`" in formatted_output
    assert "Node score: N/A" in formatted_output
    assert "Content without score or file name." in formatted_output


@patch("mcp_llamaindex.app.rag_server")
def test_respond_function(mock_rag_server):
    """Test the respond function that powers the chatbot."""
    # Mock the return value of the RAG server's query method
    mock_answer = "This is a mock answer."
    mock_nodes = [
        {
            "score": 0.99,
            "node": {"text": "Mock content.", "metadata": {"file_name": "mock_doc.md"}},
        }
    ]
    mock_rag_server.query_and_get_nodes.return_value = (mock_answer, mock_nodes)

    # Initial state
    chat_history = []
    message = "What is a mock test?"

    # Call the respond function
    new_msg, updated_chat_history, retrieved_display = respond(
        message, chat_history, selected_resources=None
    )

    # Assertions
    assert new_msg == ""
    assert len(updated_chat_history) == 2
    assert updated_chat_history[0] == {"role": "user", "content": message}
    assert updated_chat_history[1] == {"role": "assistant", "content": mock_answer}
    assert "Nombre de noeuds récupérés: 1" in retrieved_display
    assert "**File:** `mock_doc.md`" in retrieved_display
    assert "Node score: 0.99" in retrieved_display
    assert "Mock content." in retrieved_display
    # respond function pass selected_resources to allowed_files arg of the method
    mock_rag_server.query_and_get_nodes.assert_called_once_with(
        message, allowed_files=None
    )
