# 🚀 Streamlit Cloud Deployment Guide

## Essential Files for Deployment

To deploy the **Enterprise AI Data Analysis Platform** to Streamlit Cloud, you need these files:

### 📁 **Required Files (Minimum)**

```
├── streamlit_app_enterprise.py          # Main application file
├── requirements.txt                      # Dependencies
└── src/
    └── python/
        ├── integration/
        │   ├── __init__.py
        │   └── enterprise_integration.py # Core integration logic
        └── agents/                       # Agent modules (if used)
            ├── __init__.py
            └── (agent files)
```

### 📋 **Complete File List for Full Functionality**

1. **Main Application**
   - `streamlit_app_enterprise.py` ⭐ (REQUIRED)

2. **Core Integration**
   - `src/python/integration/__init__.py` ⭐ (REQUIRED)
   - `src/python/integration/enterprise_integration.py` ⭐ (REQUIRED)

3. **Dependencies**
   - `requirements.txt` or `requirements_enterprise.txt` ⭐ (REQUIRED)

4. **Optional but Recommended**
   - `src/python/agents/` (folder with agent modules)
   - `src/python/auth/` (authentication modules)
   - `src/python/workflow/` (workflow management)
   - `src/python/execution/` (task execution)
   - `src/python/reporting/` (report generation)
   - `src/python/marimo_integration/` (notebook generation)

5. **Documentation** (Optional)
   - `README.md`
   - `ENTERPRISE_PLATFORM_SUMMARY.md`

## 🔧 **Deployment Steps**

### Option 1: Deploy Directly from GitHub

1. **Push files to GitHub repository**
   ```bash
   git add streamlit_app_enterprise.py src/ requirements.txt
   git commit -m "Add enterprise app for Streamlit deployment"
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"

3. **Configure Deployment**
   - Repository: `your-username/your-repo`
   - Branch: `main` or `feat/automated-platform-no-auth`
   - Main file path: `streamlit_app_enterprise.py`

4. **Add Secrets** (Optional)
   - Click "Advanced settings"
   - Add secrets in TOML format:
   ```toml
   GEMINI_API_KEY = "your-api-key-here"
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment

### Option 2: Deploy Minimal Version

If you want the **simplest deployment**, use only these files:

1. **Create a new folder** with just:
   ```
   ├── streamlit_app_enterprise.py
   ├── requirements_minimal.txt
   └── src/
       └── python/
           └── integration/
               ├── __init__.py
               └── enterprise_integration.py
   ```

2. **Create minimal requirements.txt**:
   ```txt
   streamlit>=1.28.0
   pandas>=1.5.0
   numpy>=1.23.0
   plotly>=5.10.0
   scikit-learn>=1.1.0
   ```

3. **Deploy to Streamlit Cloud**

## 📝 **Important Notes**

### File Structure on Streamlit Cloud
Streamlit Cloud will recognize this structure:
```
repo-root/
├── streamlit_app_enterprise.py     # Entry point
├── requirements.txt                 # Auto-installed
└── src/python/                     # Import path works
    └── integration/
        └── enterprise_integration.py
```

### Import Paths
The app uses:
```python
sys.path.append(str(Path(__file__).parent / "src" / "python"))
```
This ensures imports work correctly on Streamlit Cloud.

### Fallback Implementations
The app includes fallback implementations, so it will work even if some modules are missing:
- ✅ Authentication works with fallback
- ✅ Workflow management works with fallback
- ✅ Task execution works with fallback
- ✅ Report generation works with fallback

## 🎯 **Quick Deployment Command**

If you're in the repository root:

```bash
# Option 1: Deploy full enterprise app
streamlit run streamlit_app_enterprise.py

# Option 2: Deploy from Streamlit Cloud
# Just push to GitHub and connect via share.streamlit.io
```

## 🔑 **Demo Accounts**

Once deployed, use these accounts to test:
- **Manager**: `manager@company.com` / `manager123`
- **Analyst**: `analyst@company.com` / `analyst123`
- **Associate**: `associate@company.com` / `associate123`

## ⚠️ **Troubleshooting**

### If imports fail:
- Ensure `src/python/integration/` folder is included
- Check that `__init__.py` files exist in each folder

### If app crashes:
- Use `requirements_enterprise.txt` (minimal dependencies)
- Remove optional dependencies like `marimo` and `playwright`

### If authentication doesn't work:
- The fallback authentication is built-in and will work automatically

## 🎉 **Success Indicators**

When successfully deployed, you should see:
1. Login page with demo account information
2. After login, role-based dashboard
3. Manager can create plans
4. Plans auto-generate tasks
5. All core features working

---

**Summary**: The minimum files needed are:
1. `streamlit_app_enterprise.py`
2. `requirements.txt` 
3. `src/python/integration/enterprise_integration.py`
4. `src/python/integration/__init__.py`

These 4 files will give you a fully functional enterprise app on Streamlit Cloud!