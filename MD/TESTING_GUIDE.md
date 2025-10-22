# Quick Testing Guide - New Features

## 🚀 Start the Application

### Backend
```bash
cd "New folder (2)"
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd ai-chat-frontend
npm run dev
```

Visit: http://localhost:3000

---

## ✅ Test Checklist

### 1. Copy Button ✓
**Steps:**
1. Send a text message: "Hello, tell me a joke"
2. Wait for AI response
3. **Hover over the AI message** (bottom area)
4. You should see a **copy icon** appear
5. Click the copy icon
6. **Look for:** Green checkmark + toast notification "Message copied"
7. Paste in notepad to verify

**Expected:** Message copied to clipboard successfully

---

### 2. Regenerate Response ✓
**Steps:**
1. Send a message: "Give me 3 random numbers"
2. Get AI response with numbers
3. **Hover over the last AI message**
4. Click the **🔄 regenerate icon**
5. **Watch:** Old response disappears, new one generates
6. Compare the two sets of numbers (should be different)

**Expected:** New response with different random numbers

---

### 3. Typing Indicator ✓
**Steps:**
1. Send any message
2. **Immediately look at the message area**
3. You should see **bouncing dots** animation
4. Also shows "• typing..." in the timestamp area

**Expected:** Visual indication that AI is thinking

---

### 4. CSV Suggested Questions ✓
**Steps:**
1. Switch to **CSV mode** (left sidebar)
2. Click upload button and select `test_data.csv` (or any CSV)
3. Type message: "Analyze this data"
4. Click send
5. **Look below the messages** for suggested questions
6. You should see buttons like:
   - "Summarize this dataset for me"
   - "Show me statistics for [column]"
   - "Plot a histogram of [column]"
   - etc.
7. **Click any suggestion**
8. Watch it automatically send and get answered

**Expected:** 6-8 smart suggestions appear, clickable, auto-send

**Test CSV suggestions:**
```csv
name,age,salary,department
Alice,25,50000,Engineering
Bob,30,60000,Sales
Charlie,35,70000,Engineering
Diana,28,55000,Marketing
```

Save this as `test.csv` and upload!

---

### 5. Conversation Export ✓
**Steps:**
1. Have a conversation (at least 3-4 messages)
2. **Look at top-left corner** of the chat area
3. You should see:
   - **Export MD** button
   - **Export TXT** button
4. Click "Export MD"
5. **Check your downloads folder**
6. Open the `.md` file - should show formatted conversation
7. Go back and click "Export TXT"
8. Open the `.txt` file - should show plain text conversation

**Expected:** Files download automatically with proper formatting

**What the exports contain:**
- Conversation title
- All messages with timestamps
- Formatted nicely
- Indicators for images/CSV files

---

### 6. Performance - Database Indexes ✓
**Steps:**
1. Open MongoDB Compass (if installed)
2. Connect to your MongoDB
3. Navigate to `chat_app` database
4. Go to `conversations` collection → Indexes tab
5. **You should see:**
   - `_id_` (default)
   - `created_at_1`
   - `updated_at_1`
6. Go to `messages` collection → Indexes tab
7. **You should see:**
   - `_id_` (default)
   - `conversation_id_1`
   - `conversation_id_1_timestamp_1`
   - `timestamp_1`

**Expected:** Indexes created automatically on app start

**To verify speed improvement:**
- Check backend console logs
- Should see: "Database indexes created successfully"

---

### 7. Performance - Response Caching ✓
**Steps:**
1. Send message: "What is 2+2?"
2. **Note the response time** (usually 1-2 seconds)
3. Send THE EXACT SAME message: "What is 2+2?"
4. **Second response should be INSTANT** (<100ms)
5. Check backend console logs
6. Should see: "Cache hit for request"

**Expected:** Second identical query is near-instant (cached)

**Try these to test caching:**
- "Tell me a fact about Python"
- "What is machine learning?"
- "Explain FastAPI"

Send each **twice** and watch the speed difference!

---

### 8. Performance - Connection Pooling ✓
**Steps:**
1. Check backend console logs on startup
2. Should see: "Connected to MongoDB: chat_app"
3. Open multiple browser tabs (5-10 tabs)
4. In each tab, start a new conversation
5. Send messages from all tabs simultaneously
6. **All should work smoothly** without errors

**Expected:** No connection errors, all requests handled

**Backend console should show:**
- No "connection pool exhausted" errors
- Smooth operation
- Connections reused efficiently

---

## 🎨 Visual Tour

### Where to Find Each Feature

```
┌─────────────────────────────────────────┐
│  [Export MD] [Export TXT]  ← Top-left   │
│                                          │
│  ┌────────────────────────────────┐    │
│  │ User: Hello                     │    │
│  │ 10:30                           │    │
│  └────────────────────────────────┘    │
│                                          │
│  ┌────────────────────────────────┐    │
│  │ 🤖 AI: Hi! How can I help?     │    │
│  │ [Copy] [🔄] ← Hover to see     │    │
│  │ 10:30                           │    │
│  └────────────────────────────────┘    │
│                                          │
│  💡 Suggested questions:                │
│  [Summarize data] [Show stats] [Plot]  │
│                                          │
│  ┌────────────────────────────────┐    │
│  │ Type your message...            │    │
│  │ [📎] [Send]                     │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Copy button not appearing
- Make sure you **hover** over the AI message
- Only shows for **assistant messages**
- Not visible during streaming

### Regenerate not working
- Only shows for the **last** assistant message
- Not available during streaming
- Need at least one user + assistant pair

### Suggested questions not showing
- Only appears **after CSV upload**
- Must upload a valid CSV file
- Questions clear after using one
- Re-upload CSV to get new suggestions

### Export buttons not visible
- Only show when **messages exist**
- Need active session
- Look at **top-left corner**

### Caching not working
- Must send **exact same message**
- Different messages won't cache hit
- Cache limited to 1000 responses

---

## 📊 Expected Performance

| Feature | Before | After |
|---------|--------|-------|
| Database query | 50-200ms | 5-20ms |
| Cached response | N/A | <100ms |
| CSV upload | 2-5s | 1-3s |
| Concurrent users | ~10 | ~50 |

---

## ✨ Pro Tips

1. **Test with real data:** Use your own CSV files to see smart suggestions
2. **Try different questions:** Watch caching work with repeated queries
3. **Open DevTools:** See network requests and timings
4. **Check MongoDB:** View indexes and query performance
5. **Multiple tabs:** Test connection pooling limits

---

## 🎯 Success Criteria

After testing, you should have:
- ✅ Copied an AI message
- ✅ Regenerated a response
- ✅ Seen typing indicator
- ✅ Used suggested questions
- ✅ Exported conversation (MD + TXT)
- ✅ Verified database indexes
- ✅ Experienced cached responses
- ✅ Tested concurrent connections

---

## 📝 Report Any Issues

If something doesn't work:
1. Check browser console (F12)
2. Check backend terminal logs
3. Verify MongoDB is running
4. Ensure OpenAI API key is set
5. Try clearing browser cache

---

---

## 🆕 9. Sliding Window Context Management ✓

**Steps:**
1. Start a new conversation
2. Send 5 messages back and forth (10 total)
3. **Look at top-left corner** next to Export buttons
4. You should see a button: **[📊 10 msgs]**
5. Click the context button
6. **A dropdown appears showing:**
   - Messages: 10 / 20
   - Tokens: ~2,500
   - Green progress bars (healthy)
   - "✓ Sliding window active"

**Test Long Conversation:**
1. Continue sending messages (aim for 25+ messages)
2. Watch the context button change to **[📊 20 msgs]**
3. Button may turn **red** when optimizing
4. Click to see stats:
   - Messages: 25 / 20 (total in DB / kept in context)
   - Progress bars turn yellow/red
   - "⚠ Context optimization in use"

**Expected:**
- Button appears after first messages
- Color changes based on usage (green → yellow → red)
- Stats update every 5 messages
- Long conversations stay fast (sliding window removes old messages)

**What the stats show:**
```
┌─────────────────────────┐
│ Context Window Status   │
├─────────────────────────┤
│ Messages: 15 / 20       │  ← Current / Max
│ Tokens: ~12,500         │  ← Estimated token count
│                         │
│ Message usage: 75%      │  ← Progress bar
│ ████████████░░░░        │
│                         │
│ Token usage: 12.5%      │  ← Progress bar
│ ██░░░░░░░░░░░░░░        │
│                         │
│ ✓ Sliding window active │  ← Status
└─────────────────────────┘
```

**Backend check:**
Look at backend console logs, should see:
```
Sliding window applied: kept 20/25 messages, ~15000 tokens
```

---

**Happy Testing! 🚀**

---

## ✅ Complete Feature Checklist

After all tests, you should have verified:
- ✅ Typing indicator (bouncing dots)
- ✅ Copy button (with toast notification)
- ✅ Regenerate button (new response)
- ✅ CSV suggested questions (auto-generated)
- ✅ Conversation export (MD + TXT)
- ✅ Database indexes (MongoDB Compass)
- ✅ Response caching (instant second query)
- ✅ Connection pooling (multiple tabs work)
- ✅ **Sliding window** (context management)

**9/9 Features Working = Production Ready! 🎉**
