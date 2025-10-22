# Sliding Window Context Management Guide

## 🎯 Overview

The **Sliding Window** feature automatically manages conversation context to:
- Keep conversations within token limits (prevents API errors)
- Maintain performance with long conversations
- Preserve important early context
- Show real-time context usage to users

---

## 🔧 How It Works

### The Problem
- OpenAI models have token limits (e.g., 128k tokens for GPT-4)
- Long conversations can exceed these limits
- Sending all messages becomes slow and expensive

### The Solution: Sliding Window

```
Original Conversation (25 messages):
[1][2][3][4][5][6]...[20][21][22][23][24][25]

With Sliding Window (max 20, preserve first 2):
[1][2]...[16][17][18][19][20][21][22][23][24][25]
 ^  ^                                           ^
Keep  Skip middle          Keep most recent
first
```

### Strategy
1. **Always preserve first N messages** (default: 2) - important context
2. **Keep most recent messages** up to limit (default: 20 messages)
3. **Check token count** and reduce further if needed
4. **Remove from middle** when over token limit

---

## ⚙️ Configuration

### Settings (in `config.py`)

```python
# Enable/disable sliding window
sliding_window_enabled: bool = True

# Maximum messages to keep in context
sliding_window_max_messages: int = 20

# Always preserve first N messages
sliding_window_preserve_first: int = 2

# Soft token limit (for safety)
sliding_window_token_limit: int = 100000  # 100k tokens
```

### Environment Variables (.env)

```bash
# Override defaults in .env
SLIDING_WINDOW_ENABLED=true
SLIDING_WINDOW_MAX_MESSAGES=20
SLIDING_WINDOW_PRESERVE_FIRST=2
SLIDING_WINDOW_TOKEN_LIMIT=100000
```

---

## 📊 Token Estimation

The system estimates tokens using:
- **Text**: ~1.3 tokens per word
- **Images**: ~765 tokens each (for vision models)
- **CSV data**: Estimated from text content
- **Overhead**: ~4 tokens per message for structure

**Note:** These are estimates. Actual tokenization may vary slightly.

---

## 🎨 UI Indicator

### Context Button
Located in **top-left corner** next to export buttons:

```
[Export MD] [Export TXT] [📊 15 msgs]
                            ^
                    Context indicator
```

**Color coding:**
- **Green outline**: Within limits ✓
- **Red**: Optimization needed ⚠

### Stats Dropdown
Click the context button to see:

```
┌─────────────────────────┐
│ Context Window Status   │
├─────────────────────────┤
│ Messages: 15 / 20       │
│ Tokens: ~12,500         │
│                         │
│ Message usage: 75%      │
│ ████████████░░░░        │
│                         │
│ Token usage: 12.5%      │
│ ██░░░░░░░░░░░░░░        │
│                         │
│ ✓ Sliding window active │
│ Keeping within limits   │
└─────────────────────────┘
```

**Progress bars:**
- 🟢 Green (0-60%): Healthy
- 🟡 Yellow (60-80%): Getting full
- 🔴 Red (80-100%): Optimization active

---

## 🚀 API Endpoints

### Get Context Stats
```http
GET /api/v2/sessions/{session_id}/stats
```

**Response:**
```json
{
  "total_messages": 15,
  "total_tokens": 12500,
  "max_messages": 20,
  "max_tokens": 100000,
  "needs_optimization": false,
  "within_limits": true,
  "token_usage_percent": 12.5,
  "message_usage_percent": 75.0,
  "user_messages": 8,
  "assistant_messages": 7,
  "sliding_window_enabled": true
}
```

### Get Optimized Context
```http
GET /api/v2/sessions/{session_id}/context?max_messages=15&preserve_first=2
```

**Response:**
```json
{
  "session_id": "...",
  "strategy": "sliding_window",
  "total_messages": 25,
  "kept_messages": 15,
  "removed_messages": 10,
  "estimated_tokens": 11200,
  "window_applied": true,
  "preserved_count": 2,
  "messages": [...]
}
```

---

## 💻 Code Usage

### Backend: Apply Sliding Window

```python
from services.chat_service import ChatService

# Get messages with sliding window applied
messages = await ChatService.get_messages(
    conversation_id="abc123",
    apply_sliding_window=True
)

# Get detailed optimization info
result = await ChatService.get_optimized_context(
    conversation_id="abc123",
    max_messages=15,
    preserve_first=2
)

print(f"Kept {result['kept_messages']} of {result['total_messages']} messages")
print(f"Estimated tokens: {result['estimated_tokens']}")
```

### Backend: Check Context Status

```python
from services.chat_service import ChatService

# Get context summary
summary = await ChatService.get_context_summary("abc123")

if summary["needs_optimization"]:
    print("⚠ Context window optimization needed")
    print(f"Messages: {summary['total_messages']} / {summary['max_messages']}")
    print(f"Tokens: {summary['estimated_tokens']} / {summary['token_limit']}")
```

### Frontend: Display Context Stats

```typescript
import { apiService } from '@/lib/api'

// Fetch context stats
const stats = await apiService.getContextStats(sessionId)

// Check if within limits
if (!stats.within_limits) {
  console.warn('Context optimization active')
}

// Display usage
console.log(`Message usage: ${stats.message_usage_percent}%`)
console.log(`Token usage: ${stats.token_usage_percent}%`)
```

---

## 🧪 Testing the Feature

### Test 1: Normal Conversation (Within Limits)
1. Start a new conversation
2. Send 10 messages back and forth
3. Click **context indicator** (top-left)
4. **Expected:** Green progress bars, within limits

### Test 2: Long Conversation (Sliding Window Activated)
1. Send 30+ messages in a conversation
2. Check context indicator
3. **Expected:**
   - Shows 20/20 messages (or your max)
   - Window applied notification
   - Progress bars show high usage

### Test 3: Token Estimation
1. Upload a large CSV file
2. Ask multiple questions about it
3. Check context stats
4. **Expected:** Token count increases with CSV data

### Test 4: Context Optimization
1. Create conversation with 25+ messages
2. Backend logs should show:
   ```
   Sliding window applied: kept 20/25 messages, ~15000 tokens
   ```
3. Frontend shows: "⚠ Context optimization in use"

### Test 5: Preserved Messages
1. Start conversation with important context
2. Send 20+ more messages
3. Check via API: `/api/v2/sessions/{id}/context`
4. **Expected:** First 2 messages always preserved

---

## 📈 Performance Benefits

### Before Sliding Window
```
25 messages × 500 tokens = 12,500 tokens per request
40 messages × 500 tokens = 20,000 tokens per request
100 messages × 500 tokens = 50,000 tokens per request ❌ Slow!
```

### After Sliding Window
```
25 messages → 20 kept = 10,000 tokens per request ✓
40 messages → 20 kept = 10,000 tokens per request ✓
100 messages → 20 kept = 10,000 tokens per request ✓
```

**Benefits:**
- 🚀 **Consistent performance** regardless of conversation length
- 💰 **Lower costs** (fewer tokens sent to OpenAI)
- ⚡ **Faster responses** (less data to process)
- 🛡️ **No token limit errors** (stays within bounds)

---

## 🎯 Best Practices

### 1. **Configure for Your Model**
```python
# For GPT-4 (128k context)
sliding_window_token_limit = 100000  # Leave headroom

# For GPT-3.5 (16k context)
sliding_window_token_limit = 12000  # More conservative
```

### 2. **Preserve Important Context**
```python
# First 2 messages usually contain:
# - System instructions
# - Initial user request
# - Important context setup
sliding_window_preserve_first = 2
```

### 3. **Adjust Message Limit**
```python
# More messages = better context, but slower
sliding_window_max_messages = 20  # Good balance

# Fewer messages = faster, but may lose context
sliding_window_max_messages = 10  # For quick responses
```

### 4. **Monitor Context Usage**
- Check stats every 5 messages
- Show warning at 80% capacity
- Auto-optimize before hitting limits

---

## 🐛 Troubleshooting

### Issue: "Context optimization in use" warning
**Cause:** Conversation exceeded limits
**Solution:** Normal behavior - sliding window is working
**Action:** No action needed, system is optimizing automatically

### Issue: AI forgets early conversation
**Cause:** Too few messages kept
**Solution:** Increase `sliding_window_max_messages`
**Action:** Set to 25-30 for longer context

### Issue: Responses getting slow
**Cause:** Token limit too high
**Solution:** Reduce `sliding_window_token_limit`
**Action:** Lower to 50000 for faster responses

### Issue: Context button not appearing
**Cause:** No messages in conversation
**Solution:** Send at least one message
**Action:** Button appears after first exchange

---

## 📊 Real-World Example

### Scenario: Customer Support Chat

**User:** Long conversation with 50 back-and-forth messages

**Without Sliding Window:**
```
50 messages × 300 tokens = 15,000 tokens
Cost: $0.15 per request (GPT-4)
Latency: 3-5 seconds
```

**With Sliding Window (20 messages):**
```
20 messages × 300 tokens = 6,000 tokens (60% reduction)
Cost: $0.06 per request (60% cheaper)
Latency: 1-2 seconds (60% faster)
```

**Preserved:**
- First 2 messages: User's initial problem
- Last 18 messages: Recent conversation
- Still maintains context quality!

---

## 🔬 Advanced: Algorithm Details

### Sliding Window Algorithm

```python
def apply_sliding_window(messages, max_msgs=20, preserve=2):
    total = len(messages)

    if total <= max_msgs:
        return messages  # All fit, no optimization needed

    # Step 1: Preserve first N
    preserved = messages[:preserve]

    # Step 2: Take most recent (max_msgs - preserve)
    recent_count = max_msgs - preserve
    recent = messages[-recent_count:]

    # Step 3: Combine
    result = preserved + recent

    # Step 4: Check token limit
    tokens = estimate_tokens(result)

    # Step 5: Remove from middle if over token limit
    while tokens > TOKEN_LIMIT and len(result) > preserve + 2:
        middle_index = preserve + (len(result) - preserve) // 2
        removed = result.pop(middle_index)
        tokens -= estimate_tokens([removed])

    return result
```

### Example Execution

```
Input: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
Max messages: 8
Preserve first: 2

Step 1: preserved = [1, 2]
Step 2: recent_count = 8 - 2 = 6
Step 3: recent = [7, 8, 9, 10, 11, 12]
Step 4: result = [1, 2, 7, 8, 9, 10, 11, 12]
Step 5: Check tokens (if over limit, remove from middle)

Output: [1, 2, 7, 8, 9, 10, 11, 12]
Removed: [3, 4, 5, 6] (middle messages)
```

---

## 🎓 Key Takeaways

1. ✅ **Automatic** - No user intervention needed
2. ✅ **Smart** - Preserves important context
3. ✅ **Visual** - Real-time feedback to users
4. ✅ **Configurable** - Adjust to your needs
5. ✅ **Efficient** - Better performance and lower costs

---

## 📝 Files Modified

**Backend (3 new + 2 modified):**
- ✨ `services/context_window.py` - Core sliding window logic
- ✨ `config.py` - Configuration settings
- ✨ `services/chat_service.py` - Integration methods
- 📝 `routers/chat_v2.py` - Auto-apply to all chats
- 📝 `routers/sessions_v2.py` - Stats endpoints

**Frontend (2 modified):**
- 📝 `lib/api.ts` - Context stats interface
- 📝 `components/chat-window.tsx` - UI indicator

---

**The sliding window feature makes your chat app production-ready for long conversations! 🚀**
