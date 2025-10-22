from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import base64
from io import BytesIO
from models import MessageRole, MessageType, MessageContent
from services.chat_service import ChatService
from services.image_service import ImageService
from services.csv_service import CSVService
from services.ai_service import AIService

router = APIRouter(prefix="/api/v2", tags=["chat-v2"])


@router.post("/chat")
async def send_text_message(request: dict):
    """
    Send a text message (non-streaming)
    """
    try:
        session_id = request.get("session_id")
        message = request.get("message")

        if not session_id or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id and message are required"
            )

        # Verify conversation exists
        conversation = await ChatService.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Save user message
        user_content = [MessageContent(type=MessageType.TEXT, text=message)]
        user_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Get conversation history
        messages = await ChatService.get_messages(session_id)
        formatted_messages = AIService.format_conversation_history(messages)

        # Generate AI response
        ai_response_text = await AIService.generate_response(
            formatted_messages,
            AIService.create_system_prompt()
        )

        # Save assistant message
        assistant_content = [MessageContent(type=MessageType.TEXT, text=ai_response_text)]
        assistant_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content
        )

        return {
            "message_id": assistant_message["id"],
            "response": ai_response_text,
            "timestamp": assistant_message["timestamp"].isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/chat/stream")
async def send_text_message_stream(request: dict):
    """
    Send a text message with streaming response
    """
    try:
        session_id = request.get("session_id")
        message = request.get("message")

        if not session_id or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="session_id and message are required"
            )

        # Verify conversation exists
        conversation = await ChatService.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Save user message
        user_content = [MessageContent(type=MessageType.TEXT, text=message)]
        user_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Get conversation history
        messages = await ChatService.get_messages(session_id)
        formatted_messages = AIService.format_conversation_history(messages)

        async def generate_stream():
            """Generator function for streaming response"""
            try:
                full_response = ""

                # Stream the AI response
                async for chunk in AIService.generate_response_stream(
                    formatted_messages,
                    AIService.create_system_prompt()
                ):
                    full_response += chunk
                    # Send chunk in SSE format
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"

                # Save assistant message after streaming
                assistant_content = [MessageContent(type=MessageType.TEXT, text=full_response)]
                assistant_message = await ChatService.add_message(
                    conversation_id=session_id,
                    role=MessageRole.ASSISTANT,
                    content=assistant_content
                )

                # Send completion message
                yield f"data: {json.dumps({'done': True, 'message_id': assistant_message['id']})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send streaming message: {str(e)}"
        )


@router.post("/chat/image")
async def send_image_message(
    session_id: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(...)
):
    """
    Send a message with an image
    """
    try:
        # Verify conversation exists
        conversation = await ChatService.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Read and encode image
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Determine image type
        image_type = image.content_type or "image/jpeg"
        image_data = f"data:{image_type};base64,{image_base64}"

        # Validate image
        is_valid, error = ImageService.validate_image(image_data)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        # Save user message
        user_content = [
            MessageContent(type=MessageType.TEXT, text=message),
            MessageContent(type=MessageType.IMAGE, image_url=image_data)
        ]
        user_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Get conversation history
        messages = await ChatService.get_messages(session_id)
        formatted_messages = AIService.format_conversation_history(messages)

        # Generate AI response
        ai_response_text = await AIService.generate_response(
            formatted_messages,
            AIService.create_system_prompt()
        )

        # Save assistant message
        assistant_content = [MessageContent(type=MessageType.TEXT, text=ai_response_text)]
        assistant_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content
        )

        return {
            "message_id": assistant_message["id"],
            "response": ai_response_text,
            "image_id": user_message["id"],
            "image_preview": image_data[:100] + "..."  # Preview only
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send image message: {str(e)}"
        )


@router.post("/chat/csv/upload")
async def send_csv_message(
    session_id: str = Form(...),
    message: str = Form(...),
    csv_file: UploadFile = File(...)
):
    """
    Send a message with a CSV file
    """
    try:
        # Verify conversation exists
        conversation = await ChatService.get_conversation(session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Validate file type
        if not csv_file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are allowed"
            )

        # Read and parse CSV
        csv_bytes = await csv_file.read()
        df = CSVService.load_csv_from_bytes(csv_bytes)

        # Analyze CSV
        csv_analysis = CSVService.analyze_query(df, message)

        # Save user message
        user_content = [
            MessageContent(type=MessageType.TEXT, text=f"Uploaded CSV: {csv_file.filename}. {message}"),
            MessageContent(type=MessageType.CSV, csv_data=csv_analysis)
        ]
        user_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Get conversation history
        messages = await ChatService.get_messages(session_id)
        formatted_messages = AIService.format_conversation_history(messages)

        # Generate AI response
        ai_response_text = await AIService.generate_response(
            formatted_messages,
            AIService.create_system_prompt()
        )

        # Save assistant message
        assistant_content = [MessageContent(type=MessageType.TEXT, text=ai_response_text)]
        assistant_message = await ChatService.add_message(
            conversation_id=session_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content
        )

        return {
            "message_id": assistant_message["id"],
            "response": ai_response_text,
            "csv_id": user_message["id"],
            "summary": csv_analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send CSV message: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for v2 API
    """
    try:
        from database import MongoDB

        # Check database connection
        db = MongoDB.database
        if db is None:
            return {"status": "unhealthy", "database": "not connected"}

        # Try to ping the database
        await db.command("ping")

        return {
            "status": "healthy",
            "version": "v2",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "v2",
            "error": str(e)
        }
