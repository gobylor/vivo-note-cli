# Releasing

The repository includes a GitHub Actions release workflow that builds wheel/sdist artifacts and uploads them to a GitHub Release when a `v*` tag is pushed.

It does not publish to PyPI yet.

## Local preflight

```bash
ruff check .
ruff format --check .
pytest
python -m build
python -m pip install --force-reinstall dist/vivo_note_cli-*.whl
vivo-note --help
```

## Tag release

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Future PyPI Trusted Publishing

When ready to publish to PyPI:

1. create the `vivo-note-cli` project on PyPI;
2. configure PyPI Trusted Publishing for this GitHub repository and a protected release environment;
3. add `pypa/gh-action-pypi-publish` to the release workflow;
4. keep source distributions free of private exports, database snapshots, or local test artifacts.
