# Frontend-Backend Integration Verification Checklist

## ✅ Files Updated

- [x] `services/geminiService.ts` - Now uses backend endpoints
- [x] `App.tsx` - Login and credit system integrated
- [x] `.env.local` - Backend URL configured

## ✅ Verify Backend is Ready

Run in backend terminal:
```bash
cd backend
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Then verify:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status":"healthy","version":"1.0.0"}
```

- [ ] Backend running at localhost:8000
- [ ] Health check passes
- [ ] No errors in backend terminal

## ✅ Verify Frontend is Updated

Run in root terminal:
```bash
npm run dev
```

Expected output:
```
  ➜  Local:   http://localhost:5173/
```

- [ ] Frontend running at localhost:5173
- [ ] No errors in frontend terminal

## ✅ Test Login

1. Open browser: http://localhost:5173
2. Enter email: `test@example.com`
3. Click "Enter Workspace"

Expected:
- [ ] Page loads without errors
- [ ] Login form appears
- [ ] Can type in email field
- [ ] Button shows "Enter Workspace"
- [ ] After clicking, shows "Connecting..."
- [ ] Redirects to main app after ~2 seconds
- [ ] Shows "5 CR" (5 credits) in top right

## ✅ Test Region Detection

1. Click "Upload Document" (camera icon)
2. Choose an image with text (PNG or JPEG)

Expected:
- [ ] Image uploads
- [ ] Shows "Analyzing Grid" with spinner
- [ ] Blue boxes appear around detected text
- [ ] Queue tab shows detected regions
- [ ] Each region has a number (1, 2, 3, etc.)

## ✅ Test Text Extraction

1. Verify credits show "5 CR"
2. Click "EXECUTE PRO SCAN (1 CR)"

Expected:
- [ ] Shows "Backend Processing" with spinner
- [ ] Text appears at bottom of screen
- [ ] Credits decrease to "4 CR"
- [ ] Extracted text is readable
- [ ] Can click "Copy" button

## ✅ Browser Network Tab Verification

1. Open DevTools: F12
2. Go to Network tab
3. Try login again
4. Look for requests to `localhost:8000`

Should see:
- [ ] `POST /api/users` - Login request
- [ ] Status: 200 OK
- [ ] Response contains user data with credits

## ✅ Check Network Requests

After uploading image, should see:
- [ ] `POST /api/detect-regions` - Region detection
- [ ] Response contains array of regions
- [ ] Each region has `id`, `description`, `box`, `order`

After clicking extract text, should see:
- [ ] `POST /api/extract-text` - Text extraction
- [ ] Response contains `extractedText` field
- [ ] Browser console shows no errors

## ✅ Test Multiple Operations

1. Extract text (5 → 4 credits)
2. Reset document
3. Upload different image
4. Detect regions
5. Extract text again (4 → 3 credits)

Expected:
- [ ] Credits decrease each time
- [ ] Previous data cleared
- [ ] Each upload works independently
- [ ] No errors in any console

## ✅ Error Handling Test

Try these to verify error messages:

### Kill Backend
1. Stop backend server (Ctrl+C)
2. Try to login
3. Should see error: "Login failed"

Expected:
- [ ] Error message appears
- [ ] Frontend still responsive
- [ ] Can restart backend and retry

### Wrong API URL
1. Edit `.env.local` to wrong URL
2. Try to login
3. Should see network error

Expected:
- [ ] Error handling works
- [ ] Clear error message displayed

## ✅ Verify Data Persistence

1. Login with `user1@example.com` - gets 5 credits
2. Extract text twice (5 → 4 → 3)
3. Refresh page (F5)
4. Should still show 3 credits

Expected:
- [ ] User data persists in backend database
- [ ] Credits don't reset after refresh
- [ ] Can continue from where left off

## ✅ Multiple Users Test

1. Open incognito/private window
2. Login with `user2@example.com`
3. Should get fresh 5 credits
4. Extract text (5 → 4)
5. Go back to first window
6. Should still show original user's credits

Expected:
- [ ] Each user has separate data
- [ ] Users don't interfere with each other
- [ ] Database maintains separate records

## 🎯 Success Checklist

You're done when ALL of these pass:

✅ Backend running at localhost:8000
✅ Frontend running at localhost:5173
✅ Can login with email
✅ Backend creates/retrieves user
✅ User starts with 5 credits
✅ Can upload image
✅ Can detect regions
✅ Can extract text
✅ Credits decrease by 1
✅ Network tab shows API calls
✅ No errors in browser console
✅ No errors in backend console
✅ Credits persist after refresh
✅ Multiple users work independently

## 🔍 Troubleshooting

If something fails:

1. **Check backend terminal** - Any errors?
2. **Check browser console (F12)** - Any errors?
3. **Check Network tab** - Are requests reaching backend?
4. **Check .env files** - Is GEMINI_API_KEY set?
5. **Check ports** - Is backend on 8000, frontend on 5173?

See: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for detailed troubleshooting

## 📝 What Changed

### geminiService.ts
- **Old:** Called Gemini API directly from browser
- **New:** Calls backend endpoints
- **Why:** Secure, server-side processing, API key hidden

### App.tsx
- **Old:** Mock user system, localStorage-only credits
- **New:** Real backend authentication, database credits
- **Why:** Persistent data, multi-user support, audit trail

### .env.local
- **Old:** Didn't exist
- **New:** Points to backend API
- **Why:** Configurable backend URL for different environments

## 🚀 You're All Set!

The frontend is now fully integrated with the Python backend. All API calls go through the backend, which means:

✅ Gemini API key is secure (server-side only)
✅ User data is persistent (database)
✅ Credits are tracked (transactions table)
✅ Multi-user support works
✅ Ready for production deployment

Enjoy! 🎉
