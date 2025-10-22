from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from database import MongoDB
from models import Message, Conversation, MessageRole, MessageType, MessageContent


class ChatService:
    """Service for managing chat conversations and messages"""

    @staticmethod
    async def create_conversation(title: str = "New Conversation") -> Dict[str, Any]:
        """Create a new conversation"""
        collection = MongoDB.get_collection("conversations")

        conversation = {
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
            "metadata": {}
        }

        result = await collection.insert_one(conversation)
        conversation["id"] = str(result.inserted_id)
        conversation["_id"] = result.inserted_id

        return conversation

    @staticmethod
    async def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID"""
        collection = MongoDB.get_collection("conversations")

        try:
            conversation = await collection.find_one({"_id": ObjectId(conversation_id)})
            if conversation:
                conversation["id"] = str(conversation["_id"])
            return conversation
        except Exception:
            return None

    @staticmethod
    async def list_conversations(limit: int = 50) -> List[Dict[str, Any]]:
        """List all conversations"""
        collection = MongoDB.get_collection("conversations")

        cursor = collection.find().sort("updated_at", -1).limit(limit)
        conversations = []

        async for conv in cursor:
            conv["id"] = str(conv["_id"])
            conversations.append(conv)

        return conversations

    @staticmethod
    async def delete_conversation(conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        conv_collection = MongoDB.get_collection("conversations")
        msg_collection = MongoDB.get_collection("messages")

        try:
            # Delete all messages
            await msg_collection.delete_many({"conversation_id": conversation_id})

            # Delete conversation
            result = await conv_collection.delete_one({"_id": ObjectId(conversation_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @staticmethod
    async def add_message(
        conversation_id: str,
        role: MessageRole,
        content: List[MessageContent],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a message to a conversation"""
        msg_collection = MongoDB.get_collection("messages")
        conv_collection = MongoDB.get_collection("conversations")

        message = {
            "conversation_id": conversation_id,
            "role": role.value,
            "content": [c.dict() for c in content],
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }

        result = await msg_collection.insert_one(message)
        message["id"] = str(result.inserted_id)
        message["_id"] = result.inserted_id

        # Update conversation
        try:
            await conv_collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$set": {"updated_at": datetime.utcnow()},
                    "$inc": {"message_count": 1}
                }
            )
        except Exception:
            pass

        return message

    @staticmethod
    async def get_messages(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all messages for a conversation"""
        collection = MongoDB.get_collection("messages")

        cursor = collection.find({"conversation_id": conversation_id}).sort("timestamp", 1).limit(limit)
        messages = []

        async for msg in cursor:
            msg["id"] = str(msg["_id"])
            messages.append(msg)

        return messages

    @staticmethod
    async def update_conversation_title(conversation_id: str, title: str) -> bool:
        """Update conversation title"""
        collection = MongoDB.get_collection("conversations")

        try:
            result = await collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception:
            return False
