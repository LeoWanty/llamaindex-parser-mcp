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


def respond(message, chat_history, selected_resources):
    bot_answer, nodes = rag_server.query_and_get_nodes(
        message, allowed_files=selected_resources
    )

    nb_nodes = f"Nombre de noeuds récupérés: {len(nodes)}"
    chat_history.append({"role": "user", "content": message})
    chat_history.append({"role": "assistant", "content": bot_answer})
    formatted_nodes = format_retrieved_nodes(nodes)
    return "", chat_history, f"{nb_nodes}\n\n{formatted_nodes}"


def upload_file_handler(temp_file):
    if temp_file is None:
        return "No file uploaded.", gr.update()

    status_message = rag_server.add_markdown_file(temp_file.name)
    updated_choices = rag_server.list_markdown_files()
    return status_message, gr.update(choices=updated_choices, value=updated_choices)


def check_all():
    return gr.update(value=rag_server.list_markdown_files())


def uncheck_all():
    return gr.update(value=[])


def delete_files_handler(files_to_delete):
    if not files_to_delete:
        gr.Warning("No files selected for deletion.")
        return "No files selected for deletion.", gr.update()

    status_message = rag_server.delete_markdown_files(files_to_delete)
    updated_choices = rag_server.list_markdown_files()
    return status_message, gr.update(choices=updated_choices, value=updated_choices)


with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("# RAG Pipeline Explorer")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion("Available Resources"):
                with gr.Row():
                    check_all_btn = gr.Button("Check All")
                    uncheck_all_btn = gr.Button("Uncheck All")

                resource_checklist = gr.CheckboxGroup(
                    choices=rag_server.list_markdown_files(),
                    label="Select resources to include in the RAG pipeline",
                    value=rag_server.list_markdown_files(),
                )

                delete_btn = gr.Button("Delete Selected Files", variant="stop")
                delete_status = gr.Markdown()

            with gr.Accordion("Add New Resource", open=True):
                file_uploader = gr.File(
                    label="Upload a Markdown File", file_types=[".md"], type="filepath"
                )
                upload_status = gr.Markdown()
                file_uploader.upload(
                    upload_file_handler,
                    inputs=[file_uploader],
                    outputs=[upload_status, resource_checklist],
                )

        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="RAG Chatbot", type="messages")
            msg = gr.Textbox(label="Ask a question about your documents")

            with gr.Accordion("Retrieved Elements", open=False):
                retrieved_nodes_display = gr.Markdown(
                    "Retrieved nodes will be displayed here."
                )

            msg.submit(
                respond,
                [msg, chatbot, resource_checklist],
                [msg, chatbot, retrieved_nodes_display],
            )
            check_all_btn.click(check_all, [], resource_checklist)
            uncheck_all_btn.click(uncheck_all, [], resource_checklist)
            delete_btn.click(
                delete_files_handler,
                inputs=[resource_checklist],
                outputs=[delete_status, resource_checklist],
            )


def main():
    """Launches the Gradio interface."""
    demo.launch()


if __name__ == "__main__":
    main()
