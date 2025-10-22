from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import PlainTextResponse, JSONResponse
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
    Get context statistics for a session with sliding window info
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get context summary with sliding window info
        context_summary = await ChatService.get_context_summary(session_id)

        messages = await ChatService.get_messages(session_id)
        user_messages = sum(1 for msg in messages if msg["role"] == "user")
        assistant_messages = sum(1 for msg in messages if msg["role"] == "assistant")

        return {
            "total_messages": context_summary["total_messages"],
            "total_tokens": context_summary["estimated_tokens"],
            "max_messages": context_summary.get("max_messages", 20),
            "max_tokens": context_summary.get("token_limit", 100000),
            "needs_optimization": context_summary["needs_optimization"],
            "within_limits": context_summary["within_limits"],
            "token_usage_percent": round(context_summary.get("token_usage_percent", 0), 2),
            "message_usage_percent": round(context_summary.get("message_usage_percent", 0), 2),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "system_messages": 0,
            "messages_in_db": len(messages),
            "sliding_window_enabled": True
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
    max_messages: Optional[int] = Query(None),
    preserve_first: Optional[int] = Query(None)
):
    """
    Get optimized context for a session with sliding window applied
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Get optimized context with sliding window
        result = await ChatService.get_optimized_context(
            session_id,
            max_messages=max_messages,
            preserve_first=preserve_first
        )

        return {
            "session_id": session_id,
            "strategy": "sliding_window",
            "total_messages": result["total_messages"],
            "kept_messages": result["kept_messages"],
            "removed_messages": result["removed_messages"],
            "estimated_tokens": result["estimated_tokens"],
            "window_applied": result["window_applied"],
            "preserved_count": result.get("preserved_count", 0),
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"][0]["text"] if msg["content"] and msg["content"][0].get("text") else "",
                    "timestamp": msg["timestamp"].isoformat(),
                    "metadata": {}
                }
                for msg in result["messages"]
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context: {str(e)}"
        )


@router.get("/{session_id}/export")
async def export_conversation(
    session_id: str,
    format: str = Query("json", regex="^(json|markdown|text)$")
):
    """
    Export conversation in different formats
    Supported formats: json, markdown, text
    """
    try:
        conversation = await ChatService.get_conversation(session_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        export_data = await ChatService.export_conversation(session_id, format)

        # Return appropriate response based on format
        if format == "json":
            return JSONResponse(content=export_data)
        elif format == "markdown":
            return PlainTextResponse(
                content=export_data["content"],
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename=conversation_{session_id}.md"
                }
            )
        elif format == "text":
            return PlainTextResponse(
                content=export_data["content"],
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename=conversation_{session_id}.txt"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export conversation: {str(e)}"
        )
