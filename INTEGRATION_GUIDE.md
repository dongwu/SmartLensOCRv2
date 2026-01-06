# SmartLensOCR - Complete Integration Guide

## Overview

This document provides everything you need to understand and run the complete SmartLensOCR application, including both frontend and backend.

## Project Structure

```
SmartLensOCR/
├── Frontend (React + Vite)
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   ├── index.tsx            # React entry point
│   │   ├── types.ts             # TypeScript types
│   │   ├── services/
│   │   │   └── geminiService.ts # Gemini API integration
│   │   └── components/
│   │       ├── RegionOverlay.tsx
│   │       └── PricingModal.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.local               # Frontend config
│
├── Backend (FastAPI + Python)
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Database models
│   ├── config.py                # Configuration management
│   ├── test_main.py            # Unit tests
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example             # Backend config template
│   ├── Dockerfile               # Docker configuration
│   ├── start.sh                 # Startup script
│   ├── README.md                # Backend documentation
│   └── smartlensocr.db          # SQLite database (auto-generated)
│
├── docker-compose.yml           # Multi-container orchestration
├── Dockerfile                   # Frontend Docker config
├── README.md                    # Root documentation
└── .gitignore
```

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm (for frontend)
- **Python** 3.9+ and pip (for backend)
- **Google Gemini API Key** ([Get here](https://aistudio.google.com/app/apikey))

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start the server
python main.py
# OR use the startup script:
chmod +x start.sh
./start.sh
```

Backend runs at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
# Navigate to root
cd ..

# Install dependencies
npm install

# Configure environment
# Create .env.local if needed and set GEMINI_API_KEY

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:5173`

### 3. Using Docker (Optional)

```bash
# From root directory
docker-compose up --build

# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Application Flow

### User Journey

```
1. User Opens App
   ↓
2. Login with Email
   ↓
3. Create/Retrieve User (Backend)
   └─ Get initial 5 credits
   ↓
4. Upload Document Image
   ↓
5. Region Detection (Gemini Vision)
   └─ AI identifies text blocks
   ↓
6. User Reviews & Reorders Regions
   ↓
7. Click "Execute Pro Scan"
   ↓
8. Text Extraction (Gemini OCR)
   ↓
9. Display Extracted Text
   └─ Deduct 1 credit
   ↓
10. Copy or Reprocess
```

### API Communication Flow

```
Frontend (React)
    ↓
    ├─ POST /api/users
    │  (Create/login user)
    │
    ├─ POST /api/detect-regions
    │  (Send base64 image)
    │  ↓
    │  Backend (FastAPI)
    │  ├─ GeminiService.detect_regions()
    │  │  └─ Gemini API (Vision)
    │  └─ Return regions with bounding boxes
    │
    └─ POST /api/extract-text
       (Send image + selected regions)
       ↓
       Backend (FastAPI)
       ├─ GeminiService.extract_text_from_regions()
       │  └─ Gemini API (OCR)
       ├─ Update user credits
       └─ Return extracted text
```

## Backend Architecture

### Layers

#### 1. **API Layer** (main.py)
- FastAPI endpoints
- CORS middleware
- Request/response handling
- Error handling

#### 2. **Service Layer** (GeminiService)
- Gemini API interactions
- Image processing
- Region detection logic
- Text extraction logic

#### 3. **Data Layer** (models.py)
- SQLite database operations
- User management
- Transaction tracking
- Query builders

#### 4. **Configuration Layer** (config.py)
- Environment variable management
- Application settings
- Database configuration
- API keys

### Database Schema

#### Users Table
```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  credits INTEGER DEFAULT 5,
  isPro INTEGER DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

#### Transactions Table
```sql
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY,
  user_id TEXT,
  amount INTEGER,
  type TEXT,              -- 'credit', 'debit'
  description TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### Processing Logs Table
```sql
CREATE TABLE processing_logs (
  id INTEGER PRIMARY KEY,
  user_id TEXT,
  operation TEXT,         -- 'detect', 'extract'
  status TEXT,            -- 'success', 'error'
  details TEXT,
  created_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Frontend Architecture

### State Management

```typescript
// App State
- appState: AppState              // IDLE, UPLOADING, DETECTING_REGIONS, etc.
- image: string | null            // Base64 encoded image
- regions: TextRegion[]           // Detected regions
- selectedId: string | null       // Currently selected region
- finalText: string               // Extracted text result
- user: User | null              // Current logged-in user
- error: string | null           // Error messages
```

### Components

1. **App.tsx** (Main Container)
   - State management
   - API calls
   - Layout orchestration

2. **RegionOverlay.tsx**
   - Visual region markers
   - Region selection
   - Interactive overlay

3. **PricingModal.tsx**
   - Credit purchase UI
   - Billing information

## Customization Guide

### Adding Custom Prompts

Edit the prompt in `backend/main.py`:

```python
# For region detection
prompt = """Identify all major blocks of text...
[Your custom instructions]
"""

# For text extraction
prompt = """Perform OCR on the provided image...
[Your custom instructions]
"""
```

### Modifying Credit System

In `backend/config.py`:

```python
# Change credit costs
CREDITS_PER_DETECTION = 0  # Free
CREDITS_PER_EXTRACTION = 1  # Paid

# Change initial credits
INITIAL_CREDITS = 5
```

### Updating API Models

Define in `backend/main.py`:

```python
class CustomRequest(BaseModel):
    field1: str
    field2: int
    
@app.post("/api/custom-endpoint")
async def custom_endpoint(request: CustomRequest):
    return {"result": "..."}
```

### Styling Frontend

Frontend uses Tailwind CSS. Modify classes in React components:

```tsx
// App.tsx
<button className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg p-4">
  Button
</button>
```

## Deployment

### Production Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Update `CORS_ORIGINS` in `backend/config.py`
- [ ] Set strong database password/use PostgreSQL
- [ ] Configure HTTPS/SSL
- [ ] Set up error logging (Sentry, etc.)
- [ ] Add rate limiting
- [ ] Implement API key authentication
- [ ] Set up monitoring (New Relic, etc.)
- [ ] Configure backup strategy

### Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name

# Deploy backend
git subtree push --prefix backend heroku main

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key
```

#### Google Cloud Run
```bash
# Backend
gcloud run deploy smartlensocr-backend \
  --source=backend \
  --platform=managed \
  --region=us-central1 \
  --set-env-vars=GEMINI_API_KEY=your_key

# Frontend (use Cloud Storage + Cloud CDN)
gsutil -m cp -r dist/* gs://your-bucket/
```

#### AWS Lambda + API Gateway
- Package backend with Zappa or Serverless Framework
- Deploy frontend to S3 + CloudFront
- Use API Gateway for backend endpoints

### Docker Deployment

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop containers
docker-compose down
```

## API Endpoint Reference

### Authentication
```
POST /api/users
Content-Type: application/json
{
  "email": "user@example.com"
}
```

### Document Processing
```
POST /api/detect-regions
POST /api/extract-text
POST /api/process-document
```

### User Management
```
GET /api/users/{user_id}
POST /api/users/{user_id}/credits
```

Full documentation available at `/docs` endpoint when server is running.

## Troubleshooting

### Backend Issues

#### "GEMINI_API_KEY not found"
```bash
# Make sure .env file exists in backend directory
cp .env.example .env
# Add your key to .env
```

#### "Port 8000 already in use"
```bash
# Use a different port
python main.py --port 8001
# Or find and kill existing process
lsof -i :8000
kill -9 <PID>
```

#### "Database locked"
```bash
# Remove database and restart
rm backend/smartlensocr.db
python main.py
# Database will auto-initialize
```

### Frontend Issues

#### "Cannot find module '@google/genai'"
```bash
# Reinstall dependencies
npm install
# Or update
npm update @google/genai
```

#### "CORS errors in browser console"
```
# Make sure backend is running
# Check CORS origins in backend/config.py
# Ensure frontend URL matches CORS_ORIGINS
```

## Performance Optimization

### Backend
- Implement Redis caching for processed images
- Use async database operations
- Add request pooling
- Implement image compression before Gemini API

### Frontend
- Lazy load components
- Optimize image display with Canvas
- Implement request debouncing
- Add service worker for offline support

## Security Considerations

1. **API Key Security**
   - Never commit `.env` files
   - Use environment variables
   - Rotate keys regularly

2. **Database Security**
   - Use PostgreSQL for production (not SQLite)
   - Encrypt sensitive fields
   - Regular backups

3. **API Security**
   - Implement rate limiting
   - Use API keys for frontend → backend
   - Validate all inputs
   - HTTPS only in production

4. **User Data**
   - Don't store processed images
   - Delete logs after retention period
   - GDPR compliance

## Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest -v               # Verbose output
pytest test_main.py::TestUserManagement  # Specific test class
pytest -k "credit"      # Tests matching pattern
```

### Frontend Testing (Add Later)
```bash
npm test                # Jest/Vitest
npm run test:e2e       # End-to-end tests
```

## Monitoring & Logging

### Backend Logs
```bash
# View backend logs
docker-compose logs -f backend

# Or directly
python main.py 2>&1 | tee logs/backend.log
```

### Frontend Errors
- Check browser console: `F12` → Console
- Network tab for API calls
- React DevTools extension

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request
5. Code review before merge

## License

MIT License - See LICENSE file

## Support & Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **GitHub Issues**: Create an issue for bugs/features

## FAQ

**Q: Can I use a different AI provider?**
A: Yes, modify `GeminiService` in backend/main.py to use OpenAI, Claude, etc.

**Q: How do I add more users?**
A: Users are created automatically on first login via `/api/users` endpoint.

**Q: Can I modify the UI?**
A: Yes, edit React components in src/ directory. Frontend is fully customizable.

**Q: How do I add payment processing?**
A: Integrate Stripe/PayPal in the pricing modal and credit endpoint.

**Q: Is it production-ready?**
A: It's a solid foundation. Add monitoring, logging, and security before production.

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Maintainer**: Your Team
