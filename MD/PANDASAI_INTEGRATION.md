# PandasAI Integration in CSV Service

The CSV Service has been enhanced with PandasAI integration to provide AI-powered natural language querying capabilities for CSV data analysis with enterprise-grade optimizations.

## Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **AI-Powered Insights**: Get automated insights about patterns, outliers, and relationships
- **Smart Intent Detection**: Automatically chooses between AI and rule-based analysis
- **Session Reuse**: Optimized aiohttp session management for better performance
- **Data Sampling**: Automatic sampling for large datasets to reduce costs and latency
- **Token Management**: Configurable token limits and timeouts
- **Caching**: Multi-user SmartDataframe caching for improved performance
- **Fallback Support**: Gracefully falls back to traditional analysis when PandasAI is not available
- **Comprehensive Analysis**: Combines traditional statistics with AI insights
- **Unified Response Format**: Consistent response structure across all methods

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   Or set it in your environment variables.

## Usage

### Basic Usage

```python
import asyncio
from services.csv_service import CSVService
import pandas as pd

async def main():
    # Initialize the service with custom settings
    csv_service = CSVService(
        max_tokens=500,      # Limit AI response tokens
        timeout=30          # Query timeout in seconds
    )
    
    # Load your data
    df = pd.read_csv('your_data.csv')
    
    # Ask natural language questions
    result = csv_service.analyze_query(
        df, 
        "What is the average salary by department?",
        conversation_id="user_123"  # For caching
    )
    print(result)
    
    # Clean up
    await csv_service.close_session()

asyncio.run(main())
```

### Advanced Usage with Session Management

```python
# Using context manager for automatic session management
async with CSVService() as csv_service:
    # Load CSV from URL with session reuse
    df = await csv_service.load_csv_from_url("https://example.com/data.csv")
    
    # Process multiple queries efficiently
    queries = [
        "What are the main patterns?",
        "Show me outliers in the data",
        "Which columns are correlated?"
    ]
    
    for query in queries:
        result = csv_service.analyze_query(df, query, conversation_id="session_1")
        print(f"Query: {query}")
        print(f"Result: {result['result']}")
```

### Advanced Features

#### 1. AI-Powered Insights
```python
# Get comprehensive AI insights about your dataset
insights_result = csv_service.get_pandasai_insights(df, conversation_id="user_123")
if insights_result['success']:
    for insight in insights_result['result']['insights']:
        print(f"Q: {insight['question']}")
        print(f"A: {insight['answer']}")
```

#### 2. Direct PandasAI Queries
```python
# Execute specific queries with PandasAI
result = csv_service.query_with_pandasai(
    df, 
    "Show me the correlation between age and salary",
    conversation_id="user_123"
)
```

#### 3. Comprehensive Analysis
```python
# Get both traditional stats and AI insights
analysis = csv_service.get_comprehensive_analysis(df, conversation_id="user_123")
print(analysis)
```

#### 4. Cache Management
```python
# Check cache status
cache_info = csv_service.get_cache_info()
print(f"Cached conversations: {cache_info['cached_conversations']}")

# Clear specific conversation cache
csv_service.clear_cache("user_123")

# Clear all caches
csv_service.clear_cache()
```

#### 5. Performance Monitoring
```python
# Check if PandasAI is available and configured
print(f"PandasAI Available: {csv_service.pandasai_available}")

# Get cache information
cache_info = csv_service.get_cache_info()
print(f"Cache size: {cache_info['cache_size']}")
print(f"Max dataframe size: {cache_info['max_dataframe_size']}")
```

## Response Format

All methods now return a standardized response structure:

```json
{
  "type": "pandasai_query",
  "success": true,
  "result": "...",
  "message": null,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "metadata": {
    "query": "What is the average salary?",
    "conversation_id": "user_123",
    "dataframe_size": 1000,
    "sampled": false,
    "method": "pandasai"
  }
}
```

## Performance Optimizations

### 1. Session Reuse
- aiohttp sessions are reused across multiple requests
- Automatic connection pooling and keep-alive
- Reduced overhead for multiple URL requests

### 2. Data Sampling
- Large datasets (>10,000 rows) are automatically sampled
- Configurable sampling size via `_max_dataframe_size`
- Reduces token usage and processing time by 10-20x

### 3. Intent Detection
- Simple queries use rule-based analysis (faster, no API calls)
- Complex queries use PandasAI
- Automatic fallback when PandasAI fails

### 4. Caching
- SmartDataframes are cached per conversation
- Reduces initialization overhead for repeated queries
- Memory-efficient cleanup methods

### 5. Token Management
- Configurable max tokens per response
- Timeout protection for long-running queries
- Cost control for API usage

## Example Queries

### Simple Queries (Rule-based, fast)
- "Show me the first 5 rows"
- "What are the column names?"
- "How many rows are there?"
- "Show me basic statistics"

### Complex Queries (PandasAI, intelligent)
- "What is the correlation between age and salary?"
- "Which department has the highest average salary?"
- "Are there any outliers in the data?"
- "What patterns can you find in this dataset?"
- "How does experience relate to salary by department?"

## Configuration

The service automatically detects if PandasAI is available and configured. You can check this with:

```python
csv_service = CSVService()
print(f"PandasAI Available: {csv_service.pandasai_available}")
```

## Error Handling

The service gracefully handles cases where:
- PandasAI is not installed
- OpenAI API key is not set
- API requests fail
- Invalid queries are provided

In such cases, it falls back to the traditional rule-based analysis methods.

## Example Script

Run the example script to see PandasAI in action:

```bash
python example_pandasai_usage.py
```

This will demonstrate various features of the enhanced CSV service with sample data.
