"""
Context Window Management Service
Implements sliding window for maintaining conversation context within token limits
"""

from typing import List, Dict, Any, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class ContextWindowService:
    """Service for managing conversation context with sliding window"""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text
        Rough estimation: ~1.3 tokens per word for English text
        """
        if not text:
            return 0
        words = len(text.split())
        return int(words * 1.3)

    @staticmethod
    def estimate_message_tokens(message: Dict[str, Any]) -> int:
        """Estimate tokens for a single message"""
        total_tokens = 0
        content_list = message.get("content", [])

        for content_item in content_list:
            if content_item.get("type") == "text" and content_item.get("text"):
                total_tokens += ContextWindowService.estimate_tokens(content_item["text"])
            elif content_item.get("type") == "image":
                # Images use ~765 tokens (for vision models)
                total_tokens += 765
            elif content_item.get("type") == "csv":
                # CSV data can be large, estimate conservatively
                csv_text = str(content_item.get("csv_data", ""))
                total_tokens += ContextWindowService.estimate_tokens(csv_text)

        # Add overhead for role and structure (~4 tokens)
        total_tokens += 4

        return total_tokens

    @staticmethod
    def apply_sliding_window(
        messages: List[Dict[str, Any]],
        max_messages: Optional[int] = None,
        preserve_first: Optional[int] = None,
        token_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Apply sliding window to messages

        Strategy:
        1. Always preserve first N messages (context establishment)
        2. Keep most recent messages within limits
        3. Ensure token count stays under limit

        Args:
            messages: List of messages
            max_messages: Maximum number of messages to keep
            preserve_first: Number of initial messages to always keep
            token_limit: Maximum token count

        Returns:
            Dict with filtered messages and metadata
        """
        if not messages:
            return {
                "messages": [],
                "total_messages": 0,
                "kept_messages": 0,
                "removed_messages": 0,
                "estimated_tokens": 0,
                "window_applied": False
            }

        # Use settings defaults if not provided
        max_messages = max_messages or settings.sliding_window_max_messages
        preserve_first = preserve_first or settings.sliding_window_preserve_first
        token_limit = token_limit or settings.sliding_window_token_limit

        total_messages = len(messages)

        # If sliding window is disabled or messages within limit, return all
        if not settings.sliding_window_enabled or total_messages <= max_messages:
            total_tokens = sum(
                ContextWindowService.estimate_message_tokens(msg)
                for msg in messages
            )

            # Check token limit even if message count is ok
            if total_tokens <= token_limit:
                return {
                    "messages": messages,
                    "total_messages": total_messages,
                    "kept_messages": total_messages,
                    "removed_messages": 0,
                    "estimated_tokens": total_tokens,
                    "window_applied": False
                }

        logger.info(f"Applying sliding window: {total_messages} messages -> max {max_messages}")

        # Separate preserved and sliding messages
        preserved_messages = messages[:preserve_first] if preserve_first > 0 else []
        remaining_messages = messages[preserve_first:]

        # Calculate how many recent messages we can keep
        available_slots = max_messages - len(preserved_messages)

        if available_slots <= 0:
            # Can only keep preserved messages
            kept_messages = preserved_messages
        else:
            # Keep most recent messages
            recent_messages = remaining_messages[-available_slots:]
            kept_messages = preserved_messages + recent_messages

        # Check token limit and further reduce if needed
        total_tokens = sum(
            ContextWindowService.estimate_message_tokens(msg)
            for msg in kept_messages
        )

        # If still over token limit, remove from middle (keep first and last)
        while total_tokens > token_limit and len(kept_messages) > preserve_first + 2:
            # Remove from middle (after preserved, before last few)
            remove_index = preserve_first + (len(kept_messages) - preserve_first) // 2
            removed_msg = kept_messages.pop(remove_index)
            total_tokens -= ContextWindowService.estimate_message_tokens(removed_msg)
            logger.info(f"Removed message to meet token limit: {total_tokens} tokens remaining")

        removed_count = total_messages - len(kept_messages)

        logger.info(
            f"Sliding window applied: kept {len(kept_messages)}/{total_messages} messages, "
            f"~{total_tokens} tokens"
        )

        return {
            "messages": kept_messages,
            "total_messages": total_messages,
            "kept_messages": len(kept_messages),
            "removed_messages": removed_count,
            "estimated_tokens": total_tokens,
            "window_applied": removed_count > 0,
            "preserved_count": min(preserve_first, len(kept_messages))
        }

    @staticmethod
    def get_context_summary(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of the current context window status"""
        if not messages:
            return {
                "total_messages": 0,
                "estimated_tokens": 0,
                "within_limits": True,
                "needs_optimization": False
            }

        total_tokens = sum(
            ContextWindowService.estimate_message_tokens(msg)
            for msg in messages
        )

        max_messages = settings.sliding_window_max_messages
        token_limit = settings.sliding_window_token_limit

        needs_optimization = (
            len(messages) > max_messages or
            total_tokens > token_limit
        )

        return {
            "total_messages": len(messages),
            "estimated_tokens": total_tokens,
            "max_messages": max_messages,
            "token_limit": token_limit,
            "within_limits": not needs_optimization,
            "needs_optimization": needs_optimization,
            "token_usage_percent": (total_tokens / token_limit * 100) if token_limit > 0 else 0,
            "message_usage_percent": (len(messages) / max_messages * 100) if max_messages > 0 else 0
        }

    @staticmethod
    def create_context_warning_message(summary: Dict[str, Any]) -> Optional[str]:
        """Create a warning message if context is approaching limits"""
        if not summary.get("needs_optimization"):
            return None

        warnings = []

        if summary["total_messages"] > summary["max_messages"]:
            warnings.append(
                f"Message count ({summary['total_messages']}) exceeds limit ({summary['max_messages']})"
            )

        if summary["estimated_tokens"] > summary["token_limit"]:
            warnings.append(
                f"Token count (~{summary['estimated_tokens']}) exceeds limit ({summary['token_limit']})"
            )

        if warnings:
            return "Context window optimization needed: " + "; ".join(warnings)

        return None
