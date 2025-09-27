import gradio as gr
import json
from mcp_llamaindex.rag_pipeline import DirectoryRagServer

# Initialize the RAG server
rag_server = DirectoryRagServer()

def chat_and_retrieve(message, history):
    """
    Main chat function that interacts with the RAG pipeline
    and returns both the response and the retrieved nodes.
    """
    response, nodes = rag_server.query_and_get_nodes(message)
    # Storing nodes in a temporary state for the other function to access
    return response, nodes

def format_retrieved_nodes(nodes):
    """
    Formats the retrieved nodes for display.
    """
    if not nodes:
        return "No nodes retrieved."

    formatted_nodes = []
    for node in nodes:
        # Each 'node' is a dictionary. We'll format it for display.
        # The actual content is in node['node']['text']
        node_content = node.get('node', {}).get('text', 'No content available')
        metadata = node.get('node', {}).get('metadata', {})
        file_name = metadata.get('file_name', 'N/A')

        formatted_nodes.append(f"**File:** `{file_name}`\n\n---\n\n```\n{node_content}\n```")

    return "\n\n".join(formatted_nodes)

def chat_interface_fn(message, history):
    """
    Wrapper function for the chat interface to handle the two outputs.
    """
    response, nodes = chat_and_retrieve(message, history)
    # We need a way to pass the nodes to the retrieved_nodes_display
    # We can use a global variable or a more sophisticated state management if needed
    # For simplicity, let's just return the formatted nodes as part of the chatbot response for now.
    # A better approach would be to update the retrieved_nodes_display directly.

    # This is a trick to update another component.
    # The ChatInterface only expects a single string response.
    # We'll need to restructure the app to handle this properly.

    # Let's restructure the app to handle this.
    return response

def get_available_resources():
    """
    Gets the list of available resources from the RAG server.
    """
    return rag_server.list_markdown_files()

with gr.Blocks() as demo:
    gr.Markdown("# RAG Pipeline Explorer")

    retrieved_nodes_state = gr.State([])

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Accordion("Available Resources"):
                resource_checklist = gr.CheckboxGroup(
                    choices=get_available_resources(),
                    label="Select resources to include in the RAG pipeline",
                    value=get_available_resources() # by default, all are selected
                )

        with gr.Column(scale=3):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Ask a question about your documents")

            with gr.Accordion("Retrieved Elements", open=False):
                retrieved_nodes_display = gr.Markdown("Retrieved nodes will be displayed here.")

            def respond(message, chat_history):
                bot_message, nodes = chat_and_retrieve(message, chat_history)
                chat_history.append((message, bot_message))
                formatted_nodes = format_retrieved_nodes(nodes)
                return "", chat_history, formatted_nodes

            msg.submit(respond, [msg, chatbot], [msg, chatbot, retrieved_nodes_display])

def main():
    """Launches the Gradio interface."""
    demo.launch()

if __name__ == "__main__":
    main()