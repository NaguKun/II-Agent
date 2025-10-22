from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Message type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    CSV = "csv"


class MessageContent(BaseModel):
    """Message content model"""
    type: MessageType
    text: Optional[str] = None
    image_url: Optional[str] = None
    csv_data: Optional[Dict[str, Any]] = None
    csv_url: Optional[str] = None


class Message(BaseModel):
    """Chat message model"""
    id: Optional[str] = None
    conversation_id: str
    role: MessageRole
    content: List[MessageContent]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Conversation(BaseModel):
    """Conversation model"""
    id: Optional[str] = None
    title: Optional[str] = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CreateConversationRequest(BaseModel):
    """Request model for creating a conversation"""
    title: Optional[str] = "New Conversation"


class SendMessageRequest(BaseModel):
    """Request model for sending a message"""
    conversation_id: str
    content: str
    image_data: Optional[str] = None  # Base64 encoded image
    csv_url: Optional[str] = None


class CSVAnalysisRequest(BaseModel):
    """Request model for CSV analysis"""
    conversation_id: str
    query: str
    csv_url: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response model for conversation"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class MessageResponse(BaseModel):
    """Response model for message"""
    id: str
    conversation_id: str
    role: MessageRole
    content: List[MessageContent]
    timestamp: datetime
