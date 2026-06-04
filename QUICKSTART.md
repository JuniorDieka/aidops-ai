# AidOps AI - Quick Start Guide

## 🎯 Two Ways to Run

### Option 1: Docker Compose (Recommended - Single Command)
**Best for:** Testing, demo, production deployment
**Terminals needed:** 1

### Option 2: Local Development (Multiple Terminals)
**Best for:** Active development, debugging
**Terminals needed:** 3 (Redis, Backend, Frontend)

---

## 🐳 Running with Docker (Easiest)

### Step 1: Choose Your Mode

#### **Demo Mode (No API Keys - Runs Immediately)**
```bash
cd "d:\Projects\AidOps AI"
docker-compose -f infra/docker-compose.yml up -d
```

That's it! Go to http://localhost:3000

#### **Production Mode (With OpenAI API Keys)**

1. **Get OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys
   - Sign in or create account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-...`)

2. **Configure Environment:**
```bash
cd "d:\Projects\AidOps AI\backend"
copy .env.example .env
```

3. **Edit `backend\.env` file and add your key:**
```bash
# Open backend\.env in notepad or any editor
notepad backend\.env

# Change these lines:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
EMBEDDING_PROVIDER=openai
```

4. **Start with Docker:**
```bash
cd "d:\Projects\AidOps AI"
docker-compose -f infra/docker-compose.yml up -d
```

### Step 2: Verify Services

```bash
# Check all containers are running
docker-compose -f infra/docker-compose.yml ps

# Should show:
# aidops-redis     - Up
# aidops-backend   - Up
# aidops-frontend  - Up
```

### Step 3: Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### Step 4: Load Sample Data

**Option A: Via Frontend**
1. Go to http://localhost:3000
2. Click "Upload" tab
3. Click "Load Sample Data"

**Option B: Via API**
```bash
curl -X POST http://localhost:8000/api/ingest-sample-data
```

### Step 5: Start Chatting!

Try these queries:
- "What are the Sphere minimum standards for water supply?"
- "How many people are displaced in the Northern Region?"
- "What is the budget for WASH activities?"
- "What are the GHF grant eligibility criteria?"

### Stopping Services

```bash
docker-compose -f infra/docker-compose.yml down
```

### View Logs

```bash
# All services
docker-compose -f infra/docker-compose.yml logs -f

# Specific service
docker-compose -f infra/docker-compose.yml logs -f backend
docker-compose -f infra/docker-compose.yml logs -f frontend
```

---

## 💻 Running Locally (For Development)

Only use this if you're actively developing and need hot-reload.

### Prerequisites
- Python 3.11+
- Node.js 20+
- Redis installed

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: Backend
```bash
cd "d:\Projects\AidOps AI\backend"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env if needed
uvicorn app.main:app --reload
```

### Terminal 3: Frontend
```bash
cd "d:\Projects\AidOps AI\frontend"
npm install
copy .env.example .env.local
npm run dev
```

---

## 🔑 Getting API Keys

### OpenAI (For Production Mode)

1. **Sign up:** https://platform.openai.com/signup
2. **Add payment method:** https://platform.openai.com/account/billing
3. **Create API key:** https://platform.openai.com/api-keys
4. **Copy key** (starts with `sk-...`)
5. **Add to `backend\.env`:**
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

**Pricing (as of 2024):**
- GPT-4o: $5/1M input tokens, $15/1M output tokens
- text-embedding-3-small: $0.02/1M tokens
- Whisper: $0.006/minute

### Pinecone (Optional - For Production Vector DB)

1. **Sign up:** https://www.pinecone.io/
2. **Create index:** Dashboard → Create Index
3. **Get API key:** Dashboard → API Keys
4. **Add to `backend\.env`:**
   ```
   VECTOR_DB_PROVIDER=pinecone
   PINECONE_API_KEY=your-key-here
   PINECONE_ENVIRONMENT=your-env
   PINECONE_INDEX_NAME=aidops-ai
   ```

### LangSmith (Optional - For Tracing)

1. **Sign up:** https://smith.langchain.com/
2. **Get API key:** Settings → API Keys
3. **Add to `backend\.env`:**
   ```
   ENABLE_TRACING=true
   LANGSMITH_API_KEY=your-key-here
   ```

---

## 🧪 Testing the System

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Load Sample Data
```bash
curl -X POST http://localhost:8000/api/ingest-sample-data
```

### 3. Test Chat (WebSocket)
Use the frontend at http://localhost:3000 or test with a WebSocket client.

### 4. Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### 5. Run Evaluation Harness
```bash
cd backend
python -m evals.run_evals
```

---

## ❓ Troubleshooting

### Docker Issues

**"Port already in use"**
```bash
# Check what's using the port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :6379

# Stop conflicting services or change ports in docker-compose.yml
```

**"Container won't start"**
```bash
# View logs
docker-compose -f infra/docker-compose.yml logs backend

# Rebuild containers
docker-compose -f infra/docker-compose.yml up -d --build
```

### Local Development Issues

**"Module not found"**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

**"Redis connection refused"**
- Make sure Redis is running: `redis-server`
- Check Redis is on port 6379: `redis-cli ping`

---

## 📊 What to Expect

### Demo Mode (No API Keys)
- ✅ Full UI works
- ✅ File upload and ingestion works
- ✅ Vector search works (FAISS)
- ✅ Chat works with mock responses
- ✅ Workflows execute with mock data
- ⚠️ LLM responses are simulated (not real AI)

### Production Mode (With OpenAI)
- ✅ Everything in demo mode
- ✅ Real GPT-4 responses
- ✅ Actual embeddings and semantic search
- ✅ Real transcription for audio files
- ✅ Intelligent agent reasoning

---

## 🎯 Next Steps

1. ✅ Start with Docker in demo mode
2. ✅ Load sample data
3. ✅ Test chat and workflows
4. ✅ Get OpenAI API key
5. ✅ Switch to production mode
6. ✅ Upload your own documents
7. ✅ Customize agents for your use case

---

**Need help?** Open an issue on GitHub or check the main README.md
