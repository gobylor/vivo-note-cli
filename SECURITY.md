# Security Policy

## Supported versions

Security fixes are considered for the latest released minor version.

## Reporting a vulnerability

Please do not open a public issue for vulnerabilities involving private note disclosure, unsafe writes, path traversal, or accidental upload of personal data.

Use GitHub private vulnerability reporting if enabled for this repository, or contact the maintainer from the GitHub owner profile with a short redacted report.

Helpful reports include:

- affected command and version;
- operating system;
- whether the issue requires a crafted database or affects normal vivo exports;
- a minimal synthetic reproduction database or schema, not real private note content.

## Security design

- The CLI snapshots the source database by default and opens the copy read-only.
- The default export omits raw HTML.
- The project intentionally avoids any default Obsidian write/sync behavior in v1.
