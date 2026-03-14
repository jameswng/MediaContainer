# Makefile for sysloglogger (Native System Logging)

# --- Environment & Shell ---
SHELL      := /bin/bash --noprofile --norc
export PATH := /opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin

# --- Paths ---
VENV         := .venv
BIN          := $(VENV)/bin
PYTHON       := $(BIN)/python
PYTEST       := $(BIN)/pytest
RUFF         := $(BIN)/ruff
MYPY         := $(BIN)/mypy

# --- Source Files ---
ALL_SOURCES := $(shell find . -name "*.py" -not -path "*/.*")

# --- Targets ---
.PHONY: all clean setup test lint help

all: setup test lint

# 🧹 Clean up artifacts
clean:
	@echo "🧹 Cleaning previous builds and caches..."
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +

# 🏗️  Initial directory setup and virtual environment
setup: $(VENV)/bin/activate

$(VENV)/bin/activate:
	@echo "🏗️  Setting up virtual environment..."
	@/opt/homebrew/bin/python3.13 -m venv $(VENV)
	@$(BIN)/pip install --upgrade pip
	@$(BIN)/pip install pytest ruff mypy
	@touch $(VENV)/bin/activate

# 🧪 Validation
test: setup
	@echo "🧪 [TEST] Running Unit Tests..."
	@export PYTHONPATH=.:$$PYTHONPATH; $(PYTEST) || { echo "❌ [FAILED] Unit tests failed."; exit 1; }
	@echo "✅ [VERIFIED] Unit tests passed."

lint: setup
	@echo "🔍 [LINT] Running Ruff..."
	@$(RUFF) check .
	@echo "🔍 [TYPE] Running Mypy..."
	@$(MYPY) .
	@echo "✅ [VERIFIED] Linting and typing passed."

help:
	@echo "sysloglogger Build System"
	@echo "---------------"
	@echo "make setup    - Set up virtual environment and install dependencies"
	@echo "make test     - Run all tests"
	@echo "make lint     - Run linting and type checks"
	@echo "make clean    - Remove all build and cache artifacts"
