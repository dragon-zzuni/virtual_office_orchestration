# Project Structure

## offline_agent

```
offline_agent/
├── main.py                    # Core engine (993 lines) - SmartAssistant class
├── run_gui.py                 # GUI entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment configuration
│
├── config/                    # Global settings
├── data/
│   └── multi_project_8week_ko/  # Current dataset (8-week, 4-person team)
│       ├── chat_communications.json
│       ├── email_communications.json
│       ├── team_personas.json
│       └── todos_cache.db     # SQLite TODO storage
│
├── src/                       # Source modules (organized by function)
│   ├── nlp/                   # NLP processing
│   │   ├── summarize.py       # Message summarization
│   │   ├── priority_ranker.py # Priority analysis
│   │   ├── action_extractor.py # Action extraction
│   │   ├── message_grouping.py # Time-based grouping
│   │   └── grouped_summary.py  # Group summary models
│   │
│   ├── ui/                    # PyQt6 GUI components
│   │   ├── main_window.py     # Main window (2,382 lines)
│   │   ├── todo_panel.py      # TODO management
│   │   ├── email_panel.py     # Email filtering
│   │   ├── analysis_result_panel.py  # Analysis display
│   │   ├── time_range_selector.py    # Time filtering
│   │   ├── message_summary_panel.py  # Message grouping UI
│   │   ├── message_detail_dialog.py  # Detail view
│   │   └── styles.py          # Tailwind-inspired design system
│   │
│   ├── utils/                 # Utilities
│   │   └── datetime_utils.py  # Date/time helpers
│   │
│   └── config/                # Configuration modules
│
├── docs/                      # Documentation
│   ├── UI_STYLES.md
│   ├── EMAIL_PANEL.md
│   ├── MESSAGE_SUMMARY_PANEL.md
│   ├── TIME_RANGE_SELECTOR.md
│   ├── DEVELOPMENT.md
│   └── DATASET_MIGRATION.md
│
├── test/                      # Test files
├── tools/                     # Utility scripts
└── .kiro/specs/ui-improvements/  # Kiro spec documents
    ├── requirements.md
    ├── design.md
    ├── tasks.md
    └── REFACTORING_NOTES.md   # Consolidated refactoring log
```

### Key Conventions (offline_agent)
- **Language**: Code in English, comments/docs in Korean
- **Imports**: Project root and `src/` added to sys.path
- **Logging**: Module-level loggers with `logging.getLogger(__name__)`
- **Data flow**: JSON → SmartAssistant → NLP modules → UI components
- **State**: SQLite for TODO persistence, in-memory for analysis results

## virtualoffice

```
virtualoffice/
├── src/virtualoffice/         # Main package
│   ├── __main__.py            # CLI entry point
│   ├── app.py                 # PySide6 GUI (1,197 lines)
│   │
│   ├── servers/               # FastAPI services
│   │   ├── email/
│   │   │   ├── app.py         # Email REST API
│   │   │   └── models.py      # Email data models
│   │   └── chat/
│   │       ├── app.py         # Chat REST API
│   │       └── models.py      # Chat data models
│   │
│   ├── sim_manager/           # Simulation engine
│   │   ├── app.py             # Simulation REST API
│   │   ├── engine.py          # Core engine (2,360+ lines)
│   │   ├── planner.py         # GPT/Stub planners
│   │   ├── gateways.py        # HTTP client adapters
│   │   └── schemas.py         # Request/response models
│   │
│   ├── virtualWorkers/        # AI persona system
│   │   └── worker.py          # Worker persona + markdown builder
│   │
│   ├── common/                # Shared utilities
│   │   └── db.py              # SQLite helpers
│   │
│   ├── utils/                 # Helper functions
│   │   ├── completion_util.py # OpenAI wrapper
│   │   └── pdf_to_md.py       # PDF processing
│   │
│   ├── resources/             # Static assets
│   └── vdos.db                # SQLite database
│
├── tests/                     # Comprehensive test suite
│   ├── conftest.py
│   └── test_*.py
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── GETTING_STARTED.md
│   ├── architecture.md
│   └── api/
│
├── simulation_output/         # Generated artifacts
├── agent_reports/             # AI analysis reports (timestamped)
├── scripts/                   # Utility scripts
│
├── mobile_chat_simulation.py  # Main simulation runner
├── quick_simulation.py        # Quick test simulation
├── pyproject.toml             # Briefcase config
└── requirements.txt           # Python dependencies
```

### Key Conventions (virtualoffice)
- **Language**: Code and docs in English
- **Architecture**: Microservices pattern (3 FastAPI apps)
- **Data flow**: REST APIs → Simulation Engine → Persona Workers → Communication Servers
- **State**: SQLite for simulation state, hierarchical summarization for token management
- **Outputs**: Timestamped directories in `simulation_output/` and `agent_reports/`
- **Testing**: Pytest with comprehensive coverage

## Shared Patterns

Both projects follow:
- **Module organization**: Separate folders for UI, business logic, utilities
- **Configuration**: `.env` files for secrets, code for defaults
- **Documentation**: Extensive markdown docs in `docs/` folder
- **Type safety**: Type hints on all public functions
- **Logging**: Structured logging with appropriate levels
- **Error handling**: Try-except with detailed logging
