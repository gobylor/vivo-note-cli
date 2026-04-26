# Obsidian import recipe

`vivo-note-cli` does not write to Obsidian. If you want to import exported notes into an Obsidian vault, use this as a recipe in your own automation.

## Export first

```bash
vivo-note export --notebook 日记 --format json --output /tmp/vivo-diary.json
```

Keep full exports in `/tmp` or another ignored private directory.

## Idempotency marker

Use paired markers keyed by vivo `guid`:

```markdown
<!-- vivo-note:<guid>:start -->
> Source: vivo Office Notes / <notebook> / <title> / created <time> / updated <time>

Converted Markdown body.
<!-- vivo-note:<guid>:end -->
```

On repeated imports:

1. find an existing `vivo-note:<guid>` block;
2. replace only that block;
3. never duplicate the same `guid`;
4. if matching human-written content exists without a marker, skip it and report the ambiguity.

## Suggested routing

These are examples, not package defaults:

- `日记` notebook -> daily notes such as `00-diary/YYYY/MM/YYYY-MM-DD 周X.md`.
- `追剧` notebook -> entertainment notes when the title confidently matches an existing entry.
- `todo` / `行李` notebooks -> task notes; do not invent due dates.

## Safety checklist

- Dry-run first and show create/update/skip counts.
- Write at most one representative sample before a bulk import.
- Preserve frontmatter and manual content.
- Keep raw exports and temporary reports out of Git.
