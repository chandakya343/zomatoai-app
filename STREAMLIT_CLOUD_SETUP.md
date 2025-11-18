# Streamlit Cloud Deployment Guide

## Prerequisites
- GitHub account
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## Steps to Deploy

### 1. Push to GitHub
Your code is already on GitHub at: `https://github.com/chandakya343/zomatoai-app`

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with GitHub
3. Click "New app"
4. Fill in details:
   - **Repository:** `chandakya343/zomatoai-app`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click "Deploy"

### 3. Configure Secrets

After deployment starts:

1. Click on your app settings (⚙️ icon)
2. Go to "Secrets"
3. Add the following:

```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

4. Click "Save"

### 4. Wait for Deployment

- Initial deployment takes 2-5 minutes
- Your app will be available at: `https://zomatoai-app.streamlit.app` (or similar)

## Troubleshooting

### App shows "API key not found"
- Make sure you added `GEMINI_API_KEY` to Streamlit secrets
- Secret key must match exactly: `GEMINI_API_KEY`

### App crashes on startup
- Check the logs in Streamlit Cloud (bottom right corner)
- Verify all files are pushed to GitHub
- Check `requirements.txt` has all dependencies

### Memory/file errors
- The app has cloud-safe error handling for file I/O
- Memory will work in-session but won't persist between restarts

## Features Ready for Cloud

✅ API key works from Streamlit secrets  
✅ File I/O has error handling  
✅ API responses validated  
✅ All data files included in repo  
✅ Requirements.txt complete  

## Local vs Cloud

| Feature | Local | Cloud |
|---------|-------|-------|
| API Key | `.env` file | Streamlit secrets |
| Memory Storage | Saved to files | In-session only |
| Data Files | From repo | From repo |

## Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify secrets are configured
3. Ensure all files are in GitHub repo

