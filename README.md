# 🤖 LeadGenius: CRUD Lead Management System

A powerful Streamlit application for generating, managing, and organizing business leads with full CRUD (Create, Read, Update, Delete) functionality.

## ✨ Features

### 🔍 **Lead Generation**
- **Google Maps Integration**: Find businesses using Google Places API
- **Web Scraping**: Automatically extract contact emails from business websites
- **Real-time Progress**: Live updates during lead generation
- **Bulk Generation**: Generate 5-100 leads at once

### 📋 **CRUD Operations**
- **Create**: Add new leads manually or via generation
- **Read**: View, search, and filter leads
- **Update**: Edit lead information and status
- **Delete**: Remove individual leads or clear all data

### 📊 **Lead Management**
- **Status Tracking**: New, Contacted, Qualified, Converted, Rejected
- **Search & Filter**: Find leads by name, phone, email, or status
- **Persistent Storage**: Leads saved to local JSON database
- **Export Functionality**: Download leads as CSV

### 🤖 **AI-Powered Outreach** ⚡ *4 P's FRAMEWORK*
- **"Alex" Persona**: AI agent with Business Development expertise and professional tone
- **4 P's Framework**: Personalized, Problem-Aware, Pithy, Persuasive messaging
- **Specific Personalization**: References concrete business details, not generic compliments
- **Problem-First Approach**: Leads with prospect's challenges, not your solutions
- **Mobile-Optimized**: Under 90 words, scannable on phones, 8th-grade reading level
- **Low-Friction CTAs**: Simple questions that make replying easy and worthwhile
- **Complete Email Package**: Subject line + body + LinkedIn message generation

### 📧 **Human-in-the-Loop Outreach**
- **Email Sending**: Direct email sending via SendGrid API
- **LinkedIn Integration**: Safe clipboard copying for LinkedIn messages
- **Message Review**: Edit AI-generated messages before sending
- **Email Tracking**: Track sent emails and activity logs
- **Manual Control**: Human approval for each message sent
- **Status Management**: Automatic lead status updates after sending

### 📈 **Analytics Dashboard**
- **Lead Statistics**: Total leads, conversion rates, daily counts
- **Status Distribution**: Visual charts of lead statuses
- **Recent Activity**: View recently added leads

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd lead-genius

# Install dependencies
pip install -r requirements.txt
```

### 2. API Key Setup

#### Google Maps API (Required for lead generation)
1. Get a Google Maps API Key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Places API** and **Maps JavaScript API**

#### Google Gemini AI API (Required for AI outreach)
1. Get a Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. This enables AI-powered personalized outreach generation

#### SendGrid API (Required for email sending)
1. Get a SendGrid API Key from [SendGrid Dashboard](https://app.sendgrid.com/settings/api_keys)
2. This enables direct email sending from the Human-in-the-Loop interface

#### Configure your keys in `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your_google_maps_api_key_here"
GEMINI_API_KEY = "your_gemini_api_key_here"
SENDGRID_API_KEY = "your_sendgrid_api_key_here"
```

### 3. Run the Application
```bash
python -m streamlit run app.py
```

### 4. Access the App
Open your browser and go to: `http://localhost:8501`

## 📖 Usage Guide

### 🔍 **Generate Leads Tab**
1. Enter a **business type** (e.g., "restaurants", "plumbers", "law firms")
2. Enter a **location** (e.g., "San Francisco, CA")
3. Set **max results** (5-100)
4. Click **"✨ Generate Leads"**
5. Watch real-time progress as leads are found and processed

### 📋 **Manage Leads Tab**
- **View All Leads**: Browse your lead database
- **Search**: Use the search box to find specific leads
- **Filter**: Filter by lead status (New, Contacted, etc.)
- **Edit**: Click "✏️ Edit" to modify lead information
- **Delete**: Click "🗑️ Delete" to remove a lead
- **Export**: Download all leads as CSV

### ➕ **Add New Leads**
1. Click **"➕ Add Lead"** in the sidebar
2. Fill in the lead information form
3. Set the lead status
4. Click **"💾 Save Lead"**

### ✏️ **Edit Existing Leads**
1. In the Manage Leads tab, find the lead you want to edit
2. Click **"✏️ Edit"** button
3. Modify the information in the form
4. Click **"💾 Save Lead"** to update

### 🤖 **AI Outreach Tab** ⚡ *Enhanced*
1. Configure your **Gemini AI API key** (or use secrets)
2. **Select leads** for outreach generation (individual or bulk)
3. Click **"🚀 Generate AI Outreach"**
4. **Review analytics**: Success rate, confidence scores, personalization strategies
5. **Browse optimized messages** with quality indicators and strategy insights
6. **Copy high-quality content** for email and LinkedIn outreach
7. **Export messages** with full analytics data

## 🧠 AI "4 P's" Framework Features

### 🎯 **P1: PERSONALIZED**
- **Specific References**: Must mention concrete business details (e.g., "your real estate law work in Denver")
- **Research Proof**: Shows genuine interest, not bulk spam
- **Anti-Generic**: Avoids vague compliments like "impressive company"

### 🔍 **P2: PROBLEM-AWARE**
- **Challenge First**: Leads with prospect's likely problems, not your solutions
- **Industry Empathy**: Acknowledges common challenges for their specific business type
- **Resonance Strategy**: Makes prospects think "Yes, that's exactly right"

### 📱 **P3: PITHY (Digestible)**
- **Mobile-First**: Easily scannable on phones with short sentences
- **Under 90 Words**: Brief messages that respect busy schedules
- **Clear Communication**: 8th-grade reading level, no jargon

### 🎪 **P4: PERSUASIVE (Not Pushy)**
- **Benefit-Oriented**: Focus on outcomes for them, not your process
- **Low-Friction CTAs**: Simple questions that make replying easy
- **Conversation Starters**: Building relationships, not closing deals immediately

### 🎭 **"Alex" AI Persona**
- **Professional Identity**: Business Development Specialist at "GrowthBoost"
- **Expert Tone**: Helpful industry expert, never pushy salesperson
- **Authentic Voice**: Confident, clear, genuinely curious about prospects

### 📧 **Human-in-the-Loop Tab**
1. Configure your **SendGrid API key** (or use secrets)
2. Set your **from email address** for outbound emails
3. **Review draft messages** generated by AI for each lead
4. **Edit messages** before sending if needed
5. **Send Email**: Click to send via SendGrid API (safe and robust)
6. **Copy LinkedIn**: Copy LinkedIn message to clipboard for manual pasting
7. **Reject**: Mark leads as rejected if not suitable
8. **Preview**: View formatted HTML email before sending
9. **Track progress**: Monitor sent vs. pending emails

### 📊 **Analytics Tab**
- View lead statistics and metrics
- See status distribution charts
- Track recent lead activity
- Monitor conversion rates

## 📁 File Structure

```
📦 LeadGenius/
├── 📄 app.py                    # Main Streamlit application
├── 📄 lead_generator.py         # Backend lead generation logic
├── 📄 ai_outreach.py           # AI-powered outreach generation
├── 📄 email_sender.py          # Email sending via SendGrid API
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # This documentation
├── 📄 .gitignore               # Git ignore rules
├── 📄 leads_database.json      # Local lead database (auto-generated)
├── 📄 outreach_messages_*.json # AI-generated outreach messages
├── 📄 email_log.json           # Email activity log (auto-generated)
└── 📁 .streamlit/
    └── 📄 secrets.toml         # API key configuration
```

## 🔧 Configuration

### API Key Management
- **Production**: Use Streamlit secrets (`st.secrets["GOOGLE_API_KEY"]`)
- **Development**: Manual input fallback
- **Security**: API key stored securely and excluded from version control

### Data Storage
- **Local Database**: `leads_database.json` (automatically created)
- **Persistent**: Leads survive app restarts
- **Backup**: Export to CSV for backup/sharing

## 🛡️ Security Features

- **API Key Protection**: Secrets file excluded from Git
- **Input Validation**: Form validation and error handling
- **Rate Limiting**: Responsible web scraping with delays
- **Error Handling**: Graceful handling of API failures

## 📊 Lead Status Workflow

```
New → Contacted → Qualified → Converted
  ↓
Rejected
```

- **New**: Freshly generated or added leads
- **Contacted**: Leads that have been reached out to
- **Qualified**: Leads that show potential
- **Converted**: Successful conversions
- **Rejected**: Leads that didn't work out

## 🔄 Data Flow

1. **Generate**: Google Maps API → Business Data → Web Scraping → Contact Info
2. **Store**: Leads saved to JSON database with unique IDs and timestamps
3. **Manage**: CRUD operations update database in real-time
4. **Analyze**: Dashboard provides insights from stored data

## 🐛 Troubleshooting

### Common Issues

**Streamlit Command Not Found:**
```bash
python -m streamlit run app.py
```

**API Key Issues:**
- Ensure your Google Maps API key is valid
- Enable Places API in Google Cloud Console
- Check API key permissions and quotas

**Web Scraping Errors:**
- Some websites block scraping (403 errors)
- Email formats may not be detected
- Rate limiting prevents being blocked

### Error Messages
- **"No API key found"**: Add your Google Maps API key to secrets.toml
- **"403 Forbidden"**: Website blocks scraping (normal behavior)
- **"No connection adapters"**: Invalid URL format (handled gracefully)

## 🚀 Deployment

### Streamlit Cloud
1. Upload code to GitHub
2. Connect to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy!

### Local Production
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Made with ❤️ using Streamlit, Google Maps API, Google Gemini AI, and Beautiful Soup** 