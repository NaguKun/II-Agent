# Chat Application API

Multi-turn chat application with image and CSV data support, powered by FastAPI and OpenAI.

## Features

- Multi-turn conversational chat with OpenAI GPT models
- Image upload and analysis
- CSV file upload and natural language querying
- CSV data visualization (histograms, scatter plots, heatmaps, etc.)
- AI-powered CSV insights using PandasAI
- MongoDB for conversation persistence
- RESTful API with streaming support

## How to Run Locally

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB instance)
- OpenAI API key

### Installation Steps

1. **Clone the repository**
   ```bash
   cd path/to/project
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

   Edit `.env` file with your credentials:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=chat_app
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   MAX_FILE_SIZE_MB=10
   ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at: `http://localhost:8000`

6. **Access the API documentation**

   Open your browser and navigate to:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Quick Test

Test if the API is running:
```bash
curl http://localhost:8000
```

Expected response:
```json
{
  "message": "Chat Application API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## API Endpoints

### Chat API (v2)
- `POST /api/v2/chat/sessions` - Create new chat session
- `GET /api/v2/chat/sessions` - List all sessions
- `POST /api/v2/chat/stream` - Send message with streaming response
- `POST /api/v2/chat/csv/upload` - Upload CSV file
- `GET /api/v2/chat/csv/suggestions` - Get suggested questions for CSV

### Legacy Chat API (v1)
- `POST /api/chat/message` - Send chat message
- `POST /api/chat/upload-csv` - Upload and analyze CSV
- `POST /api/chat/analyze-csv` - Analyze CSV from URL

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | Required |
| `DATABASE_NAME` | Database name | `chat_app` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `MAX_FILE_SIZE_MB` | Max file upload size | `10` |
| `ALLOWED_IMAGE_TYPES` | Allowed image MIME types | `image/jpeg,image/png,image/jpg` |

## Technology Stack

- **FastAPI** - Modern web framework
- **MongoDB** - Database for conversations
- **OpenAI API** - AI chat capabilities
- **PandasAI** - Natural language CSV querying
- **Pandas** - Data analysis
- **Matplotlib/Seaborn** - Data visualization
- **aiohttp** - Async HTTP client

## Running frontend
 ```bash
   cd ai-chat-frontend
   npm run dev
   ```