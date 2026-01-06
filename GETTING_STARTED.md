# SmartLensOCR - Getting Started Checklist

## ✅ Prerequisites

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] Git installed (`git --version`)
- [ ] Google Gemini API Key obtained

### Get API Key
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

---

## 🚀 Backend Setup

### Step 1: Navigate to Backend
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

- [ ] Virtual environment created
- [ ] Virtual environment activated

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

- [ ] Dependencies installed successfully
- [ ] No error messages

### Step 4: Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

- [ ] .env file created
- [ ] GEMINI_API_KEY added
- [ ] Other settings reviewed

**Example .env:**
```
GEMINI_API_KEY=AIzaSy... (your actual key)
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

### Step 5: Start Backend
```bash
python main.py
```

Expected output:
```
Uvicorn running on http://0.0.0.0:8000
Application startup complete
```

- [ ] Backend server started
- [ ] Running at http://localhost:8000
- [ ] No errors in console

### Step 6: Verify Backend
```bash
# In another terminal
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","version":"1.0.0"}
```

- [ ] Health check passes
- [ ] API responding correctly

### Step 7: Check API Docs
Visit in browser: http://localhost:8000/docs

- [ ] Swagger UI loads
- [ ] All endpoints visible
- [ ] Looks good

---

## 🎨 Frontend Setup

### Step 1: Navigate to Root
```bash
cd ..
```

(You should be in the SmartLensOCR root directory)

### Step 2: Install Dependencies
```bash
npm install
```

- [ ] npm install completes
- [ ] No warnings about conflicts

### Step 3: Create .env.local (Optional)
If you want to use a different backend URL:
```bash
echo "VITE_API_URL=http://localhost:8000" > .env.local
```

- [ ] .env.local created (if needed)
- [ ] API URL configured

### Step 4: Start Frontend
```bash
npm run dev
```

Expected output:
```
  VITE v6.x.x  ready in ... ms

  ➜  Local:   http://localhost:5173/
```

- [ ] Frontend started successfully
- [ ] Running at http://localhost:5173

### Step 5: Verify Frontend
Visit in browser: http://localhost:5173

Expected:
- [ ] "Smart Lens Pro" login page appears
- [ ] No errors in console (F12)
- [ ] Can type email address
- [ ] Button clickable

---

## 🧪 Integration Test

### Step 1: Login
1. Open http://localhost:5173
2. Enter test email: `test@example.com`
3. Click "Enter Workspace"

- [ ] Login successful
- [ ] App shows main interface
- [ ] Credits displayed (should show 5)

### Step 2: Upload Document
1. Click "Upload Document" (camera icon)
2. Choose an image with text

Expected:
- [ ] Image uploads
- [ ] Shows "Analyzing Grid"
- [ ] Image displays in viewport

- [ ] Upload works
- [ ] Image appears

### Step 3: Detect Regions
Wait for detection to complete.

Expected:
- [ ] Regions detected
- [ ] Blue boxes appear around text
- [ ] Queue tab shows regions
- [ ] Status says "INTERACTING"

- [ ] Region detection works
- [ ] Regions displayed correctly

### Step 4: Extract Text
1. Ensure you have credits (showing 5)
2. Click "EXECUTE PRO SCAN (1 CR)"

Expected:
- [ ] Shows "Backend Processing"
- [ ] Text appears at bottom
- [ ] Credits reduced to 4
- [ ] Can copy text

- [ ] Text extraction works
- [ ] Credits deducted
- [ ] Text displayed

### Step 5: Verify Everything
Check:
- [ ] Text is readable
- [ ] Credits decreased by 1
- [ ] No errors in browser console
- [ ] No errors in backend console

---

## 🐳 Docker Setup (Alternative)

### Step 1: Install Docker
- [ ] Docker Desktop installed
- [ ] Docker running

### Step 2: Build & Run
```bash
# From root directory
docker-compose up --build
```

- [ ] Docker images build successfully
- [ ] Containers start
- [ ] No errors

### Step 3: Access Services
- [ ] Frontend: http://localhost:5173
- [ ] Backend: http://localhost:8000
- [ ] API Docs: http://localhost:8000/docs

### Step 4: Stop Services
```bash
docker-compose down
```

- [ ] Containers stop cleanly

---

## 📚 Documentation Review

Read in this order:

1. [ ] **QUICK_REFERENCE.md** - Quick overview
2. [ ] **BACKEND_IMPLEMENTATION.md** - What was built
3. [ ] **backend/README.md** - Backend details
4. [ ] **INTEGRATION_GUIDE.md** - Full integration
5. [ ] **DEPLOYMENT.md** - For production

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error: ModuleNotFoundError**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error: Port 8000 already in use**
```bash
# Solution: Kill the process
lsof -i :8000
kill -9 <PID>
# Or use different port
python main.py --port 8001
```

**Error: No GEMINI_API_KEY**
```bash
# Solution: Add to .env
GEMINI_API_KEY=your_key_here
```

### Frontend Won't Start

**Error: npm command not found**
```bash
# Install Node.js from nodejs.org
node --version  # Should show v18+
```

**Error: Port 5173 in use**
```bash
# Vite will use next available port automatically
# Or: kill process using port 5173
```

**Error: Cannot find module**
```bash
# Solution: Install dependencies
npm install
```

### Can't Connect

**Frontend → Backend not connecting**

Check:
1. [ ] Backend running at http://localhost:8000
2. [ ] Frontend can reach it: check Network tab (F12)
3. [ ] CORS not showing errors
4. [ ] Firewall not blocking

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check API docs
curl http://localhost:8000/docs
```

### Image Upload Fails

1. [ ] Check browser console (F12) for errors
2. [ ] Check backend logs for errors
3. [ ] Ensure image is PNG/JPEG
4. [ ] Try smaller image (under 5MB)

### Region Detection Fails

Check:
1. [ ] GEMINI_API_KEY is valid
2. [ ] API quota not exceeded
3. [ ] Image has clear text
4. [ ] Backend console shows error?

---

## 🎯 Success Criteria

You're done when:

✅ Backend running at http://localhost:8000
✅ Frontend running at http://localhost:5173
✅ Can login with email
✅ Can upload document image
✅ Can detect regions
✅ Can extract text
✅ Credits deducted correctly
✅ No errors in consoles
✅ API docs work at /docs

---

## 📝 Next Steps

Once everything is working:

1. **Explore the Code**
   - Review main.py (550 lines)
   - Check App.tsx (React component)
   - Review services/geminiService.ts

2. **Customize**
   - Modify AI prompts
   - Change credit costs
   - Update styling
   - Add features

3. **Test More**
   - Try different document types
   - Test with multiple users
   - Run pytest tests
   - Check API docs

4. **Deploy**
   - Follow DEPLOYMENT.md
   - Choose your platform
   - Set up production environment
   - Configure monitoring

---

## 💡 Tips

1. **Keep terminals open** - One for backend, one for frontend
2. **Watch for changes** - Both auto-reload in dev mode
3. **Check .env files** - API keys must be configured
4. **Use API docs** - /docs is your friend
5. **Check browser console** - F12 for frontend errors
6. **Check terminal console** - For backend errors
7. **Search documentation** - Read QUICK_REFERENCE.md first

---

## 📞 Get Help

1. Check **QUICK_REFERENCE.md** for troubleshooting
2. Read **backend/README.md** for backend help
3. Visit **http://localhost:8000/docs** for API help
4. Check error messages carefully
5. Search documentation files

---

## ✨ You're Ready!

Once you have all checkboxes completed, your SmartLensOCR application is fully operational and ready for:
- ✅ Development
- ✅ Testing
- ✅ Customization
- ✅ Deployment

Enjoy! 🚀

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Difficulty**: Beginner-friendly
**Time Required**: 15-20 minutes
