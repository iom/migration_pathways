# Utility Notebook to Test Azure OpenAI Connections

# Cell 1: Imports and Environment Variables
import os
from langchain_openai import AzureOpenAIEmbeddings
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

# Retrieve and display key environment variables for verification
print("AZURE_EMBEDDING_MODEL:", os.getenv("AZURE_EMBEDDING_MODEL"))
print("AZURE_OPENAI_ENDPOINT_EMBED:", os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"))
print("AZURE_OPENAI_API_KEY_EMBED:", bool(os.getenv("AZURE_OPENAI_API_KEY_EMBED")))
print("AZURE_OPENAI_API_VERSION_EMBED:", os.getenv("AZURE_OPENAI_API_VERSION_EMBED"))
print("AZURE_EMBEDDING_DEPLOYMENT_NAME:", os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME"))
print("AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("AZURE_OPENAI_API_KEY:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
print("AZURE_OPENAI_API_VERSION:", os.getenv("AZURE_OPENAI_API_VERSION"))
print("AZURE_DEPLOYMENT_NAME:", os.getenv("AZURE_DEPLOYMENT_NAME"))

# Cell 2: Test Azure OpenAI Embeddings Connection
def test_embeddings():
    print("\n--- Testing Azure OpenAI Embeddings Connection ---")
    try:
        embed = AzureOpenAIEmbeddings(
            model=os.getenv("AZURE_EMBEDDING_MODEL"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT_EMBED"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY_EMBED"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION_EMBED"),
            deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME")
        )
        # Perform a simple embedding request
        sample_text = "This is a test."
        vector = embed.embed_documents([sample_text])
        print("Embeddings test successful! Vector length:", len(vector[0]))
    except Exception as e:
        print("Embeddings test failed:", str(e))

test_embeddings()

# Cell 3: Test Azure OpenAI Chat Completion Connection
def test_llm():
    print("\n--- Testing Azure OpenAI Chat Completion Connection ---")
    try:
        llm = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        # Construct a minimal chat request
        system_msg = {"role": "system", "content": "You are a test assistant."}
        user_msg = {"role": "user", "content": "Hello, how are you?"}
        response = llm.chat.completions.create(
            model=os.getenv("AZURE_DEPLOYMENT_NAME"),
            messages=[system_msg, user_msg],
            temperature=0.0
        )
        print("LLM test successful! Response:", response.choices[0].message.content)
    except Exception as e:
        print("LLM test failed:", str(e))

test_llm()
