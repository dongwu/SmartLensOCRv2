# SmartLensOCR Backend

A FastAPI-based backend server for intelligent document OCR processing using Google's Gemini AI.

## Features

- **Text Region Detection**: Uses Gemini's vision model to identify and locate text blocks in images
- **OCR Extraction**: Performs high-precision text extraction with custom region ordering
- **User Management**: User authentication and credit-based billing system
- **SQLite Database**: Lightweight, file-based database for users and transactions

## Architecture

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── smartlensocr.db        # SQLite database (created at runtime)
└── README.md              # This file
```

## Prerequisites

- Python 3.9 or higher
- Google Generative AI API key (from [Google AI Studio](https://aistudio.google.com))
- pip (Python package manager)

## Installation

### 1. Set up virtual environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Running the Backend

### Development Mode (with auto-reload)

```bash
python main.py
```

The server will start at `http://localhost:8000`

### Production Mode

```bash
ENVIRONMENT=production uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /health
```

Returns server status and version.

### User Management

#### Create or Get User
```http
POST /api/users
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "id": "usr_abc123",
  "email": "user@example.com",
  "credits": 5,
  "isPro": false,
  "created_at": "2024-01-10T15:30:00"
}
```

#### Get User
```http
GET /api/users/{user_id}
```

#### Update Credits
```http
POST /api/users/{user_id}/credits
Content-Type: application/json

{
  "amount": -1
}
```

### OCR Operations

#### Detect Text Regions
```http
POST /api/detect-regions
Content-Type: application/json

{
  "imageBase64": "data:image/png;base64,..."
}
```

**Response:**
```json
{
  "regions": [
    {
      "id": "region_0_1234567890",
      "description": "Document Header",
      "box": {
        "ymin": 0,
        "xmin": 0,
        "ymax": 100,
        "xmax": 500
      },
      "order": 1,
      "isActive": true
    }
  ]
}
```

#### Extract Text from Regions
```http
POST /api/extract-text
Content-Type: application/json

{
  "imageBase64": "data:image/png;base64,...",
  "regions": [
    {
      "id": "region_0_1234567890",
      "description": "Header",
      "box": {"ymin": 0, "xmin": 0, "ymax": 100, "xmax": 500},
      "order": 1,
      "isActive": true
    }
  ]
}
```

**Response:**
```json
{
  "extractedText": "Document Title\nAuthor: John Doe\n\n..."
}
```

#### Process Complete Document
```http
POST /api/process-document
Content-Type: multipart/form-data

[File upload: document.png]
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  credits INTEGER DEFAULT 5,
  isPro INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  amount INTEGER NOT NULL,
  type TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users (id)
);
```

## Configuration Options

Environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Google Generative AI API key |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `8000` | Server port |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `DATABASE_URL` | `sqlite:///smartlensocr.db` | Database connection URL |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL for CORS |

## Service Layer: GeminiService

The `GeminiService` class handles all interactions with Google's Gemini API:

### detect_regions(base64_image: str) -> List[dict]
Analyzes an image and returns detected text regions with bounding boxes (0-1000 range).

**Features:**
- Automatic paragraph grouping
- Normalized coordinates
- JSON response with descriptions

### extract_text_from_regions(base64_image: str, regions: List[TextRegion]) -> str
Extracts text from specified regions in order.

**Features:**
- Region-specific OCR
- Maintains text order
- Handles special formatting

## Development Tips

### Testing Endpoints

Use `curl` or Postman to test endpoints:

```bash
# Test health
curl http://localhost:8000/health

# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### Debugging

Enable debug logging in `main.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

1. **`ModuleNotFoundError: No module named 'google'`**
   - Run: `pip install -r requirements.txt`

2. **API Key Error**
   - Verify `GEMINI_API_KEY` in `.env`
   - Check at [Google AI Studio](https://aistudio.google.com/app/apikey)

3. **CORS Errors**
   - Update `FRONTEND_URL` in `.env`
   - Or modify CORS origins in `main.py`

4. **Database Lock**
   - Delete `smartlensocr.db` and restart
   - Database will auto-initialize

## Performance Considerations

- **Region Detection**: ~2-5 seconds per image (depends on size and complexity)
- **Text Extraction**: ~3-8 seconds per image (depends on text density)
- **Concurrent Requests**: FastAPI handles async operations efficiently
- **Database**: SQLite suitable for <1000 concurrent users

For production deployment:
- Consider upgrading to PostgreSQL for better concurrency
- Implement caching for frequently processed images
- Add rate limiting per user/API key
- Use Redis for session management

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/main.py .
ENV GEMINI_API_KEY=your_key_here
ENV PORT=8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Heroku/Cloud Run

1. Set environment variables in platform dashboard
2. Deploy `backend/` folder
3. Ensure `Procfile` or equivalent is configured

## API Integration with Frontend

The frontend (React app) communicates with this backend:

```typescript
// Frontend example
const detectRegions = async (imageBase64: string) => {
  const response = await fetch('http://localhost:8000/api/detect-regions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ imageBase64 })
  });
  return response.json();
};
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the [GitHub Issues](https://github.com/yourusername/SmartLensOCR/issues)
2. Review API documentation at `/docs` endpoint
3. Check environment configuration

## Roadmap

- [ ] WebSocket support for real-time processing
- [ ] Batch processing API for multiple documents
- [ ] Advanced text formatting preservation
- [ ] Multi-language OCR support
- [ ] Custom ML model fine-tuning
- [ ] API rate limiting and quotas
- [ ] User analytics dashboard
