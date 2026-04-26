# Releasing

The repository includes a GitHub Actions release workflow that builds wheel/sdist artifacts, uploads them to a GitHub Release, and publishes them to PyPI when a `v*` tag is pushed.

PyPI publishing uses Trusted Publishing through the GitHub `pypi` environment; no PyPI API token is required.

## Local preflight

```bash
ruff check .
ruff format --check .
pytest
vivo-note install-skills --dry-run
npx -y skills add . --list
python -m build
uv tool install --force git+https://github.com/gobylor/vivo-note-cli.git
vivo-note --help
uv tool uninstall vivo-note-cli
```

After PyPI publish succeeds, verify the registry install path:

```bash
uv tool install --force vivo-note-cli
vivo-note --help
uv tool uninstall vivo-note-cli
```

## Tag release

```bash
git tag v0.1.0
git push origin v0.1.0
```

If the `pypi` environment requires approval, approve the waiting `Publish to PyPI` job in GitHub Actions.

## PyPI Trusted Publishing setup

The PyPI pending publisher must match:

- PyPI project: `vivo-note-cli`
- Owner: `gobylor`
- Repository: `vivo-note-cli`
- Workflow: `release.yml`
- Environment: `pypi`

Keep source distributions free of private exports, database snapshots, or local test artifacts.
