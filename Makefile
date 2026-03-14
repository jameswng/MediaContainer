# Makefile for mediacontainer (Identify, group, extract, and play media objects)
# Adheres to strict environment standards: System PATH + Clean Shell

# --- Environment & Shell ---
SHELL      := /bin/bash --noprofile --norc
export PATH := /opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin

# --- Project Constants ---
PROJECT_NAME := mediacontainer

# --- Paths ---
VENV         := .venv
BIN          := $(VENV)/bin
PYTHON       := $(BIN)/python
PYTEST       := $(BIN)/pytest
RUFF         := $(BIN)/ruff
MYPY         := $(BIN)/mypy

# --- Installation Defaults ---
DEST_DIR     ?= bin
EXE_NAME     ?= $(PROJECT_NAME)

# --- Source Files ---
ALL_SOURCES := $(shell find mediacontainer -name "*.py")
ALL_TESTS   := $(shell find tests -name "*.py")

# --- Targets ---
.PHONY: all clean setup test lint version-advance commit help start stop restart wip push

all: setup test lint

# 🧹 Clean up artifacts
clean:
	@echo "🧹 Cleaning previous builds and caches..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .pytest_cache/
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} +

# 🏗️  Initial directory setup and virtual environment
setup: sync-ignore $(VENV)/bin/activate

install: setup
	@echo "📦 Installing $(PROJECT_NAME) command..."
	@$(BIN)/pip install -e .
	@echo "🚀 Creating environment-clean executable in $(DEST_DIR)/$(EXE_NAME)..."
	@mkdir -p $(DEST_DIR)
	@echo '#!/bin/bash' > $(DEST_DIR)/$(EXE_NAME)
	@echo '# MediaContainer Environment-Clean Safe Wrapper' >> $(DEST_DIR)/$(EXE_NAME)
	@echo 'if [ -z "$$MC_CLEANED" ]; then' >> $(DEST_DIR)/$(EXE_NAME)
	@echo '    export MC_CLEANED=1' >> $(DEST_DIR)/$(EXE_NAME)
	@echo '    exec env -i HOME="$$HOME" USER="$$USER" TERM="$$TERM" PATH="$$PATH" MC_CLEANED=1 "$$0" "$$@"' >> $(DEST_DIR)/$(EXE_NAME)
	@echo 'fi' >> $(DEST_DIR)/$(EXE_NAME)
	@echo "python3 -c 'import sys; from pathlib import Path; ROOT = Path(\"$(PWD)\").resolve(); sys.path.insert(0, str(ROOT)); from mediacontainer.cli import main; main()' \"\$$@\"" >> $(DEST_DIR)/$(EXE_NAME)
	@chmod +x $(DEST_DIR)/$(EXE_NAME)
	@echo "✅ Installed: You can now run '$(DEST_DIR)/$(EXE_NAME)' from any directory."


sync-ignore:
	@echo "🔄 Syncing ignore files..."
	@cp .claudeignore .geminiignore

$(VENV)/bin/activate: pyproject.toml
	@echo "🏗️  Setting up virtual environment..."
	@/opt/homebrew/bin/python3.13 -m venv $(VENV)
	@$(BIN)/pip install --upgrade pip
	@$(BIN)/pip install -e ".[dev]" || $(BIN)/pip install -e .
	@$(BIN)/pip install pytest ruff mypy
	@touch $(VENV)/bin/activate

# 🧪 Validation
test: setup
	@$(MAKE) version-advance
	@echo "🧪 [TEST] Running Unit Tests (Version $$(cat VERSION))..."
	@$(PYTEST) || { echo "❌ [FAILED] Unit tests failed."; exit 1; }
	@echo "✅ [VERIFIED] Unit tests passed."
	@$(MAKE) git-wip

lint: setup
	@echo "🔍 [LINT] Running Ruff..."
	@$(RUFF) check .
	@echo "🔍 [TYPE] Running Mypy..."
	@$(MYPY) mediacontainer
	@echo "✅ [VERIFIED] Linting and typing passed."

version-advance:
	@v=$$(cat VERSION); \
	major=$$(echo $$v | cut -d. -f1); \
	minor=$$(echo $$v | cut -d. -f2); \
	patch=$$(echo $$v | cut -d. -f3); \
	patch=$$(($$patch + 1)); \
	echo "$$major.$$minor.$$patch" > VERSION

# 🛠️ Git WIP (Shadow Commit)
wip:
	@echo "💾 Creating shadow WIP commit..."
	@git add .
	@last_msg=$$(git log -1 --pretty=%B 2>/dev/null); \
	if [[ $$last_msg == WIP:* ]]; then \
		git commit --amend --no-edit --allow-empty; \
	else \
		git commit -m "WIP: Build v$$(cat VERSION)" --allow-empty; \
	fi

# 🤝 Promote WIP to Real Commit
commit:
	@if [ -z "$(MSG)" ]; then echo "Error: MSG='message' is required."; exit 1; fi
	@$(MAKE) test
	@echo "🎯 Promoting WIP to explicit commit..."
	@git commit --amend -m "$(MSG) (v$$(cat VERSION))"
	@echo "✅ Finalized v$$(cat VERSION)."

# 🚀 Push changes to remote
push:
	@echo "🚀 Pushing changes to remote..."
	@git push
	@echo "✅ Changes pushed."

help:
	@echo "mediacontainer Build System"
	@echo "---------------"
	@echo "make setup    - Set up virtual environment and install dependencies"
	@echo "make install  - Install the CLI tool (supports DEST_DIR and EXE_NAME)"
	@echo "make test     - Run all tests and advance patch version"
	@echo "make lint     - Run linting and type checks"
	@echo "make clean    - Remove all build and cache artifacts"
	@echo "make commit MSG='msg' - Finalize changes and version"
	@echo "make wip      - Create a shadow WIP commit"
	@echo "make push     - Push changes to the remote repository"
