# Technical Stack

## offline_agent

### Core Technologies
- **Python 3.10+** (Windows-optimized with UTF-8 encoding)
- **PyQt6** for desktop GUI
- **SQLite** for TODO persistence
- **OpenAI/Azure OpenAI/OpenRouter** for LLM analysis

### Key Libraries
- `fastapi==0.104.1` - API framework (minimal usage)
- `PyQt6==6.6.1` - GUI framework
- `openai==1.3.7` - LLM client
- `transformers==4.36.0` - Local NLP models
- `torch==2.5.1` - ML backend
- `requests==2.31.0` - HTTP client
- `python-dotenv==1.0.0` - Environment config

### Common Commands
```bash
# Run GUI
python run_gui.py
# or
run_gui.bat

# Install dependencies
pip install -r requirements.txt

# Run with specific log level
set LOG_LEVEL=DEBUG
python run_gui.py
```

### Environment Variables
- `OPENAI_API_KEY` / `AZURE_OPENAI_KEY` / `OPENROUTER_API_KEY`
- `LLM_PROVIDER` (openai | azure | openrouter)
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION`
- `LOG_LEVEL` (DEBUG | INFO | WARNING | ERROR)

## virtualoffice

### Core Technologies
- **Python 3.11+**
- **FastAPI** for REST APIs (3 separate services)
- **PySide6** for GUI dashboard
- **SQLite** for simulation state
- **OpenAI GPT-4o** for persona behavior

### Key Libraries
- `fastapi~=0.117` - REST API framework
- `uvicorn~=0.36` - ASGI server
- `PySide6-Essentials~=6.8` - GUI framework
- `httpx~=0.28` - Async HTTP client
- `openai` - LLM integration
- `briefcase` - App packaging
- `pytest` - Testing framework

### Service Architecture
- **Email Server**: Port 8000 (or 8025)
- **Chat Server**: Port 8001 (or 8035)
- **Simulation Manager**: Port 8015

### Common Commands
```bash
# Run GUI (recommended)
briefcase dev
# or
python -m virtualoffice

# Run services manually (3 terminals)
uvicorn virtualoffice.servers.email:app --port 8000 --reload
uvicorn virtualoffice.servers.chat:app --port 8001 --reload
uvicorn virtualoffice.sim_manager:create_app --port 8015 --reload

# Run complete simulation
python mobile_chat_simulation.py
python quick_simulation.py

# Run tests
pytest
pytest --cov=. --cov-report=html
```

### Environment Variables
- `VDOS_DB_URL` (default: `sqlite:///./vdos.db`)
- `VDOS_TICK_MS` (default: 50)
- `VDOS_BUSINESS_DAYS` (default: 5)
- `VDOS_WORKDAY_START` / `VDOS_WORKDAY_END`
- `VDOS_LOCALE_TZ` (default: `Asia/Seoul`)
- `OPENAI_API_KEY` for GPT-4o persona generation

## Shared Patterns

Both projects use:
- **Async/await** for I/O operations
- **Type hints** extensively (95%+ coverage)
- **Logging** with Python's standard library
- **Environment-based configuration** via `.env` files
- **SQLite** for local data persistence
