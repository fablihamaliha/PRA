# RapidAPI Setup Guide - Get Real Amazon Data

## ✅ What You'll Get
- **Real Amazon product data**
- **FREE: 100-200 requests/month** (enough for testing)
- **No business required**
- **No credit card required**
- **Setup time: 3 minutes**

---

## Step-by-Step Setup

### Step 1: Create RapidAPI Account (1 minute)

1. Go to: https://rapidapi.com/
2. Click **"Sign Up"** (top right)
3. Sign up with:
   - Email + Password, OR
   - Google account, OR
   - GitHub account
4. Verify your email

### Step 2: Subscribe to Real-Time Amazon Data API (1 minute)

1. Go to: https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-amazon-data
2. Click **"Subscribe to Test"** button
3. Select the **"Basic"** plan:
   - **FREE**
   - **100 requests/month**
   - No credit card required
4. Click **"Subscribe"**

### Step 3: Get Your API Key (30 seconds)

After subscribing, you'll see the API dashboard:

1. Look for **"X-RapidAPI-Key"** in the code snippet
2. It looks like: `1234567890abcdef...`
3. Click the **Copy** button next to it

### Step 4: Add to Your .env File (30 seconds)

1. Open: `/Users/maliha/PycharmProjects/PRA/.env`
2. Find the line: `RAPIDAPI_KEY=`
3. Paste your key after the `=`:
   ```
   RAPIDAPI_KEY=1234567890abcdefghijklmnop
   ```
4. Save the file

### Step 5: Restart Your Flask App

```bash
# Stop your current server (Ctrl+C)
# Then restart:
cd /Users/maliha/PycharmProjects/PRA/pra
python app.py
```

---

## Test It Works

### Option 1: Use the Web Interface
1. Go to: http://localhost:5001/deals
2. Search for "laptop" or "headphones"
3. You should see real Amazon products!

### Option 2: Use curl
```bash
curl -X POST http://localhost:5001/deals/api/search \
  -H "Content-Type: application/json" \
  -d '{"product_name": "laptop", "use_location": false}'
```

You should see JSON with real Amazon product data!

---

## What You Get from RapidAPI

Each product will have:
- ✅ Product name
- ✅ Real price
- ✅ Product image
- ✅ Star rating
- ✅ Number of reviews
- ✅ Direct Amazon link (opens in new tab)
- ✅ Prime shipping info

---

## Troubleshooting

### "No deals found"
- Make sure you pasted the API key correctly (no extra spaces)
- Check that you subscribed to the "Real-Time Amazon Data" API
- Restart your Flask server after adding the key

### "Rate limit exceeded"
- Free tier: 100 requests/month
- Wait until next month, or upgrade to paid plan
- App has 30-minute caching to reduce API calls

### "Unauthorized" error
- Your API key might be wrong
- Go to https://rapidapi.com/developer/apps
- Find your default application
- Copy the API key again

---

## Upgrade Options (Optional)

If you need more requests:

| Plan | Requests/Month | Price |
|------|----------------|-------|
| **Basic** | 100 | **FREE** |
| Pro | 1,000 | $9.99/mo |
| Ultra | 10,000 | $49.99/mo |
| Mega | 100,000 | $199.99/mo |

**For testing/development, FREE tier is enough!**

---

## Next Steps

Once RapidAPI is working, you can add more data sources:

1. **eBay API** - https://developer.ebay.com/ (FREE: 5,000/day)
2. **Rainforest API** - https://www.rainforestapi.com/ (FREE: 1,000/month)
3. **Another RapidAPI** - Many other shopping APIs available

---

## Support

- RapidAPI Docs: https://docs.rapidapi.com/
- Real-Time Amazon Data API Docs: Click "Documentation" tab on API page
- Issues: Check your Flask server logs for error messages

---

**Ready?** Sign up at https://rapidapi.com/ and get your key in 3 minutes! 🚀
