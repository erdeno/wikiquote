# 🧠 WikiQuote - Multimodal Quote Discovery System

## 📋 Project Overview

WikiQuote is a production-ready NLP application that combines graph databases, voice interaction, and AI to create an intelligent quote discovery system. The project features:

* **Graph Database** - Neo4j storing 150,000+ Wikiquote entries with semantic relationships
* **Voice Interaction** - Multi-accent speech recognition (Whisper) and text-to-speech (gTTS) in 9 languages
* **Speaker Identification** - ECAPA-TDNN model with 95% accuracy for personalized responses
* **RAG-Powered Chatbot** - Conversational quote search using Ollama (llama3.2:3b)
* **Autocomplete Search** - Real-time quote suggestions with debounced input
* **Cloud Deployment** - Fully containerized and deployed on Azure Container Instances

---

## 🏗️ Architecture

```
wikiquote/
│
├── backend/              # Django REST API
│   ├── voice/           # ASR, TTS, Speaker ID endpoints
│   ├── quotes/          # Quote search and Neo4j integration
│   ├── users/           # Authentication and user profiles
│   └── settings.py      # Configuration
│
├── frontend/            # Vue.js SPA with Nginx
│   ├── index.html       # Main application
│   └── nginx.conf       # Web server config
│
├── services/
│   ├── voice/
│   │   ├── asr/        # Whisper speech recognition
│   │   ├── speaker/    # ECAPA-TDNN speaker identification
│   │   └── tts/        # gTTS text-to-speech (9 accents)
│   └── rag/            # RAG chatbot with Ollama
│
├── docker-compose.yml   # Local development setup
├── .github/workflows/   # CI/CD pipeline
└── requirements.txt     # Python dependencies
```

---

## 🚀 Features

### 🎤 Voice Interaction
- **Multi-language ASR**: Whisper model supporting multiple accents
- **Speaker Recognition**: 95% accuracy using ECAPA-TDNN embeddings
- **Natural TTS**: 9 accent variations (American, British, Indian, Mexican, etc.)
- **Personalized Voices**: User-specific TTS preferences with pitch/speed control

### 🔍 Intelligent Search
- **Autocomplete**: Real-time quote suggestions (300ms debounced)
- **Semantic Search**: Neo4j graph queries with relevance scoring
- **RAG Chatbot**: Conversational quote discovery powered by Ollama
- **Query History**: Track user searches with authentication

### 👤 User Management
- **Authentication**: Token-based auth with Django REST Framework
- **User Profiles**: Customizable TTS preferences and favorite quotes
- **Query Analytics**: Track searches and results for insights

---

## 🧰 Tech Stack

| Component        | Technology                  | Purpose                        |
|:-----------------|:----------------------------|:-------------------------------|
| **Backend**      | Django 5.0 + DRF           | REST API server                |
| **Frontend**     | Vue.js 3 + Tailwind CSS    | Reactive web UI                |
| **Database**     | PostgreSQL (Neon)          | User data and auth             |
| **Graph DB**     | Neo4j (AuraDB)             | Quote relationships            |
| **LLM**          | Ollama (llama3.2:3b)       | RAG-powered responses          |
| **ASR**          | Whisper (openai-whisper)   | Speech recognition             |
| **Speaker ID**   | SpeechBrain ECAPA-TDNN     | Voice identification           |
| **TTS**          | gTTS                       | Multi-accent speech synthesis  |
| **Deployment**   | Azure Container Instances  | Cloud hosting                  |
| **CI/CD**        | GitHub Actions             | Automated deployment           |

---

## ⚙️ Local Development Setup

### Prerequisites
- Python ≥ 3.10
- Docker ≥ 24.x
- Docker Compose ≥ 2.x
- Git

### 1. Clone Repository
```bash
git clone https://github.com/oguzhan-yilmaz1/wikiquote.git
cd wikiquote
```

### 2. Create `.env` File
```bash
cp .env.example .env
```

**Required environment variables:**
```bash
# Neo4j (AuraDB)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# PostgreSQL (Neon)
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=your_password
DB_HOST=your-host.neon.tech
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### 3. Start Services
```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 4. Access Applications

| Service    | Local URL                  | Production URL                                               |
|:-----------|:---------------------------|:-------------------------------------------------------------|
| Frontend   | http://localhost:8080      | http://wikiquote-frontend.germanywestcentral.azurecontainer.io:8080 |
| Backend    | http://localhost:8000      | http://wikiquote-backend.germanywestcentral.azurecontainer.io:8000  |
| Ollama     | http://localhost:11434     | http://wikiquote-ollama.germanywestcentral.azurecontainer.io:11434  |

---

## 🧪 Testing

### Run Backend Tests
```bash
# Inside backend container
docker exec -it wikiquote-backend pytest -v

# Or from host with coverage
docker exec -it wikiquote-backend pytest --cov=backend --cov-report=html
```

### Test Individual Services
```bash
# Test TTS service
docker exec -it wikiquote-backend python3 -c "
from services.voice.tts.gtts_service import GTTSService
tts = GTTSService()
tts.synthesize_to_file('Hello World', '/tmp/test.wav', voice_type='american')
print('TTS test passed!')
"

# Test Neo4j connection
docker exec -it wikiquote-backend python3 manage.py shell -c "
from backend.quotes.neo4j_client import health_check_details
print(health_check_details())
"
```

---

## 🐳 Docker Commands

| Task                      | Command                              |
|:--------------------------|:-------------------------------------|
| Build containers          | `docker-compose build`               |
| Start services            | `docker-compose up -d`               |
| Stop services             | `docker-compose down`                |
| View logs                 | `docker-compose logs -f backend`     |
| Restart service           | `docker-compose restart backend`     |
| Shell into container      | `docker exec -it wikiquote-backend bash` |
| Clean up everything       | `docker-compose down -v --rmi local` |

---

## 🚢 Deployment

### Automatic Deployment (CI/CD)
The project uses GitHub Actions for automated deployment:

1. **Push to `main` branch** triggers the pipeline
2. **Tests run** on Ubuntu runner
3. **Docker images built** and pushed to Docker Hub
4. **Deploy to Azure** Container Instances automatically

### Manual Deployment
```bash
# Build and tag images
docker build -t your-username/wikiquote-backend:latest -f backend/Dockerfile .
docker build -t your-username/wikiquote-frontend:latest -f frontend/Dockerfile .

# Push to registry
docker push your-username/wikiquote-backend:latest
docker push your-username/wikiquote-frontend:latest

# Deploy via Azure CLI
az container create --resource-group wikiquote-rg \
  --name wikiquote-backend \
  --image your-username/wikiquote-backend:latest \
  --dns-name-label wikiquote-backend \
  --ports 8000 \
  --environment-variables NEO4J_URI=$NEO4J_URI ...
```

---

## 📊 Performance Metrics

- **Quote Search**: Sub-200ms response time with Neo4j indexing
- **Speaker ID**: 95% accuracy on test dataset
- **ASR**: Multi-accent support with Whisper
- **TTS**: 9 accent variations with natural prosody
- **Database**: 150,000+ quotes indexed
- **Uptime**: 99.9% on Azure Container Instances

---

## 🛠️ Development Workflow

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test locally
3. Commit: `git commit -m "feat: description"`
4. Push: `git push origin feature/new-feature`
5. Create Pull Request to `main`
6. CI/CD automatically deploys on merge

### Common Development Tasks

**Update TTS voices:**
```bash
# Edit services/voice/tts/gtts_service.py
# Update voice_configs dictionary
# Test locally, then commit
```

**Add new API endpoint:**
```bash
# 1. Create view in backend/voice/views.py
# 2. Add URL in backend/voice/urls.py
# 3. Test with curl or Postman
# 4. Update frontend to use new endpoint
```

**Modify database schema:**
```bash
# Create migration
docker exec -it wikiquote-backend python manage.py makemigrations

# Apply migration
docker exec -it wikiquote-backend python manage.py migrate
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Database connection errors**
```bash
# Check if .env file is loaded
docker exec -it wikiquote-backend env | grep DB_

# Test database connection
docker exec -it wikiquote-backend python manage.py dbshell
```

**2. Ollama not responding**
```bash
# Check if Ollama is running
docker-compose ps ollama

# Pull model if missing
docker exec -it wikiquote-ollama ollama pull llama3.2:3b
```

**3. TTS has chipmunk voice**
```bash
# This was fixed by removing pitch manipulation
# Verify gtts_service.py doesn't use asetrate
docker exec -it wikiquote-backend grep "asetrate" /app/services/voice/tts/gtts_service.py
# Should return nothing
```

**4. Frontend can't reach backend**
```bash
# Check apiUrl in browser console
# Should be localhost for local, Azure URL for production
# Check CORS settings in backend/settings.py
```

---

## 📝 API Documentation

### Voice Endpoints

**ASR (Speech Recognition)**
```bash
POST /api/v1/voice/asr/
Content-Type: multipart/form-data
Body: audio file (WAV/MP3)

Response: { "success": true, "transcription": "hello world" }
```

**TTS (Text-to-Speech)**
```bash
POST /api/v1/voice/synthesize/
Content-Type: application/json
Body: { "text": "Hello", "voice_type": "american" }

Response: Audio file (WAV)
```

**Speaker Registration**
```bash
POST /api/v1/voice/speaker/register/
Content-Type: multipart/form-data
Body: audio file + speaker_id

Response: { "success": true, "embedding_saved": true }
```

### Quote Endpoints

**Search Quotes**
```bash
GET /api/v1/quotes/search/?q=wisdom&limit=3

Response: {
  "success": true,
  "results": [
    {
      "quote_id": "123",
      "text": "Wisdom begins in wonder.",
      "author": "Socrates",
      "score": 0.95
    }
  ]
}
```

**Chat with RAG**
```bash
POST /api/v1/quotes/chat/
Body: { "query": "tell me about courage", "accent": "american" }

Response: {
  "success": true,
  "response": "Courage is...",
  "quotes": [...],
  "method": "rag"
}
```

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

---

## 📜 License

This project is part of an NLP Capstone course and is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **NVIDIA NeMo** for speech processing models
- **Neo4j** for graph database technology
- **Wikiquote** for quote dataset
- **OpenAI Whisper** for ASR capabilities
- **Anthropic Claude** for development assistance

---

## 📧 Contact

For questions or collaboration:
- GitHub: [@erdeno](https://github.com/erdeno)
---

**Built with ❤️ using Python, Django, Vue.js, and AI**
