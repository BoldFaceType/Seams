# Makefile - Dev automation for Seams
# Usage: make <target>
# Run 'make help' for available targets

.PHONY: help bootstrap install lint format check test test-fast test-last ci clean

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# VARIABLES
# ============================================================================
PACKAGE_NAME := seams
UV := uv

# ============================================================================
# HELP
# ============================================================================
help: ## Show this help message
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# SETUP
# ============================================================================
bootstrap: ## Create venv and install all dependencies (run once)
	@echo "🚀 Bootstrapping development environment..."
	$(UV) venv
	$(UV) sync --all-extras --dev
	@echo "✅ Bootstrap complete. Activate with: source .venv/bin/activate"

install: ## Install package in editable mode with dev deps
	$(UV) sync --all-extras --dev

# ============================================================================
# CODE QUALITY
# ============================================================================
lint: ## Run linter (ruff check)
	$(UV) run ruff check .

format: ## Format code (ruff format)
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

check: ## Run all quality checks (format, lint, security, type)
	@echo "🔍 Running quality gate checks..."
	@echo "1️⃣  Checking code formatting..."
	$(UV) run ruff format --check .
	@echo "2️⃣  Running linter..."
	$(UV) run ruff check .
	@echo "3️⃣  Running security scan..."
	$(UV) run bandit -r src/ -ll
	@echo "4️⃣  Running type checker..."
	$(UV) run mypy src/ tests/
	@echo "✅ All quality checks passed!"

# ============================================================================
# TESTING
# ============================================================================
test: ## Run full test suite with coverage
	$(UV) run pytest --cov=$(PACKAGE_NAME) --cov-report=term --cov-fail-under=80

test-fast: ## Run tests without coverage (faster iteration)
	$(UV) run pytest -x --tb=short

test-last: ## Re-run only failed tests
	$(UV) run pytest --lf --tb=short

# ============================================================================
# CI SIMULATION
# ============================================================================
ci: lint test ## Run full CI locally (lint + test)
	@echo "✅ CI simulation passed"

# ============================================================================
# CLEANUP
# ============================================================================
clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	rm -rf .ruff_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned"
