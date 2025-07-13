# 🚂 Railway Deployment Guide

## 📋 Pre-Deployment Checklist

1. **Upload your dashboard data file** to Railway
2. **Set environment variables** for user authentication
3. **Connect your GitHub repository**
4. **Deploy and test**

## 🔐 Authentication Setup

Your dashboard supports **2 users** with these default credentials:

### User 1 (Admin):
- **Username:** `admin`
- **Password:** `admin123`

### User 2 (Viewer):
- **Username:** `viewer` 
- **Password:** `viewer123`

**⚠️ IMPORTANT: Change these passwords in production!**

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Data File

```bash
# Copy your dashboard data to the root directory
cp data/dashboard_data.json ./dashboard_data.json
```

### Step 2: Push to GitHub

```bash
# Create new repository or push to existing
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 3: Deploy to Railway

1. **Go to:** [railway.app](https://railway.app)
2. **Login** with GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Select** your repository
5. **Railway auto-detects** Procfile and deploys

### Step 4: Set Environment Variables (Security)

In Railway dashboard → **Variables** tab:

#### Required Variables:
```
USER1_USERNAME=your_admin_username
USER1_PASSWORD_HASH=your_admin_password_hash
USER2_USERNAME=your_viewer_username  
USER2_PASSWORD_HASH=your_viewer_password_hash
ENVIRONMENT=production
```

#### Generate Password Hashes:
```python
import hashlib
password = "your_secure_password"
hash_value = hashlib.sha256(password.encode()).hexdigest()
print(hash_value)
```

### Step 5: Upload Data File

**Option A: Include in repository** (if private repo)
```bash
# Add dashboard_data.json to git
git add dashboard_data.json
git commit -m "Add dashboard data"
git push
```

**Option B: Upload via Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and upload
railway login
railway environment
railway shell
# Then upload file manually
```

### Step 6: Custom Domain (Optional)

1. **Railway Dashboard** → **Settings** → **Domains**
2. **Custom Domain** → `rbc.yourdomain.com`
3. **Add CNAME record** in your DNS:
   ```
   rbc.yourdomain.com → your-app.railway.app
   ```

## 🔒 Security Recommendations

### Production Security:
1. **Change default passwords** immediately
2. **Use strong passwords** (12+ characters)
3. **Set ENVIRONMENT=production**
4. **Use private GitHub repository**
5. **Consider IP whitelisting** if needed

### Environment Variables for Production:
```
USER1_USERNAME=admin_strong_username
USER1_PASSWORD_HASH=generated_hash_for_strong_password
USER2_USERNAME=viewer_username
USER2_PASSWORD_HASH=generated_hash_for_viewer_password
ENVIRONMENT=production
```

## 🔄 Data Updates

### Manual Update:
1. **Generate new** `dashboard_data.json` locally
2. **Upload** to Railway via GitHub or CLI
3. **Restart** deployment (if needed)

### Automated Update (Future):
- Set up **scheduled jobs** on Railway
- **Webhook integration** from local system
- **API endpoint** for data uploads

## 💰 Railway Pricing

- **Hobby Plan:** $5/month
- **Pro Plan:** $20/month (for multiple apps)
- **Custom domains** included
- **SSL certificates** automatic

## 🌐 Access URLs

After deployment:
- **Railway URL:** `https://your-app.railway.app`
- **Custom Domain:** `https://rbc.yourdomain.com`

## 🆘 Troubleshooting

### Common Issues:

**"No dashboard data file found"**
- Upload `dashboard_data.json` to project root
- Check file permissions

**"Invalid username or password"**
- Verify environment variables are set
- Check password hash generation

**"Application error"**
- Check Railway logs
- Verify requirements.txt dependencies

### Check Logs:
```bash
railway logs
```

## 📱 Mobile Access

Your dashboard will be **fully responsive** and accessible from:
- **Desktop browsers**
- **Mobile phones** 
- **Tablets**
- **Any device** with internet access

## 🎉 Final Result

After deployment, you'll have:
- **Secure authentication** (username/password)
- **Real-time portfolio dashboard**
- **Global accessibility** 
- **Professional URL** (with custom domain)
- **Mobile-friendly** interface

**Example Access:**
- Share `https://rbc.yourdomain.com` with trusted parties
- They login with credentials you provide
- Full portfolio visibility with live data

🚀 **Ready to deploy!**