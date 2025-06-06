from flask import Blueprint, request, jsonify
import os
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
#from langchain_community.embeddings import AzureOpenAIEmbeddings
# from utility.embedder import generate_embeddings 
from langchain_openai import AzureOpenAIEmbeddings
from utility.auth_utils import token_required
from sqlalchemy import text 
from utility.db_config import engine
from utility.json_loader import load_json_knowledge, format_json_knowledge_as_text
from openai import AzureOpenAI


chat_blueprint = Blueprint("chat", __name__)

# Store user conversation per session
session_contexts = {}

# Load environment variables
load_dotenv()

# Azure OpenAI setup
# openai.api_type = "azure"
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_version = os.getenv("OPENAI_API_VERSION")
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
# chat_deployment = os.getenv("AZURE_DEPLOYMENT_NAME")

# Initialize Flask app
app = Flask(__name__)

# Load Chroma DB
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "chroma_store"))

# embedding_model = AzureOpenAIEmbeddings(
#     azure_deployment=embedding_deployment,
#     openai_api_version=openai.api_version
# )

embedding_model = AzureOpenAIEmbeddings(
    model= os.getenv("AZURE_EMBEDDING_MODEL"),
    azure_endpoint= os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
    api_key= os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
    openai_api_version= os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
    deployment= os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
)

llm = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key= os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version= os.getenv("AZURE_OPENAI_API_VERSION"),
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

    query_parts = user_query.split(" and ")  # basic multi-part detection

    if len(query_parts) > 1:
        k = 15
        threshold = 0.2
    else:
        k = 8
        threshold = 0.3

    # 1. Retrieve relevant documents from Chroma
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        # search_kwargs={"k": 6, "score_threshold": 0.3}
        search_kwargs = {"k": k, "score_threshold": threshold} #testing

    )
    docs = retriever.get_relevant_documents(user_query)


    DEBUG_MODE = True  # Toggle to False in production

    if DEBUG_MODE:
        print("\n🔍 Retrieved Chunks:")
        if not docs:
            print(" No relevant chunks found for this query.")
        for i, doc in enumerate(docs):
            print(f"\n--- Chunk {i+1} ---")
            print(" Source:", doc.metadata.get("source") or doc.metadata.get("source_url") or "Unknown")
            print(" Title:", doc.metadata.get("title", "N/A"))
            print(" Preview:", doc.page_content[:300].strip(), "...\n")


    vector_context = "\n\n".join([doc.page_content for doc in docs])
    context_str = "\n\n".join([doc.page_content for doc in docs])

    if not docs:
        context_str = "No context available from retrieved documents."

    
    # 2. Load JSON knowledge base and format it
    json_knowledge = load_json_knowledge()
    json_context = format_json_knowledge_as_text(json_knowledge)

    # 3. Merge both into one context string
    context_str = f"""[Vector Knowledge Base]\n{vector_context}\n\n[Structured JSON Knowledge Base]\n{json_context}"""

    # 2. Load conversation so far
    convo_history = session_contexts.get(user_email, [])

#testing
    system_message = {
  "role": "system",
  "content": f"""
        You are an AI assistant specialized in migration topics. ONLY use the information provided between <context> tags — DO NOT use external knowledge, or your training data or assumptions.

        <context>
        The context includes:
        1. [Vector Knowledge Base] – Migration services, procedures, and policies.
        2. [Structured JSON Knowledge Base] – Official IOM contact info (offices, emails, phone numbers).
        {context_str}
        </context>

        Follow these rules:
        - Respond only to English queries. If not, reply: "Please ask your question in English so I can assist you properly."
        - For each part of a multi-question query, answer independently.
        - Use Vector KB for migration questions.
        - Use JSON KB for contact/location/email queries.
        - If no CONTEXT or RELEVANT info is found, respond: "I don’t have enough information in the provided context to answer that."
        - DO NOT guess, infer, or use unrelated context.
        - Ignore unrelated, unethical, or non-migration questions.

        Format your answers clearly per sub-question.
        """
        }

    # 4. Add current user query
    convo_history.append({"role": "user", "content": user_query})

    # 5. Construct final message list for OpenAI
    messages = [system_message] + convo_history

    try:
        # completion = llm.ChatCompletion.create(
        #     engine=os.getenv("AZURE_DEPLOYMENT_NAME"),
        #     messages=messages,
        #     temperature=0.2
        # )
        completion = llm.chat.completions.create(
            model=os.getenv("AZURE_DEPLOYMENT_NAME"),
            messages=messages,
            temperature=0.2
        )
        response_text = completion.choices[0].message.content.strip()

        # 6. Add assistant response to memory
        convo_history.append({"role": "assistant", "content": response_text})
        session_contexts[user_email] = convo_history
        print(f"Updated session_context for {user_email}: {session_contexts[user_email]}")

        return jsonify({
        "sender": "assistant",
        "text": response_text
        })
    
    except openai.error.InvalidRequestError as e:
        if "content management policy" in str(e):
            return jsonify({
                "sender": "assistant",
                "text": "I'm here to assist with migration-related topics. If you have questions in that area, I'd be happy to help!"
            }), 200
        else:
            print("OpenAI InvalidRequestError:", e)
            return jsonify({"error": "LLM request was invalid."}), 500

    except Exception as e:
        print("Error from OpenAI:", e)
        return jsonify({"error": "LLM failed to respond."}), 500


@chat_blueprint.route("/api/preferences", methods=["POST"])
# @app.route("/api/preferences", methods=["POST"])
@token_required
def update_preferences(email):

    try:
        data = request.get_json()
        source = data.get("source_country")
        destination = data.get("destination_country")

        if not source or not destination:
            return jsonify({"error": "Both source and destination country are required"}), 400

        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET source_country = :src, destination_country = :dst WHERE email = :email"),
                {"src": source, "dst": destination, "email": email}
            )

        return jsonify({"message": "Preferences updated successfully"}), 200

    except Exception as e:
        print(f"[ERROR] Failed to update preferences: {str(e)}")
        return jsonify({"error": "Could not update preferences"}), 500


