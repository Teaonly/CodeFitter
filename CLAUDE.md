# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeFitter (代码钳工) is a command-line coding assistant designed for lightweight and precise code generation and manipulation. It's structured as a semi-automated coding tool with fine-grained control.

## Architecture

### Core Structure
- **Main Entry Point**: `fitter/main.py` - Contains the primary application logic and command-line interface
- **Configuration**: `fitter/lore/write.yaml` - System prompts and task templates for AI interactions
- **Provider System**: `fitter/provider/` - Modular system for different AI model providers (currently empty but structured for LLM integration)

### Key Dependencies
- `prompt-toolkit>=3.0.52` - For interactive command-line interfaces
- `pyyaml>=6.0.2` - Configuration file parsing
- `rich>=14.1.0` - Enhanced terminal output formatting
- `setuptools>=80.9.0` - Package management and build system

### Configuration System
The application uses YAML-based configuration stored in `fitter/lore/write.yaml` which contains:
- System prompts for AI behavior
- Task templates for different coding scenarios
- User interaction patterns
- GitHub search integration templates

## Development Commands

### Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Run the main application
fitter
```

### Build and Package
```bash
# Build the package using setuptools
python setup.py build

# Create distribution
python setup.py sdist
```

### Testing
Currently no formal test framework is implemented. The project structure suggests future test files should be placed in a dedicated test directory.

## Current Implementation Status

### Completed Features
- Basic package structure with setuptools configuration
- Main application skeleton with configuration loading
- YAML-based prompt and template system
- Provider abstraction layer for AI model integration

### Planned Features (Based on TODO comments)
- Command-line argument parsing for file operations
- Support for composing files with input/output specifications
- GitHub search integration for code discovery
- AI model provider implementations

### Development Notes
- The main application is currently in early development stage
- Command-line interface is planned but not fully implemented
- The system is designed to support multiple AI model providers through the provider abstraction
- Configuration is loaded from YAML files in the `lore/` directory

## Code Style and Conventions
- Follow Python PEP 8 conventions
- Use type hints where appropriate
- Modular design with clear separation of concerns
- Configuration-driven approach for AI prompts and behavior

## File Structure Conventions
- `fitter/main.py` - Application entry point
- `fitter/lore/` - Configuration and prompt templates
- `fitter/provider/` - AI model provider implementations
- `pyproject.toml` - Modern Python project configuration
- No test directory currently exists