from flask import Blueprint, request, jsonify
import os
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import AzureOpenAIEmbeddings
from utility.embedder import generate_embeddings 
from utility.auth_utils import token_required
from sqlalchemy import text 
from utility.db_config import engine


chat_blueprint = Blueprint("chat", __name__)

# Store user conversation per session
session_contexts = {}

# Load environment variables
load_dotenv()

# Azure OpenAI setup
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
chat_deployment = os.getenv("AZURE_DEPLOYMENT_NAME")
embedding_deployment = "embedding-ada" 

# Initialize Flask app
app = Flask(__name__)

# Load Chroma DB
CHROMA_DIR = "chroma_store"
embedding_model = AzureOpenAIEmbeddings(
    azure_deployment=embedding_deployment,
    openai_api_version=openai.api_version
)
vector_store = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_model)



@chat_blueprint.route("/api/chat", methods=["POST"])
@token_required
def chat(user_email):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT active FROM users WHERE email = :email"),
            {"email": user_email}
        )
        user = result.fetchone()
        if not user or not user[0]:  # user[0] == active
            return jsonify({"error": "User is temporarily banned. Please contact admin."}), 403

    user_query = request.json.get("message")
    if not user_query:
        return jsonify({"error": "Missing message"}), 400
    try:
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET request_count = request_count + 1 WHERE email = :email"),
                {"email": user_email}
            )

    except Exception as e:
        print(f"[WARN] Failed to update request_count for {user_email}: {str(e)}")

    # 1. Retrieve relevant documents from Chroma
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 6, "score_threshold": 0.3}
    )
    docs = retriever.get_relevant_documents(user_query)
    context_str = "\n\n".join([doc.page_content for doc in docs])

    if not docs:
        context_str = "No context available from retrieved documents."

    # 2. Load conversation so far
    convo_history = session_contexts.get(user_email, [])

    # 3. Create system prompt to add context
    system_message = {
        "role": "system",
        "content": f"You are a helpful migration assistant. Use the following context when answering:\n\n{context_str}"
    }

    # 4. Add current user query
    convo_history.append({"role": "user", "content": user_query})

    # 5. Construct final message list for OpenAI
    messages = [system_message] + convo_history

    try:
        completion = openai.ChatCompletion.create(
            engine=chat_deployment,
            messages=messages,
            temperature=0.2
        )
        response_text = completion.choices[0].message.content.strip()

        # 6. Add assistant response to memory
        convo_history.append({"role": "assistant", "content": response_text})
        session_contexts[user_email] = convo_history
        print(f"[DEBUG] Updated session_context for {user_email}: {session_contexts[user_email]}")

        return jsonify({
        "sender": "assistant",
        "text": response_text
        })

    except Exception as e:
        print("❌ Error from OpenAI:", e)
        return jsonify({"error": "LLM failed to respond."}), 500

