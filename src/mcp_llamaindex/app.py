import gradio as gr
from mcp_llamaindex.rag_pipeline import DirectoryRagServer

# Initialize the RAG server
rag_server = DirectoryRagServer()


def format_retrieved_nodes(nodes: list[dict]) -> str:
    """
    Formats the retrieved nodes for display.
    """
    if not nodes:
        return "No nodes retrieved."

    formatted_nodes = []
    for node in nodes:
        node_score = node.get("score", "N/A")
        node_content = node.get("node", {}).get("text", "No content available")
        metadata = node.get("node", {}).get("metadata", {})
        file_name = metadata.get("file_name", "N/A")

        formatted_nodes.append(
            f"**File:** `{file_name}`  |  Node score: {node_score}\n\n---\n\n```\n{node_content}\n```"
        )

    return "\n\n".join(formatted_nodes)


def get_available_resources():
    """
    Gets the list of available resources from the RAG server.
    """
    return rag_server.list_markdown_files()


with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("# RAG Pipeline Explorer")

    retrieved_nodes_state = gr.State([])

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion("Available Resources"):
                resource_checklist = gr.CheckboxGroup(
                    choices=get_available_resources(),
                    label="Select resources to include in the RAG pipeline",
                    value=get_available_resources(),  # by default, all are selected
                )

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="RAG Chatbot", type="messages")
            msg = gr.Textbox(label="Ask a question about your documents")

            with gr.Accordion("Retrieved Elements", open=False):
                retrieved_nodes_display = gr.Markdown(
                    "Retrieved nodes will be displayed here."
                )

            def respond(message, chat_history):
                bot_answer, nodes = rag_server.query_and_get_nodes(message)
                nb_nodes = f"Nombre de noeuds récupérés: {len(nodes)}"
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": bot_answer})
                formatted_nodes = format_retrieved_nodes(nodes)
                return "", chat_history, f"{nb_nodes}\n\n{formatted_nodes}"

            msg.submit(respond, [msg, chatbot], [msg, chatbot, retrieved_nodes_display])


def main():
    """Launches the Gradio interface."""
    demo.launch()


if __name__ == "__main__":
    main()
