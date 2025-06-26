# chat_crew_ai.py - Enhanced Chat with CrewAI Integration

from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv
from utility.auth_utils import token_required
from sqlalchemy import text 
from utility.db_config import engine
from crew_ai.crew import MigrationAssistanceCrew
import openai
import time


load_dotenv()

crew_chat_blueprint = Blueprint("crew_chat", __name__)

# Initialize CrewAI system
migration_crew = MigrationAssistanceCrew()

# Store user conversation per session (enhanced with CrewAI context)
crew_session_contexts = {}

@crew_chat_blueprint.route("/api/chat/crew", methods=["POST"])
@token_required
def crew_chat(user_email):
    """Enhanced chat endpoint using CrewAI agents"""
    
    # Check user status
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT active FROM users WHERE email = :email"),
            {"email": user_email}
        )
        user = result.fetchone()
        if not user or not user[0]:
            return jsonify({"error": "User is temporarily banned. Please contact admin."}), 403

    user_query = request.json.get("message")
    if not user_query:
        return jsonify({"error": "Missing message"}), 400
        
    # Update request count
    try:
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET request_count = request_count + 1 WHERE email = :email"),
                {"email": user_email}
            )
    except Exception as e:
        print(f"[WARN] Failed to update request_count for {user_email}: {str(e)}")

    try:
        # Get user context from database
        user_context = migration_crew.get_user_context_from_db(user_email, engine)
        
        # Add conversation history to context
        conversation_history = crew_session_contexts.get(user_email, [])
        if conversation_history:
            user_context["conversation_history"] = conversation_history[-5:]  # Last 5 messages
        
        # Process query through CrewAI
        print(f"[CREW AI] Processing query for {user_email}: {user_query[:100]}...")
        start_time = time.time()
        
        crew_response = migration_crew.process_migration_query(user_query, user_context)
        
        processing_time = time.time() - start_time
        print(f"[CREW AI] Processing completed in {processing_time:.2f} seconds")
        
        # Update conversation history
        if user_email not in crew_session_contexts:
            crew_session_contexts[user_email] = []
        
        crew_session_contexts[user_email].append({"role": "user", "content": user_query})
        crew_session_contexts[user_email].append({"role": "assistant", "content": crew_response})
        
        # Keep only last 20 messages to prevent memory issues
        if len(crew_session_contexts[user_email]) > 20:
            crew_session_contexts[user_email] = crew_session_contexts[user_email][-20:]
        
        return jsonify({
            "sender": "assistant",
            "text": crew_response,
            "processing_time": f"{processing_time:.2f}s",
            "crew_ai_enabled": True
        })
        
    except Exception as e:
        print(f"[CREW AI ERROR] {str(e)}")
        
        # Fallback to basic response
        fallback_response = """I apologize, but our advanced migration assistance system is currently experiencing issues. 
        However, I can still provide basic migration information. Please try rephrasing your question or contact your 
        nearest IOM office for direct assistance.
        
        For immediate help, you can reach IOM through their global contact directory or visit their official website."""
        
        return jsonify({
            "sender": "assistant", 
            "text": fallback_response,
            "crew_ai_enabled": False,
            "error": "crew_ai_fallback"
        })

@crew_chat_blueprint.route("/api/chat/crew/status", methods=["GET"])
@token_required 
def crew_status(user_email):
    """Check CrewAI system status"""
    try:
        # Simple test to check if CrewAI is working
        test_response = migration_crew.process_migration_query(
            "test query", 
            {"source_country": "test", "destination_country": "test"}
        )
        
        return jsonify({
            "status": "operational",
            "crew_ai_available": True,
            "message": "CrewAI migration assistance is available"
        })
        
    except Exception as e:
        return jsonify({
            "status": "degraded", 
            "crew_ai_available": False,
            "error": str(e),
            "message": "CrewAI system is experiencing issues"
        })

@crew_chat_blueprint.route("/api/chat/crew/reset", methods=["POST"])
@token_required
def reset_crew_conversation(user_email):
    """Reset user's CrewAI conversation history"""
    try:
        if user_email in crew_session_contexts:
            del crew_session_contexts[user_email]
            
        return jsonify({
            "message": "Conversation history reset successfully",
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to reset conversation",
            "message": str(e)
        }), 500

# Hybrid endpoint that tries CrewAI first, falls back to original RAG
@crew_chat_blueprint.route("/api/chat/hybrid", methods=["POST"]) 
@token_required
def hybrid_chat(user_email):
    """Hybrid chat that tries CrewAI first, falls back to original RAG"""
    
    # Check user status
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT active FROM users WHERE email = :email"),
            {"email": user_email}
        )
        user = result.fetchone()
        if not user or not user[0]:
            return jsonify({"error": "User is temporarily banned. Please contact admin."}), 403

    user_query = request.json.get("message")
    if not user_query:
        return jsonify({"error": "Missing message"}), 400
    
    # Update request count
    try:
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE users SET request_count = request_count + 1 WHERE email = :email"),
                {"email": user_email}
            )
    except Exception as e:
        print(f"[WARN] Failed to update request_count for {user_email}: {str(e)}")
    
    # Try CrewAI first
    try:
        user_context = migration_crew.get_user_context_from_db(user_email, engine)
        conversation_history = crew_session_contexts.get(user_email, [])
        if conversation_history:
            user_context["conversation_history"] = conversation_history[-3:]
        
        print(f"[HYBRID] Trying CrewAI for {user_email}")
        crew_response = migration_crew.process_migration_query(user_query, user_context)
        
        # Update conversation history
        if user_email not in crew_session_contexts:
            crew_session_contexts[user_email] = []
        
        crew_session_contexts[user_email].append({"role": "user", "content": user_query})
        crew_session_contexts[user_email].append({"role": "assistant", "content": crew_response})
        
        if len(crew_session_contexts[user_email]) > 16:
            crew_session_contexts[user_email] = crew_session_contexts[user_email][-16:]
        
        return jsonify({
            "sender": "assistant",
            "text": crew_response,
            "method": "crew_ai"
        })
        
    except Exception as crew_error:
        print(f"[HYBRID] CrewAI failed, falling back to RAG: {str(crew_error)}")
        
        # Fallback to original RAG system
        try:
            from chat_rag import chat
            # Note: This would need to be refactored to be called as a function
            # For now, return a basic fallback
            fallback_response = """I'm here to help with your migration questions. While our advanced system is 
            temporarily unavailable, I can still provide information based on official migration resources. 
            
            Please let me know what specific migration information you need, and I'll do my best to assist you."""
            
            return jsonify({
                "sender": "assistant",
                "text": fallback_response, 
                "method": "fallback"
            })
            
        except Exception as fallback_error:
            print(f"[HYBRID] Both systems failed: {str(fallback_error)}")
            return jsonify({
                "error": "Migration assistance system temporarily unavailable"
            }), 500