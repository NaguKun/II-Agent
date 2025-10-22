from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import Optional
from models import (
    SendMessageRequest,
    MessageResponse,
    MessageRole,
    MessageType,
    MessageContent
)
from services.chat_service import ChatService
from services.image_service import ImageService
from services.csv_service import CSVService
from services.ai_service import AIService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=dict)
async def send_message(
    conversation_id: str = Form(...),
    content: str = Form(...),
    image_data: Optional[str] = Form(None),
    csv_url: Optional[str] = Form(None)
):
    """
    Send a message in a conversation
    Supports text, image, and CSV data
    """
    try:
        # Verify conversation exists
        conversation = await ChatService.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Build user message content
        user_content = []

        # Add text content
        if content:
            user_content.append(MessageContent(
                type=MessageType.TEXT,
                text=content
            ))

        # Handle image if provided
        if image_data:
            is_valid, error = ImageService.validate_image(image_data)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error
                )

            user_content.append(MessageContent(
                type=MessageType.IMAGE,
                image_url=image_data
            ))

        # Handle CSV if provided
        csv_analysis = None
        visualization_image = None
        if csv_url:
            try:
                csv_service = CSVService()
                df = await csv_service.load_csv_from_url(csv_url)
                csv_analysis = await csv_service.analyze_query(df, content, conversation_id=conversation_id)
                await csv_service.close_session()

                # Check if visualization was generated
                if csv_analysis.get("type") == "visualization" and csv_analysis.get("result", {}).get("image_data"):
                    visualization_image = csv_analysis["result"]["image_data"]

                user_content.append(MessageContent(
                    type=MessageType.CSV,
                    csv_url=csv_url,
                    csv_data=csv_analysis
                ))
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"CSV error: {str(e)}"
                )

        # Save user message
        user_message = await ChatService.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Get conversation history for AI
        messages = await ChatService.get_messages(conversation_id)
        formatted_messages = AIService.format_conversation_history(messages)

        # Generate AI response
        ai_response_text = await AIService.generate_response(
            formatted_messages,
            AIService.create_system_prompt()
        )

        # Save assistant message
        assistant_content = [MessageContent(
            type=MessageType.TEXT,
            text=ai_response_text
        )]

        # Add visualization image to assistant message if generated
        if visualization_image:
            assistant_content.append(MessageContent(
                type=MessageType.IMAGE,
                image_url=visualization_image
            ))

        assistant_message = await ChatService.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content
        )

        return {
            "user_message": MessageResponse(
                id=user_message["id"],
                conversation_id=user_message["conversation_id"],
                role=user_message["role"],
                content=user_message["content"],
                timestamp=user_message["timestamp"]
            ),
            "assistant_message": MessageResponse(
                id=assistant_message["id"],
                conversation_id=assistant_message["conversation_id"],
                role=assistant_message["role"],
                content=assistant_message["content"],
                timestamp=assistant_message["timestamp"]
            ),
            "csv_analysis": csv_analysis,
            "visualization": visualization_image
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    conversation_id: str = Form(...),
    query: str = Form("summarize")
):
    """Upload a CSV file and analyze it"""
    try:
        # Verify conversation exists
        conversation = await ChatService.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are allowed"
            )

        # Read file
        contents = await file.read()

        # Parse CSV and analyze
        df = CSVService.load_csv_from_bytes(contents)
        csv_service = CSVService()
        analysis = await csv_service.analyze_query(df, query, conversation_id=conversation_id)
        await csv_service.close_session()

        # Check if visualization was generated
        visualization_image = None
        if analysis.get("type") == "visualization" and analysis.get("result", {}).get("image_data"):
            visualization_image = analysis["result"]["image_data"]

        # Save user message with CSV data
        user_content = [
            MessageContent(
                type=MessageType.TEXT,
                text=f"Uploaded CSV file: {file.filename}. Query: {query}"
            ),
            MessageContent(
                type=MessageType.CSV,
                csv_data=analysis
            )
        ]

        user_message = await ChatService.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_content
        )

        # Generate AI response
        messages = await ChatService.get_messages(conversation_id)
        formatted_messages = AIService.format_conversation_history(messages)
        ai_response_text = await AIService.generate_response(
            formatted_messages,
            AIService.create_system_prompt()
        )

        # Save assistant message
        assistant_content = [MessageContent(
            type=MessageType.TEXT,
            text=ai_response_text
        )]

        # Add visualization image to assistant message if generated
        if visualization_image:
            assistant_content.append(MessageContent(
                type=MessageType.IMAGE,
                image_url=visualization_image
            ))

        assistant_message = await ChatService.add_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_content
        )

        return {
            "analysis": analysis,
            "user_message": MessageResponse(
                id=user_message["id"],
                conversation_id=user_message["conversation_id"],
                role=user_message["role"],
                content=user_message["content"],
                timestamp=user_message["timestamp"]
            ),
            "assistant_message": MessageResponse(
                id=assistant_message["id"],
                conversation_id=assistant_message["conversation_id"],
                role=assistant_message["role"],
                content=assistant_message["content"],
                timestamp=assistant_message["timestamp"]
            ),
            "visualization": visualization_image
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV: {str(e)}"
        )


@router.post("/analyze-csv")
async def analyze_csv(
    conversation_id: str = Form(...),
    csv_url: str = Form(...),
    query: str = Form("summarize")
):
    """Analyze a CSV from URL"""
    try:
        # Verify conversation exists
        conversation = await ChatService.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Load CSV from URL and analyze
        csv_service = CSVService()
        df = await csv_service.load_csv_from_url(csv_url)
        analysis = await csv_service.analyze_query(df, query, conversation_id=conversation_id)
        await csv_service.close_session()

        return {
            "success": True,
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze CSV: {str(e)}"
        )
