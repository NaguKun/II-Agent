from typing import List, Dict, Any, Optional
from config import settings
import json
import base64
from openai import OpenAI


class AIService:
    """Service for OpenAI GPT interactions"""

    client = None

    @classmethod
    def get_client(cls):
        """Get or create OpenAI client"""
        if cls.client is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            cls.client = OpenAI(api_key=settings.openai_api_key)
        return cls.client

    @staticmethod
    def format_conversation_history(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format conversation history for OpenAI API"""
        formatted = []

        for msg in messages:
            role = msg.get("role", "user")
            content_list = msg.get("content", [])

            # Build content for this message
            message_content = []

            for content_item in content_list:
                content_type = content_item.get("type")

                if content_type == "text" and content_item.get("text"):
                    message_content.append({
                        "type": "text",
                        "text": content_item["text"]
                    })

                elif content_type == "image" and content_item.get("image_url"):
                    # OpenAI expects image_url format
                    image_data = content_item["image_url"]

                    # Ensure proper format
                    if not image_data.startswith("data:image"):
                        image_data = f"data:image/jpeg;base64,{image_data}"

                    message_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    })

                elif content_type == "csv" and content_item.get("csv_data"):
                    # Format CSV data as text context
                    csv_text = AIService._format_csv_for_context(content_item["csv_data"])
                    message_content.append({
                        "type": "text",
                        "text": csv_text
                    })

            if message_content:
                # If only one text content, simplify
                if len(message_content) == 1 and message_content[0]["type"] == "text":
                    formatted.append({
                        "role": "user" if role == "user" else "assistant",
                        "content": message_content[0]["text"]
                    })
                else:
                    formatted.append({
                        "role": "user" if role == "user" else "assistant",
                        "content": message_content
                    })

        return formatted

    @staticmethod
    def _format_csv_for_context(csv_data: Dict[str, Any]) -> str:
        """Format CSV analysis data for AI context"""
        parts = ["CSV Data Analysis:"]

        if csv_data.get("basic_info"):
            info = csv_data["basic_info"]
            parts.append(f"\nDataset: {info.get('rows')} rows × {info.get('columns')} columns")
            parts.append(f"Columns: {', '.join(info.get('column_names', []))}")

            # Add data types information
            if info.get('dtypes'):
                parts.append("\nColumn Types:")
                for col, dtype in info['dtypes'].items():
                    parts.append(f"  - {col}: {dtype}")

        if csv_data.get("stats"):
            stats_data = csv_data["stats"]
            if stats_data.get("statistics"):
                parts.append("\nStatistical Summary:")
                for col, stats in stats_data["statistics"].items():
                    parts.append(f"\n{col}:")
                    if isinstance(stats, dict):
                        for stat_name, value in stats.items():
                            if isinstance(value, (int, float)):
                                parts.append(f"  - {stat_name}: {value:.2f}")
                            else:
                                parts.append(f"  - {stat_name}: {value}")

        if csv_data.get("missing"):
            missing_data = csv_data["missing"]
            if missing_data.get("total_missing", 0) > 0:
                parts.append(f"\nMissing Values: {missing_data['total_missing']} total")
                if missing_data.get("details"):
                    for col, info in missing_data["details"].items():
                        parts.append(f"  - {col}: {info['count']} ({info['percentage']}%)")
            else:
                parts.append("\nNo missing values detected")

        if csv_data.get("data"):
            # Handle other data types (column_info, preview, etc.)
            parts.append(f"\nAdditional Data: {json.dumps(csv_data['data'], indent=2)}")

        if csv_data.get("preview"):
            parts.append(f"\nData preview: {json.dumps(csv_data['preview'], indent=2)}")

        return "\n".join(parts)

    @staticmethod
    async def generate_response(
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate AI response using OpenAI GPT-4o-mini"""
        try:
            client = AIService.get_client()

            # Prepare messages for OpenAI
            openai_messages = []

            # Add system prompt if provided
            if system_prompt:
                openai_messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add conversation history
            openai_messages.extend(messages)

            # Call OpenAI API
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=openai_messages,
                max_tokens=1024,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            # Fallback response if API fails
            return f"I apologize, but I encountered an error: {str(e)}. Please check your API key and try again."

    @staticmethod
    async def generate_response_stream(
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ):
        """Generate AI response with streaming using OpenAI GPT-4o-mini"""
        try:
            client = AIService.get_client()

            # Prepare messages for OpenAI
            openai_messages = []

            # Add system prompt if provided
            if system_prompt:
                openai_messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Add conversation history
            openai_messages.extend(messages)

            # Call OpenAI API with streaming
            stream = client.chat.completions.create(
                model=settings.openai_model,
                messages=openai_messages,
                max_tokens=1024,
                temperature=0.7,
                stream=True
            )

            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            # Yield error message
            yield f"I apologize, but I encountered an error: {str(e)}. Please check your API key and try again."

    @staticmethod
    def create_system_prompt() -> str:
        """Create system prompt for the AI"""
        return """You are a helpful AI assistant integrated into a chat application.

You can:
1. Have multi-turn conversations with users
2. Analyze and discuss images that users upload
3. Analyze CSV data and answer questions about datasets
4. Help with data analysis tasks like summarizing data, computing statistics, and identifying patterns

When discussing images, be specific about what you observe.
When analyzing CSV data, provide clear, actionable insights.
Be concise but informative in your responses."""
