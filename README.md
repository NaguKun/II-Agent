# Chat Application with FastAPI & MongoDB

A lightweight chat application that supports multi-turn conversations, image chat, and CSV data analysis.

## Features

- **Multi-turn Conversations**: Persistent chat history with MongoDB
- **Image Chat**: Upload and discuss images (PNG/JPG)
- **CSV Data Analysis**: Upload CSV files or provide URLs for data analysis
- **AI Integration**: Ready for Claude API integration
- **RESTful API**: Clean FastAPI endpoints with automatic documentation

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas (with Motor async driver)
- **AI Model**: OpenAI GPT-4o-mini
- **Data Analysis**: Pandas, NumPy
- **Image Processing**: Pillow
- **Validation**: Pydantic

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── database.py            # MongoDB connection manager
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── routers/
│   ├── conversations.py  # Conversation endpoints
│   └── chat.py           # Chat and messaging endpoints
└── services/
    ├── chat_service.py   # Chat business logic
    ├── image_service.py  # Image processing
    ├── csv_service.py    # CSV analysis
    └── ai_service.py     # AI integration (placeholder)
```

## Setup Instructions

### 1. Set Up MongoDB Atlas

Create a free MongoDB Atlas cluster:

1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account and cluster
3. Create a database user (username & password)
4. Whitelist your IP address (or use 0.0.0.0/0 for testing)
5. Get your connection string (it looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)

**Alternative**: Use local MongoDB if you prefer:
- Download from: https://www.mongodb.com/try/download/community
- Connection string will be: `mongodb://localhost:27017`

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# MongoDB Atlas connection string (replace username, password, and cluster)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=chat_app

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# File upload settings
MAX_FILE_SIZE_MB=10
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg
```

**Important**:
- Replace `username`, `password`, and `cluster` in the MongoDB URL with your actual credentials
- Get your OpenAI API key from https://platform.openai.com/api-keys

### 4. Run the Application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

### Conversations

- `POST /api/conversations/` - Create a new conversation
- `GET /api/conversations/` - List all conversations
- `GET /api/conversations/{id}` - Get specific conversation
- `DELETE /api/conversations/{id}` - Delete conversation
- `GET /api/conversations/{id}/messages` - Get conversation messages
- `PATCH /api/conversations/{id}/title` - Update conversation title

### Chat

- `POST /api/chat/message` - Send a message (supports text, image, CSV URL)
- `POST /api/chat/upload-csv` - Upload and analyze CSV file
- `POST /api/chat/analyze-csv` - Analyze CSV from URL

## Usage Examples

### 1. Create a Conversation

```bash
curl -X POST "http://localhost:8000/api/conversations/" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Chat"}'
```

### 2. Send a Text Message

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -F "conversation_id=YOUR_CONVERSATION_ID" \
  -F "content=Hello, how are you?"
```

### 3. Send a Message with Image

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -F "conversation_id=YOUR_CONVERSATION_ID" \
  -F "content=What's in this image?" \
  -F "image_data=data:image/jpeg;base64,YOUR_BASE64_IMAGE"
```

### 4. Analyze CSV from URL

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -F "conversation_id=YOUR_CONVERSATION_ID" \
  -F "content=Summarize this dataset" \
  -F "csv_url=https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv"
```

### 5. Upload CSV File

```bash
curl -X POST "http://localhost:8000/api/chat/upload-csv" \
  -F "conversation_id=YOUR_CONVERSATION_ID" \
  -F "query=show basic stats" \
  -F "file=@path/to/your/file.csv"
```

## CSV Analysis Features

The application can answer questions like:

- "Summarize the dataset"
- "Show basic stats for numeric columns"
- "Which column has the most missing values?"
- "Show a histogram of price"
- "What are the top values in category column?"

### Available Analysis Types:

1. **Summary** - Complete dataset overview
2. **Statistics** - Numeric column statistics
3. **Missing Values** - Missing data analysis
4. **Histogram** - Distribution of numeric columns
5. **Column Info** - Detailed column information
6. **Preview** - Sample rows from the dataset

## AI Integration

The application is fully integrated with **OpenAI GPT-4o-mini**:

### Features:
- Multi-turn conversational AI
- Image understanding and analysis
- CSV data analysis and insights
- Natural language responses

### Setup:
1. Get your API key from https://platform.openai.com/api-keys
2. Add it to your `.env` file:
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

The AI will automatically:
- Answer questions about uploaded images
- Provide insights on CSV data
- Maintain conversation context across messages

## Database Schema

### Conversations Collection

```json
{
  "_id": ObjectId,
  "title": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "number",
  "metadata": {}
}
```

### Messages Collection

```json
{
  "_id": ObjectId,
  "conversation_id": "string",
  "role": "user|assistant|system",
  "content": [
    {
      "type": "text|image|csv",
      "text": "string (optional)",
      "image_url": "string (optional)",
      "csv_data": {} (optional),
      "csv_url": "string (optional)"
    }
  ],
  "timestamp": "datetime",
  "metadata": {}
}
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid input, CSV parsing errors
- **404 Not Found**: Conversation/resource not found
- **500 Internal Server Error**: Server-side errors

All errors return JSON with a `detail` field explaining the issue.

## Security Notes

- Don't commit `.env` file to version control
- In production, restrict CORS origins to your frontend domain
- Consider adding authentication/authorization
- Validate and sanitize all user inputs
- Limit file upload sizes

## Development

### Run with Auto-Reload

```bash
uvicorn main:app --reload
```

### Access Interactive API Docs

Visit http://localhost:8000/docs for Swagger UI documentation.

### MongoDB GUI Tools

- MongoDB Compass: https://www.mongodb.com/products/compass
- Studio 3T: https://studio3t.com/

## Testing

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Future Enhancements

- [ ] User authentication and authorization
- [ ] Real-time chat with WebSockets
- [ ] Message reactions and threading
- [ ] File attachments (PDF, documents)
- [ ] Advanced data visualizations
- [ ] Export conversation history
- [ ] Multi-language support
- [ ] Rate limiting
- [ ] Caching layer (Redis)

## Troubleshooting

### MongoDB Connection Issues

```
Failed to connect to MongoDB
```

**Solution**:
- Check your MongoDB Atlas connection string is correct
- Ensure username and password are properly encoded in the URL
- Verify your IP address is whitelisted in MongoDB Atlas
- Check `MONGODB_URL` in `.env` matches your cluster details
- For special characters in password, use URL encoding (%40 for @, %23 for #, etc.)

### Large File Upload Errors

```
Image size exceeds 10MB limit
```

**Solution**:
- Reduce image size
- Adjust `MAX_FILE_SIZE_MB` in `.env`

### CSV Parsing Errors

```
Error parsing CSV
```

**Solution**:
- Ensure CSV is properly formatted
- Check URL is accessible
- Verify file encoding (UTF-8 recommended)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
