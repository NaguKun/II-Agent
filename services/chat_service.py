from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from database import MongoDB
from models import Message, Conversation, MessageRole, MessageType, MessageContent
from services.context_window import ContextWindowService
import logging

logger = logging.getLogger(__name__)


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
    async def get_messages(
        conversation_id: str,
        limit: int = 100,
        apply_sliding_window: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation

        Args:
            conversation_id: The conversation ID
            limit: Maximum messages to retrieve from DB
            apply_sliding_window: If True, apply sliding window optimization

        Returns:
            List of messages (potentially filtered by sliding window)
        """
        collection = MongoDB.get_collection("messages")

        cursor = collection.find({"conversation_id": conversation_id}).sort("timestamp", 1).limit(limit)
        messages = []

        async for msg in cursor:
            msg["id"] = str(msg["_id"])
            messages.append(msg)

        # Apply sliding window if requested
        if apply_sliding_window:
            result = ContextWindowService.apply_sliding_window(messages)
            logger.info(
                f"Sliding window: {result['kept_messages']}/{result['total_messages']} messages, "
                f"~{result['estimated_tokens']} tokens"
            )
            return result["messages"]

        return messages

    @staticmethod
    async def get_optimized_context(
        conversation_id: str,
        max_messages: Optional[int] = None,
        preserve_first: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get optimized conversation context with sliding window applied

        Returns messages + metadata about optimization
        """
        messages = await ChatService.get_messages(conversation_id, limit=200)

        result = ContextWindowService.apply_sliding_window(
            messages,
            max_messages=max_messages,
            preserve_first=preserve_first
        )

        return result

    @staticmethod
    async def get_context_summary(conversation_id: str) -> Dict[str, Any]:
        """Get summary of context window status for a conversation"""
        messages = await ChatService.get_messages(conversation_id)
        return ContextWindowService.get_context_summary(messages)

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

    @staticmethod
    async def update_conversation_metadata(conversation_id: str, metadata: Dict[str, Any]) -> bool:
        """Update conversation metadata (merge with existing)"""
        collection = MongoDB.get_collection("conversations")

        try:
            # Get existing metadata
            conversation = await collection.find_one({"_id": ObjectId(conversation_id)})
            if not conversation:
                return False

            existing_metadata = conversation.get("metadata", {})
            existing_metadata.update(metadata)

            result = await collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {"$set": {"metadata": existing_metadata, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating conversation metadata: {str(e)}")
            return False

    @staticmethod
    async def export_conversation(conversation_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export conversation in different formats
        Supports: json, markdown, text
        """
        conversation = await ChatService.get_conversation(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")

        messages = await ChatService.get_messages(conversation_id)

        if format == "json":
            return {
                "conversation": conversation,
                "messages": messages
            }
        elif format == "markdown":
            md_lines = [
                f"# {conversation.get('title', 'Conversation')}",
                f"\n**Created:** {conversation.get('created_at').strftime('%Y-%m-%d %H:%M:%S')}",
                f"\n**Messages:** {len(messages)}\n",
                "---\n"
            ]

            for msg in messages:
                role = msg.get('role', 'user').capitalize()
                content_list = msg.get('content', [])
                timestamp = msg.get('timestamp').strftime('%H:%M:%S')

                md_lines.append(f"### {role} ({timestamp})\n")

                for content_item in content_list:
                    if content_item.get('type') == 'text' and content_item.get('text'):
                        md_lines.append(f"{content_item['text']}\n")
                    elif content_item.get('type') == 'image':
                        md_lines.append(f"*[Image attached]*\n")
                    elif content_item.get('type') == 'csv':
                        md_lines.append(f"*[CSV data attached]*\n")

                md_lines.append("\n")

            return {"content": "\n".join(md_lines)}

        elif format == "text":
            text_lines = [
                f"Conversation: {conversation.get('title', 'Untitled')}",
                f"Created: {conversation.get('created_at').strftime('%Y-%m-%d %H:%M:%S')}",
                f"Messages: {len(messages)}",
                "=" * 50,
                ""
            ]

            for msg in messages:
                role = msg.get('role', 'user').upper()
                content_list = msg.get('content', [])
                timestamp = msg.get('timestamp').strftime('%H:%M:%S')

                text_lines.append(f"[{timestamp}] {role}:")

                for content_item in content_list:
                    if content_item.get('type') == 'text' and content_item.get('text'):
                        text_lines.append(f"  {content_item['text']}")
                    elif content_item.get('type') == 'image':
                        text_lines.append(f"  [Image attached]")
                    elif content_item.get('type') == 'csv':
                        text_lines.append(f"  [CSV data attached]")

                text_lines.append("")

            return {"content": "\n".join(text_lines)}

        else:
            raise ValueError(f"Unsupported format: {format}")
