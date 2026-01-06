# SmartLensOCR - Quick Reference

## 🚀 Quick Start (5 minutes)

### Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 5. Run
python main.py
```

**Backend URL**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs`

### Frontend

```bash
# 1. In root directory
npm install

# 2. Set API key (optional if using local backend)
# Create .env.local if needed

# 3. Start
npm run dev
```

**Frontend URL**: `http://localhost:5173`

---

## 📋 Project Structure

```
SmartLensOCR/
├── backend/               # Python FastAPI backend
│   ├── main.py           # Main application
│   ├── models.py         # Database models
│   ├── config.py         # Configuration
│   ├── requirements.txt   # Dependencies
│   └── .env.example      # Config template
├── src/                  # Frontend source (React)
├── components/           # React components
├── services/             # API services
├── package.json          # Frontend dependencies
└── docker-compose.yml    # Full stack setup
```

---

## 🔌 API Endpoints Summary

### Users
```
POST   /api/users                    # Create/get user
GET    /api/users/{id}              # Get user
POST   /api/users/{id}/credits      # Update credits
```

### OCR
```
POST   /api/detect-regions          # Find text blocks
POST   /api/extract-text            # Extract text
POST   /api/process-document        # Full process
```

### Health
```
GET    /health                      # Check status
GET    /                            # API info
```

---

## 🗂️ Key Files & What They Do

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server, all endpoints |
| `models.py` | Database operations |
| `config.py` | Settings & environment |
| `test_main.py` | Unit tests |
| `.env` | API keys (don't commit!) |
| `requirements.txt` | Python packages |
| `Dockerfile` | Docker image |
| `docker-compose.yml` | Multi-container setup |

---

## 🔑 Environment Variables

```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development  # or: production
FRONTEND_URL=http://localhost:5173
```

Get key: https://aistudio.google.com/app/apikey

---

## 📊 Database Schema (Quick View)

### Users Table
```sql
id (TEXT)        -- User ID
email (TEXT)     -- Email address
credits (INT)    -- Credit balance
isPro (INT)      -- Pro status (0/1)
created_at       -- Timestamp
```

### Transactions Table
```sql
id (INT)         -- Transaction ID
user_id (TEXT)   -- Related user
amount (INT)     -- Credit amount
type (TEXT)      -- 'credit' or 'debit'
created_at       -- Timestamp
```

---

## 🧪 Testing

```bash
cd backend
pytest                  # Run all tests
pytest -v              # Verbose
pytest test_main.py    # Specific file
pytest -k "credit"     # Match pattern
```

---

## 🐳 Docker Commands

```bash
# Build & run
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down

# Clean
docker-compose down -v  # Remove volumes too
```

---

## 📝 Common Tasks

### Check Backend Health
```bash
curl http://localhost:8000/health
```

### Create Test User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

### View API Documentation
```
http://localhost:8000/docs
```

### Reset Database
```bash
rm backend/smartlensocr.db
python backend/main.py
```

### Debug Frontend
```
Open Browser DevTools: F12
Check Console for errors
Check Network tab for API calls
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| No GEMINI_API_KEY | Add to .env file |
| CORS errors | Check backend is running |
| Module not found | `pip install -r requirements.txt` |
| Database locked | Delete smartlensocr.db and restart |
| Frontend not connecting | Check API_URL in environment |

---

## 📚 Documentation Files

- **[README.md](README.md)** - Project overview
- **[backend/README.md](backend/README.md)** - Backend docs
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Full integration
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[BACKEND_IMPLEMENTATION.md](BACKEND_IMPLEMENTATION.md)** - Implementation details

---

## 🚀 Deployment

### Local
```bash
npm run dev          # Frontend
python main.py       # Backend
```

### Docker
```bash
docker-compose up
```

### Production (see DEPLOYMENT.md)
- Heroku
- AWS EC2
- Google Cloud Run
- Vercel (frontend)
- Railway (backend)
- Kubernetes

---

## 💳 Credit System

- **Initial credits**: 5
- **Cost per detection**: 0 (free)
- **Cost per extraction**: 1
- **Max credits**: Unlimited (with purchase)

---

## 🔒 Security Checklist

- [ ] API key in .env (not committed)
- [ ] HTTPS in production
- [ ] CORS origins configured
- [ ] Input validation enabled
- [ ] Rate limiting enabled
- [ ] Database backup configured
- [ ] Error logging enabled
- [ ] Secrets encrypted

---

## 📞 Support Resources

- **Gemini API**: https://ai.google.dev/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev
- **Docker**: https://docs.docker.com
- **Tailwind CSS**: https://tailwindcss.com

---

## 🎯 Architecture Overview

```
Browser
   ↓
Frontend (React + Vite)
   ↓ HTTP
Backend (FastAPI)
   ├─ API endpoints
   ├─ User management
   └─ OCR processing
   ↓
Gemini API (Google)
   ├─ Vision model
   └─ OCR model
   ↓
SQLite Database
   ├─ Users
   ├─ Transactions
   └─ Logs
```

---

## ✅ Checklist Before Going Live

- [ ] API key configured
- [ ] Backend running successfully
- [ ] Frontend connecting to backend
- [ ] Can upload images
- [ ] Region detection works
- [ ] Text extraction works
- [ ] Credits deducted correctly
- [ ] All tests passing
- [ ] Error messages user-friendly
- [ ] Documentation updated
- [ ] Deployed to production
- [ ] Monitoring configured
- [ ] Backups enabled

---

## 💡 Tips & Tricks

1. **Use API docs for testing**: http://localhost:8000/docs
2. **Check logs for errors**: `docker-compose logs`
3. **Browser DevTools for frontend**: F12 → Console & Network
4. **Database viewer**: Use DBeaver or similar for SQLite
5. **API testing**: Use curl, Postman, or Insomnia
6. **Docker cleanup**: `docker system prune`
7. **Venv activate**: Source it before running commands
8. **Hot reload**: Frontend & backend both support auto-reload

---

## 📊 Performance Tips

- **Backend**: Increase pool size for more concurrent requests
- **Frontend**: Enable lazy loading for large images
- **Database**: Add indexes for frequently searched columns
- **Caching**: Implement Redis for processed images
- **Images**: Compress before sending to Gemini

---

## 🔄 Development Workflow

1. Make changes to code
2. Backend auto-reloads (with `--reload`)
3. Frontend hot-reloads (with `npm run dev`)
4. Test in browser
5. Check API docs if needed
6. Commit when working
7. Push to repository

---

## 📱 Mobile Testing

```bash
# Get your machine IP
ifconfig | grep inet

# Access from phone
http://YOUR_IP:5173
```

---

## 🎓 Learning Paths

**If new to FastAPI:**
1. Read backend/README.md
2. Check /docs endpoint
3. Review test_main.py
4. Explore main.py code

**If new to React:**
1. Read App.tsx
2. Review components/
3. Check services/geminiService.ts
4. Experiment with styling

**If new to deployment:**
1. Read DEPLOYMENT.md
2. Try docker-compose first
3. Then try cloud platform
4. Finally production setup

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Status**: Production Ready
