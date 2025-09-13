# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeFitter (代码钳工) is a command-line coding assistant designed for lightweight and precise code generation and manipulation. It's structured as a semi-automated coding tool with fine-grained control over LLM interactions.

## Architecture

### Core Structure
- **Main Entry Point**: `fitter/main.py` - Contains the primary application logic, interactive CLI interface, and command orchestration
- **Configuration**: `fitter/config.yaml` - YAML-based system prompts, model configuration, and tool definitions
- **Provider System**: `fitter/provider/` - Modular abstraction layer for different AI model providers

### Provider Pattern Architecture
The codebase implements a sophisticated provider abstraction pattern:

- **Base Interface**: `fitter/provider/base.py` - Abstract base class defining the LLM provider contract
- **Factory Pattern**: `fitter/provider/modules_factory.py` - Dynamic provider instantiation using `importlib`
- **Concrete Implementations**: Currently includes BigModel GLM-4.5 integration

### Key Dependencies
- `httpx>=0.28.1` - HTTP client for API communication
- `loguru>=0.7.3` - Advanced logging system
- `prompt-toolkit>=3.0.52` - Interactive command-line interface
- `pyyaml>=6.0.2` - Configuration file parsing
- `dotenv>=0.9.9` - Environment variable management
- `rich>=14.1.0` - Enhanced terminal output formatting

### Configuration System
The application uses YAML-based configuration that controls:
- Model selection and API settings
- System prompts for AI behavior
- Tool definitions for function calling
- Provider-specific configuration

## Development Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Run the main application
fitter
```

### Package Management
The project uses modern Python packaging with `pyproject.toml`:
- Build backend: `setuptools.build_meta`
- Entry point: `fitter = "fitter.main:main"`
- Python version: `~=3.12`

## Current Implementation Status

### Completed Features
- Provider abstraction layer with factory pattern
- BigModel GLM-4.5 integration with streaming responses
- Configuration-driven architecture
- Interactive command-line interface with `prompt-toolkit`
- Function calling framework
- Environment variable management via `.env`
- Logging system with user-facing output only

### Architecture Patterns
- **Provider Abstraction**: Enables easy swapping of different LLM providers
- **Configuration-Driven**: All behavior controlled through YAML configuration
- **Streaming Response**: Generator-based streaming for real-time LLM responses
- **Function Calling**: Built-in support for AI tool usage with configurable tool definitions

## Code Style and Conventions
- Follow Python PEP 8 conventions
- Use type hints where appropriate
- Modular design with clear separation of concerns
- Configuration-driven approach for AI prompts and behavior
- Logger initialization for user notifications only (no file logging)

## File Structure Conventions
- `fitter/main.py` - Application entry point and CLI interface
- `fitter/config.yaml` - Model configuration and system prompts
- `fitter/provider/` - AI model provider implementations
- `fitter/provider/base.py` - Abstract provider interface
- `fitter/provider/modules_factory.py` - Provider factory pattern
- `pyproject.toml` - Modern Python project configuration