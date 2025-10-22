from typing import List, Dict, Any, Optional
from config import settings
import json
import base64
import hashlib
import logging
from functools import lru_cache
from openai import OpenAI

logger = logging.getLogger(__name__)

# Simple in-memory cache for responses (use Redis in production)
_response_cache: Dict[str, str] = {}
MAX_CACHE_SIZE = 1000


class AIService:
    """Service for OpenAI GPT interactions with caching"""

    _client: Optional[OpenAI] = None
    _client_lock = None

    @classmethod
    def get_client(cls) -> OpenAI:
        """Get or create OpenAI client (singleton pattern)"""
        if cls._client is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            cls._client = OpenAI(
                api_key=settings.openai_api_key,
                timeout=30.0,  # Request timeout
                max_retries=2,  # Retry failed requests
            )
            logger.info("OpenAI client initialized")
        return cls._client

    @staticmethod
    def _generate_cache_key(messages: List[Dict[str, Any]], system_prompt: Optional[str]) -> str:
        """Generate a cache key for the request"""
        # Create a hash of the messages and system prompt
        content = json.dumps(messages, sort_keys=True) + (system_prompt or "")
        return hashlib.md5(content.encode()).hexdigest()

    @staticmethod
    def _get_cached_response(cache_key: str) -> Optional[str]:
        """Get cached response if available"""
        return _response_cache.get(cache_key)

    @staticmethod
    def _cache_response(cache_key: str, response: str):
        """Cache a response (with size limit)"""
        if len(_response_cache) >= MAX_CACHE_SIZE:
            # Simple LRU: remove first item
            _response_cache.pop(next(iter(_response_cache)))
        _response_cache[cache_key] = response

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
                    # IMPORTANT: OpenAI API only allows images in user messages, not assistant messages
                    # Skip images in assistant messages to avoid API errors
                    if role == "user":
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
                    # If it's an assistant message with an image, skip the image but keep processing other content

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

        # Handle the response structure from CSVService.analyze_query
        result_data = csv_data.get("result", csv_data)
        response_type = csv_data.get("type", "unknown")

        parts.append(f"\nAnalysis Type: {response_type}")

        # Handle different response types
        if response_type == "summary":
            # Summary includes basic_info, stats, and missing
            if result_data.get("basic_info"):
                info = result_data["basic_info"]
                parts.append(f"\nDataset: {info.get('rows')} rows × {info.get('columns')} columns")
                parts.append(f"Columns: {', '.join(info.get('column_names', []))}")

                if info.get('dtypes'):
                    parts.append("\nColumn Types:")
                    for col, dtype in info['dtypes'].items():
                        parts.append(f"  - {col}: {dtype}")

            if result_data.get("stats"):
                stats_data = result_data["stats"]
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

            if result_data.get("missing"):
                missing_data = result_data["missing"]
                if missing_data.get("total_missing", 0) > 0:
                    parts.append(f"\nMissing Values: {missing_data['total_missing']} total")
                    if missing_data.get("details"):
                        for col, info in missing_data["details"].items():
                            parts.append(f"  - {col}: {info['count']} ({info['percentage']}%)")
                else:
                    parts.append("\nNo missing values detected")

        elif response_type == "statistics":
            # Statistics response
            if result_data.get("statistics"):
                parts.append("\nStatistical Summary:")
                for col, stats in result_data["statistics"].items():
                    parts.append(f"\n{col}:")
                    if isinstance(stats, dict):
                        for stat_name, value in stats.items():
                            if isinstance(value, (int, float)):
                                parts.append(f"  - {stat_name}: {value:.2f}")
                            else:
                                parts.append(f"  - {stat_name}: {value}")

        elif response_type == "preview":
            # Preview response
            if result_data.get("data"):
                parts.append(f"\nData Preview ({result_data.get('rows', 0)} rows):")
                parts.append(json.dumps(result_data["data"], indent=2))

        elif response_type == "histogram":
            # Histogram response
            parts.append(f"\nHistogram for column: {result_data.get('column')}")
            parts.append(f"Range: {result_data.get('min')} to {result_data.get('max')}")
            if result_data.get("data"):
                parts.append("\nDistribution:")
                for item in result_data["data"]:
                    parts.append(f"  {item.get('range')}: {item.get('count')} values")

        elif response_type == "column_info":
            # Column info response
            parts.append(f"\nColumn: {result_data.get('name')}")
            parts.append(f"Data Type: {result_data.get('dtype')}")
            parts.append(f"Non-null Count: {result_data.get('non_null_count')}")
            parts.append(f"Unique Values: {result_data.get('unique_values')}")

            if result_data.get('mean') is not None:
                parts.append(f"\nNumeric Statistics:")
                parts.append(f"  - Min: {result_data.get('min')}")
                parts.append(f"  - Max: {result_data.get('max')}")
                parts.append(f"  - Mean: {result_data.get('mean'):.2f}")
                parts.append(f"  - Median: {result_data.get('median'):.2f}")
                parts.append(f"  - Std Dev: {result_data.get('std'):.2f}")

            if result_data.get('top_values'):
                parts.append("\nTop Values:")
                for value, count in result_data['top_values'].items():
                    parts.append(f"  - {value}: {count}")

        elif response_type == "basic_info":
            # Basic info response
            parts.append(f"\nDataset: {result_data.get('rows')} rows × {result_data.get('columns')} columns")
            parts.append(f"Columns: {', '.join(result_data.get('column_names', []))}")

            if result_data.get('dtypes'):
                parts.append("\nColumn Types:")
                for col, dtype in result_data['dtypes'].items():
                    parts.append(f"  - {col}: {dtype}")

        elif response_type == "pandasai_query":
            # PandasAI query result
            parts.append(f"\nAI Analysis Result:")
            parts.append(str(result_data))

        elif response_type == "visualization":
            # Visualization response - has image_data
            parts.append(f"\nVisualization Type: {result_data.get('type', 'unknown')}")
            parts.append(f"Message: {result_data.get('message', '')}")
            if result_data.get('column'):
                parts.append(f"Column: {result_data.get('column')}")
            if result_data.get('columns'):
                parts.append(f"Columns: {', '.join(result_data.get('columns', []))}")
            parts.append("\n[A visualization image has been generated and will be displayed to the user]")

        elif response_type == "error":
            # Error response
            parts.append(f"\nError: {csv_data.get('message', 'Unknown error')}")

        else:
            # Generic fallback - just dump the result
            parts.append(f"\nResult Data:")
            parts.append(json.dumps(result_data, indent=2, default=str))

        # Add metadata if available
        if csv_data.get("metadata"):
            metadata = csv_data["metadata"]
            parts.append(f"\nMetadata:")
            parts.append(f"  - Method: {metadata.get('method', 'unknown')}")
            if metadata.get('query'):
                parts.append(f"  - Query: {metadata['query']}")

        return "\n".join(parts)

    @staticmethod
    async def generate_response(
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        use_cache: bool = True
    ) -> str:
        """Generate AI response using OpenAI GPT-4o-mini with caching"""
        try:
            # Check cache first
            if use_cache:
                cache_key = AIService._generate_cache_key(messages, system_prompt)
                cached_response = AIService._get_cached_response(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for request")
                    return cached_response

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

            response_text = response.choices[0].message.content

            # Cache the response
            if use_cache and response_text:
                AIService._cache_response(cache_key, response_text)

            return response_text

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
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
4. Generate data visualizations (charts, plots, graphs) for CSV data
5. Help with data analysis tasks like summarizing data, computing statistics, and identifying patterns

IMPORTANT FOR CSV DATA:
- When a user uploads a CSV file, you WILL receive the complete data analysis in your context
- The CSV data analysis includes: dataset info, column names, data types, statistical summaries, and previews
- You HAVE ACCESS to all this data - you should analyze it and answer questions about it
- Do NOT say you cannot access the data - the data is provided to you in the message content
- If you see "CSV Data Analysis:" in the message, that means you have the data and should analyze it

IMPORTANT FOR VISUALIZATIONS:
- When you see "[A visualization image has been generated and will be displayed to the user]", it means a plot/chart was created
- You should acknowledge the visualization and provide insights about what it shows
- The visualization is automatically shown to the user - you don't need to explain how to create it
- Focus on interpreting the visualization and providing meaningful insights

When discussing images, be specific about what you observe.
When analyzing CSV data, provide clear, actionable insights based on the data you received.
Be concise but informative in your responses."""
