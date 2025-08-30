# AI Data Analysis Team - Streamlit Deployment Guide

## 🚀 Quick Start

### Option 1: Run Locally (No Docker Required)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### Option 2: Deploy to Streamlit Cloud (100% FREE)

1. **Fork/Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit app"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Main file: `streamlit_app.py`
   - Click "Deploy"

3. **Add API Keys (Optional)**
   - In Streamlit Cloud dashboard
   - Go to App Settings → Secrets
   - Add: `GEMINI_API_KEY = "your-key-here"`

### Option 3: Deploy to Hugging Face Spaces (FREE)

1. Create account at [huggingface.co](https://huggingface.co)
2. Create new Space → Select Streamlit SDK
3. Push code to the Space
4. Auto-deploys at `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE`

## 🎯 Features

- **No Docker Required** - Pure Python, runs anywhere
- **Free Hosting** - Multiple free deployment options
- **Data Analysis** - Upload CSV, get instant insights
- **Visualizations** - Interactive charts with Plotly
- **ML Models** - Regression, clustering, classification
- **AI Insights** - Powered by Gemini (optional, with free tier)
- **Sample Data** - Built-in sample data for testing

## 💰 Cost Analysis

| Service | Cost | Limits |
|---------|------|--------|
| Streamlit Cloud | FREE | 1GB resources, public apps |
| Hugging Face Spaces | FREE | 2 vCPU, 16GB RAM |
| Render | FREE (with limits) | 750 hours/month |
| Local Development | FREE | Unlimited |
| Gemini API | FREE tier | 60 requests/minute |

## 🔑 Getting Gemini API Key (Optional)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Create API key
4. Add to Streamlit secrets or `.env` file

## 📱 Using the App

1. **Upload Data**: CSV files or use sample data
2. **Analyze**: Get summary statistics, quality reports
3. **Visualize**: Create interactive charts
4. **ML Models**: Train and evaluate models
5. **AI Insights**: Get intelligent analysis (requires Gemini key)

## 🛠️ Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run streamlit_app.py

# Run with environment variables
GEMINI_API_KEY=your-key streamlit run streamlit_app.py
```

## 📦 Project Structure

```
.
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # Local secrets (gitignored)
├── src/python/              # Core Python modules
│   ├── agents/              # AI agents
│   ├── llm/                 # LLM integration
│   └── marimo_integration/  # Notebook features
└── data/sample/             # Sample datasets
```

## 🔒 Security

- Never commit API keys to git
- Use Streamlit secrets for production
- API keys are optional - app works without them
- Free tier limits prevent cost overruns

## 🐛 Troubleshooting

**Import errors?**
```bash
pip install --upgrade -r requirements.txt
```

**Streamlit not found?**
```bash
pip install streamlit
```

**Memory issues on free tier?**
- Use smaller datasets (<10MB)
- Limit to 1000 rows for ML training
- Clear cache: Menu → Clear cache

## 🎉 Next Steps

1. **Customize UI**: Edit `streamlit_app.py`
2. **Add Features**: Extend agents in `src/python/agents/`
3. **Custom Models**: Add to ML agent
4. **Branding**: Update `.streamlit/config.toml`
5. **Scale Up**: Upgrade to paid tiers when needed

## 📝 License

MIT - Free to use and modify

## 🤝 Support

- Issues: Create GitHub issue
- Questions: Use GitHub Discussions
- Updates: Watch/Star the repository

---

**Made with ❤️ by Terragon Labs**