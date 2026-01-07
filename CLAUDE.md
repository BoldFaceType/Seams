# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Seams** is a Python package for connecting components seamlessly. This is an early-stage project (v0.1.0, Alpha) following modern Python development practices with a lean, fast toolchain.

**Tech Stack:**
- Python 3.11+ (managed by mise)
- uv for package management (10-100x faster than pip)
- Ruff for linting and formatting (replaces black, isort, flake8)
- pytest with coverage enforcement (≥80%)
- Hatchling build backend (PEP 621 compliant)

## Development Commands

### Initial Setup
```bash
# Install Python version manager and set Python 3.12
mise install
mise trust

# Bootstrap development environment (one-time)
make bootstrap

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Daily Development
```bash
make format     # Auto-format code with ruff
make lint       # Check code quality (no auto-fix)
make test       # Run full test suite with coverage (must pass ≥80%)
make test-fast  # Quick test iteration (no coverage, stops on first failure)
make test-last  # Re-run only previously failed tests
make ci         # Local CI simulation (lint + test)
make clean      # Remove build artifacts and caches
```

### Running Single Tests
```bash
# Specific test file
uv run pytest tests/test_init.py

# Specific test function
uv run pytest tests/test_init.py::test_version

# With verbose output
uv run pytest -v tests/test_init.py::test_version

# Stop on first failure with short traceback
uv run pytest -x --tb=short tests/
```

### Pre-commit Hooks
```bash
# Install hooks (one-time, runs format + lint before each commit)
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Code Quality Standards

### Coverage Requirements
- Minimum test coverage: **80%** (enforced in CI)
- Branch coverage enabled
- Coverage report shows missing lines

### Ruff Configuration
- Line length: 88 characters
- Python 3.11+ syntax
- Selected rules: E, W, F, I, B, C4, UP, ARG, SIM
- Disabled: E501 (line length, handled by formatter), B008, B905
- Import sorting: known-first-party = ["seams"]
- Quote style: double quotes
- Indent: spaces

### Testing Conventions
- Test files: `tests/test_*.py`
- Source path: `src/seams`
- Strict markers enforced
- Short tracebacks by default

## Project Structure

```
seams/
├── src/seams/          # Package source code
│   └── __init__.py     # Package metadata (__version__, __author__)
├── tests/              # Test suite
│   ├── conftest.py     # Shared pytest fixtures
│   └── test_*.py       # Test modules
├── .mise.toml          # Tool versions (Python 3.12)
├── pyproject.toml      # Package config, tool settings, dependencies
├── Makefile            # Development automation
└── .pre-commit-config.yaml  # Git hooks for code quality
```

## CI/CD Pipeline

**Workflow:** `.github/workflows/ci.yml`

Runs on:
- Every push to `main`
- All pull requests to `main`
- Concurrent runs canceled for same branch

**Matrix:** Python 3.11 and 3.12

**Steps:**
1. Lint with ruff (`ruff check .`)
2. Check formatting (`ruff format --check .`)
3. Run tests with coverage (fail if <80%)
4. Upload coverage to Codecov (Python 3.12 only, non-blocking)

## Development Workflow

### Adding New Features
1. Create feature branch
2. Write tests first (TDD encouraged)
3. Implement feature in `src/seams/`
4. Run `make format` to auto-format
5. Run `make ci` to verify all checks pass locally
6. Push and create PR (CI will re-validate)

### Fixing Bugs
1. Write failing test that reproduces the bug
2. Fix the bug
3. Run `make test-fast` for quick iteration
4. Run `make ci` before committing

### Code Style
- Use type hints where beneficial (not strictly enforced yet)
- Follow existing patterns in `src/seams/__init__.py`
- Keep functions focused and testable
- Document public APIs with docstrings

## Package Management

**Never use pip directly** - always use `uv`:

```bash
# Add dependency
uv add requests

# Add dev dependency
uv add --dev pytest-asyncio

# Install dependencies
uv sync --all-extras --dev

# Remove dependency
uv remove requests
```

## Tool Versions

Managed by mise (`.mise.toml`):
- Python: 3.12
- uv: latest (auto-updated in CI)

Pre-commit hooks:
- ruff-pre-commit: v0.8.4
- pre-commit-hooks: v5.0.0

## Publishing (Future)

Build backend: Hatchling
- Source: `src/seams`
- Build: `uv build`
- Publish: `uv publish` (when ready)

## Notes

- This is an **early-stage project** - the codebase is minimal and will evolve
- Coverage requirement (≥80%) is enforced in CI and local `make test`
- Pre-commit hooks prevent committing code that fails formatting/linting
- The `make ci` command simulates the exact CI pipeline locally

---

## Memory

### Code Review Summary (2026-01-06)

Comprehensive review of Seams v0.1.0 identifying infrastructure gaps, tooling inconsistencies, and missing quality enforcement mechanisms.

**Review Scope:**
- Source code (src/seams/)
- Test suite (tests/)
- Configuration files (pyproject.toml, Makefile, CI, pre-commit)
- Documentation (README, CHANGELOG)
- DevOps tooling (mise, deploy.sh)

### Priority Issues

#### 🔴 CRITICAL (Blocks Production Readiness)

1. **Project Structure Mismatch**
   - CI workflow location incorrect: `ci.yml` in root should be `.github/workflows/ci.yml`
   - Missing root `README.md` (only in seams-devops subdirectory)
   - Directory structure not production-ready

2. **Tooling Inconsistency: uv Commands**
   - Makefile uses: `uv pip install -e ".[dev]"`
   - CI uses: `uv sync --all-extras --dev`
   - Different commands may produce different dependency resolution results
   - **Risk:** CI passes but local development breaks (or vice versa)

3. **Missing Quality Gates (Project Guidelines Violations)**
   - No MyPy type checking (required by project coding standards)
   - No Bandit security scanning (required by security standards)
   - No `make check` target (required quality gate from guidelines)
   - pyproject.toml missing MyPy configuration

4. **Test Coverage Will Fail**
   - Only 2 trivial tests (test_import, test_author)
   - 80% coverage threshold impossible to meet with no actual implementation
   - CI will fail immediately on first real code commit

#### 🟡 HIGH (Quality & Maintainability)

5. **Missing Type Safety Infrastructure**
   - No type hints in `src/seams/__init__.py`
   - No `py.typed` marker file (PEP 561 - makes package not type-checkable by consumers)
   - __all__ export list is empty but declared

6. **Dependency Management Issues**
   - No lockfile (uv.lock should be committed for reproducibility)
   - No dependency version constraints in pyproject.toml
   - Missing optional dependency groups (e.g., [test], separate from [dev])

7. **Incomplete Deploy Script**
   - `deploy.sh` is non-functional template
   - Doesn't actually copy/deploy files
   - Manual steps required - defeats automation purpose

8. **CI/Makefile Divergence**
   - CI runs `ruff format --check` (read-only)
   - Makefile `format` target runs `ruff format` + `ruff check --fix` (modifies)
   - Can cause "works locally but fails in CI" scenarios

#### 🟢 MEDIUM (Developer Experience & Documentation)

9. **Unused Test Infrastructure**
   - `conftest.py` has placeholder `sample_fixture` that's never used
   - Dead code in test suite

10. **Missing Documentation**
    - No CONTRIBUTING.md (how to contribute)
    - No architecture docs (what will this package do?)
    - No examples/ directory
    - No API documentation structure

11. **Placeholder Data**
    - Email in pyproject.toml: `boldface@example.com` (should be real or omitted)
    - README features list: "Feature 1, Feature 2, Feature 3" (placeholder text)

12. **GitHub Repository Setup Incomplete**
    - No issue templates (.github/ISSUE_TEMPLATE/)
    - No PR template (.github/pull_request_template.md)
    - No CODEOWNERS file
    - No security policy (SECURITY.md)

#### 🔵 LOW (Nice-to-Have)

13. **CHANGELOG Inconsistency**
    - Unreleased section duplicates 0.1.0 content
    - Should use [Unreleased] for future work only

14. **Missing CI Badges**
    - README has CI badge but could add: coverage %, Python versions, license
    - Could add: PyPI version (when published), downloads

15. **No Performance Baseline**
    - No benchmarks/ directory
    - No performance regression tests

### Task List (Prioritized)

**Must-Fix Before v0.2.0:**
- [x] Fix CI workflow location (.github/workflows/) ✅ PR #1
- [x] Align uv commands (Makefile ↔ CI) ✅ PR #1
- [x] Add MyPy configuration and type checking ✅ PR #2
- [x] Add Bandit security scanning ✅ PR #2
- [x] Add `make check` target per guidelines ✅ PR #2
- [x] Add py.typed marker file ✅ PR #2
- [x] Create uv.lock and commit ✅ PR #1
- [x] Remove or implement deploy.sh ✅ PR #2.1

**Should-Fix Before v0.2.0:**
- [x] Add type hints to __init__.py ✅ PR #2
- [ ] Populate __all__ or remove declaration
- [ ] Remove unused sample_fixture
- [ ] Align format commands (Makefile ↔ CI)
- [ ] Add CONTRIBUTING.md
- [ ] Document architecture/roadmap
- [ ] Replace placeholder email/features

**Nice-to-Have:**
- [ ] Add GitHub templates (issue, PR)
- [ ] Add SECURITY.md
- [ ] Add CODEOWNERS
- [x] Clean up CHANGELOG ✅ PR #1
- [ ] Add coverage badge
- [ ] Create examples/ directory

### Suggested Pull Request Groupings

#### PR #1: Fix Project Structure & CI Alignment (Critical)
**Goal:** Make CI workflow functional and align tooling
**Files:**
- Move `ci.yml` → `.github/workflows/ci.yml`
- Move `seams-devops/README.md` → `README.md` (root)
- Update Makefile to use `uv sync` instead of `uv pip install`
- Update CI activation command to match
- Generate and commit `uv.lock`

**Why Together:** These are foundational infrastructure fixes that affect all future work.

---

#### PR #2: Add Missing Quality Gates (Critical)
**Goal:** Enforce type checking and security scanning per project guidelines
**Files:**
- `pyproject.toml`: Add [tool.mypy] section with strict mode
- `pyproject.toml`: Add dev dependencies (mypy, bandit)
- `Makefile`: Add `check` target: black → ruff → bandit → mypy
- `.github/workflows/ci.yml`: Add type check and security scan steps
- `src/seams/__init__.py`: Add type hints
- Create `src/seams/py.typed` (empty marker file)

**Why Together:** Complete quality enforcement per coding standards. Type safety + security scanning are complementary.

---

#### PR #3: Test Infrastructure Cleanup (High)
**Goal:** Remove dead code and prepare for real testing
**Files:**
- `tests/conftest.py`: Remove sample_fixture or add comment explaining it's a template
- Add test utilities documentation in conftest docstring
- Add test examples for future contributors

**Why Together:** Small, focused cleanup of test infrastructure.

---

#### PR #4: Dependency Management & Tooling Alignment (High)
**Goal:** Make local dev and CI produce identical results
**Files:**
- `Makefile`: Change `format` to match CI (add `--check` flag, remove `--fix`)
- Add `make format-fix` for local auto-formatting
- `pyproject.toml`: Add version constraints for dependencies
- `pyproject.toml`: Split [dev] into [test] and [dev] groups
- Update documentation in README and CLAUDE.md

**Why Together:** Tooling consistency prevents "works on my machine" issues.

---

#### PR #5: Documentation & Onboarding (Medium)
**Goal:** Help contributors understand and contribute to the project
**Files:**
- Create `CONTRIBUTING.md` with:
  - How to set up dev environment
  - How to run tests
  - PR guidelines
  - Code style requirements
- Create `docs/architecture.md` explaining project vision
- Create `examples/` directory with basic usage examples
- Update README.md to replace placeholder features
- Fix email in pyproject.toml or remove

**Why Together:** All documentation and onboarding improvements.

---

#### PR #6: GitHub Repository Setup (Medium)
**Goal:** Standardize issue/PR workflow
**Files:**
- Create `.github/ISSUE_TEMPLATE/bug_report.md`
- Create `.github/ISSUE_TEMPLATE/feature_request.md`
- Create `.github/pull_request_template.md`
- Create `SECURITY.md` (vulnerability reporting)
- Create `CODEOWNERS` (optional, if team grows)

**Why Together:** GitHub workflow automation as a single package.

---

#### PR #7: Deploy Script Fix (Low)
**Goal:** Remove non-functional deployment script
**Files:**
- Delete `deploy.sh` (incomplete and misleading)
- Update README if it references deploy.sh

**Why Together:** Single-file cleanup, low impact.

---

#### PR #8: Polish & Maintenance (Low)
**Goal:** Clean up minor inconsistencies
**Files:**
- `CHANGELOG.md`: Remove duplicate Unreleased/0.1.0 content
- `README.md`: Add coverage badge
- `README.md`: Add Python version badge
- Consider adding benchmarks/ skeleton for future performance work

**Why Together:** Low-priority polish items that don't affect functionality.

---

### Review Methodology

**Tools Used:**
- Manual code inspection
- Configuration file analysis
- Cross-reference with project guidelines (CLAUDE.md, AGENT_Instructions)
- Tooling consistency validation (Makefile ↔ CI ↔ pyproject.toml)

**Not Reviewed:**
- Runtime behavior (no actual functionality exists yet)
- Performance characteristics (no code to profile)
- Security vulnerabilities in dependencies (no dependencies beyond dev tools)

**Limitations:**
- Unable to access live GitHub repository (network issues)
- Review based on local seams-devops.zip extraction
- May miss branch-specific or recent commits

### Action Items for Next Session

1. **Immediate:** Implement PR #1 (Structure & CI) - blocks all other work
2. **High Priority:** Implement PR #2 (Quality Gates) - required by coding standards
3. **Before Adding Features:** Implement PR #3 (Test Cleanup) and PR #4 (Tooling Alignment)
4. **Ongoing:** PRs #5-8 can be tackled in parallel or as time permits

**Estimated Effort:**
- PR #1: 30 min (file moves + config updates)
- PR #2: 1-2 hours (MyPy config + type hints + testing)
- PR #3: 15 min (trivial cleanup)
- PR #4: 45 min (dependency management + docs)
- PR #5: 2-3 hours (documentation writing)
- PR #6: 1 hour (GitHub templates)
- PR #7: 5 min (delete file)
- PR #8: 30 min (polish)

**Total:** ~6-8 hours to address all issues

---

### Implementation Status

#### ✅ Completed PRs

**PR #1: Fix Project Structure & CI Alignment** (Completed: 2026-01-06)
- ✅ Moved `ci.yml` to `.github/workflows/ci.yml`
- ✅ Moved project files from `seams-devops/` to root directory
- ✅ Updated Makefile: `bootstrap` and `install` now use `uv sync --all-extras --dev`
- ✅ Generated and committed `uv.lock` (63KB, 19 packages installed)
- ✅ Updated CHANGELOG.md with changes
- ✅ Project structure now matches standard Python package layout

**Impact:** Foundation fixed. CI workflow is now properly located and dependency management is consistent between local development and CI.

---

**PR #2: Add Missing Quality Gates** (Completed: 2026-01-06)
- ✅ Added MyPy (v1.19.1) and Bandit (v1.9.2) to dev dependencies
- ✅ Configured MyPy with strict mode in `pyproject.toml`
- ✅ Configured Bandit security scanning in `pyproject.toml`
- ✅ Added type hints to `src/seams/__init__.py` (`__version__`, `__author__`)
- ✅ Added type hints to all test files (`tests/test_init.py`, `tests/conftest.py`)
- ✅ Created `src/seams/py.typed` marker file (PEP 561 compliance)
- ✅ Added `make check` target (format → lint → security → type)
- ✅ Updated CI workflow with security scan and type check steps
- ✅ All quality gates passing (6 files formatted, 0 lint issues, 0 security issues, 0 type errors)

**Impact:** Complete quality enforcement now in place. Code is type-safe, security-scanned, and follows all project coding standards. Package is now PEP 561 compliant for external type checkers.

---

**PR #2.1: Repository Cleanup** (Completed: 2026-01-06)
- ✅ Removed obsolete `seams-devops/` directory (~100KB)
- ✅ Removed non-functional `deploy.sh` script
- ✅ Removed archive files (`files.zip`, `seams-devops.zip`)
- ✅ Added `*.zip` to `.gitignore` to prevent future archive commits
- ✅ Updated CHANGELOG.md with cleanup details

**Impact:** Cleaner repository structure. No duplicate files, no confusing partial scripts. All "Must-Fix Before v0.2.0" critical tasks now complete (8/8 = 100%).

**Next Priority:** PR #3 (Test Infrastructure Cleanup) and PR #4 (Tooling Alignment)

---

*Last Updated: 2026-01-06 | Reviewed by: Claude Code | Codebase Version: v0.1.0+PR2.1*
