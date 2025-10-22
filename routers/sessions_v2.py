from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from models import ConversationResponse
from services.chat_service import ChatService
from datetime import datetime

router = APIRouter(prefix="/api/v2/sessions", tags=["sessions-v2"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_session(
    user_id: Optional[str] = Query(None),
    title: Optional[str] = Query("New Conversation")
):
    """
    Create a new chat session
    Returns session_id, created_at, and message
    """
    try:
        conversation = await ChatService.create_conversation(title)

        return {
            "session_id": conversation["id"],
            "created_at": conversation["created_at"].isoformat(),
            "message": "Session created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/{session_id}")
async def get_session(session_id: str):
    """
    Get session details with messages
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get messages for the session
        messages = await ChatService.get_messages(session_id)

        return {
            "session_id": conversation["id"],
            "created_at": conversation["created_at"].isoformat(),
            "updated_at": conversation.get("updated_at", conversation["created_at"]).isoformat(),
            "message_count": conversation["message_count"],
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"][0]["text"] if msg["content"] and msg["content"][0].get("text") else "",
                    "timestamp": msg["timestamp"].isoformat(),
                    "metadata": {}
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """
    Delete a session
    """
    try:
        success = await ChatService.delete_conversation(session_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/{session_id}/stats")
async def get_session_stats(session_id: str):
    """
    Get context statistics for a session
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        messages = await ChatService.get_messages(session_id)

        user_messages = sum(1 for msg in messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in messages if msg["role"] == "assistant")

        # Simple token estimation (rough)
        total_tokens = sum(
            len(msg["content"][0].get("text", "").split()) * 1.3
            for msg in messages if msg["content"]
        )

        return {
            "total_messages": len(messages),
            "total_tokens": int(total_tokens),
            "max_messages": 100,
            "max_tokens": 128000,
            "needs_optimization": total_tokens > 100000,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": 0,
            "messages_in_db": len(messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/{session_id}/context")
async def get_optimized_context(
    session_id: str,
    strategy: str = Query("smart", regex="^(smart|sliding_window|token_aware)$"),
    max_messages: Optional[int] = Query(None)
):
    """
    Get optimized context for a session
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        messages = await ChatService.get_messages(session_id, limit=max_messages or 100)

        return {
            "session_id": session_id,
            "strategy": strategy,
            "message_count": len(messages),
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"][0]["text"] if msg["content"] and msg["content"][0].get("text") else "",
                    "timestamp": msg["timestamp"].isoformat(),
                    "metadata": {}
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context: {str(e)}"
        )
