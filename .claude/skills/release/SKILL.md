---
name: release
description: Prepare and tag a MarketSensing release
---

# Release Skill

Prepare a versioned release of the MarketSensing platform.

## Steps

1. **Verify tests pass**: `pytest tests/ -v`
2. **Check lint**: `ruff check src/`
3. **Update version** in `pyproject.toml`
4. **Update CHANGELOG.md** with release notes
5. **Tag release**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
6. **Validate signal schema** — ensure all signal outputs match canonical schema
7. **Verify config compatibility** — all YAML configs load without errors

## Versioning

- **Major**: breaking changes to signal schema or API contracts
- **Minor**: new signal strategies, new instruments, new features
- **Patch**: bug fixes, threshold adjustments, documentation
