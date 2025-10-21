# Product Overview

This workspace contains two distinct Python projects focused on workplace communication analysis and simulation.

## offline_agent (Smart Assistant)

A desktop application that analyzes offline email and messenger data to generate actionable TODO lists for project managers. The system uses LLM-based analysis to extract priorities, summarize messages, and identify action items from team communications.

**Key Features:**
- Offline message analysis from JSON datasets (8-week multi-project data)
- LLM-powered message summarization and priority ranking
- PyQt6 GUI with TODO management, time-range filtering, and message grouping
- PM-focused filtering (only messages received by PM)
- Email threading and recipient type tracking (TO/CC/BCC)
- SQLite-based TODO persistence with 14-day auto-cleanup

**Target Users:** Project managers needing to triage large volumes of team communications

## virtualoffice (VDOS)

A headless-first simulation system that generates realistic workplace communication patterns (email + chat) for testing downstream tools without real company data. Features AI-powered persona generation and multi-project scenario support.

**Key Features:**
- FastAPI-based email and chat servers with REST APIs
- Simulation engine with tick-based time advancement
- AI persona system with GPT-4o integration for realistic behavior
- PySide6 GUI for simulation control and monitoring
- Hierarchical summarization to prevent token overflow
- Email threading and multi-project context switching

**Target Users:** Developers testing communication analysis tools, researchers studying workplace patterns
