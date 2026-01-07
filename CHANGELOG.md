# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Moved CI workflow to correct location (`.github/workflows/ci.yml`)
- Aligned dependency management between Makefile and CI (now using `uv sync`)
- Project structure now follows standard Python package layout

### Added

- Committed `uv.lock` file for reproducible dependency resolution
- MyPy type checking with strict mode enabled
- Bandit security scanning for vulnerability detection
- `make check` target for unified quality gate (format, lint, security, type)
- Type hints to all source code and tests
- `py.typed` marker file for PEP 561 compliance
- CI pipeline now includes type checking and security scanning steps

### Removed

- Obsolete `seams-devops/` directory (files migrated to root in previous fix)
- Non-functional `deploy.sh` script
- Archive files (`files.zip`, `seams-devops.zip`)
- Added `*.zip` to `.gitignore` to prevent future archive commits

## [0.1.0] - 2025-01-06

### Added

- Initial release
