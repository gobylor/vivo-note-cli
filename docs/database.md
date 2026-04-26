# Known vivo NoteSync.db shape

This project targets the vivo Office / Atomic Notes desktop database usually found at:

```text
~/Library/Application Support/pcsuite/database/NoteSync.db
```

Known tables observed in local read-only inspection:

```text
Document, File, Note, NoteBook, NoteCache, Resource, Tag, ToDo, User
```

## Active row semantics

For the known schema, `deleted = 1` means the row is currently visible/active. This is unusual compared with many applications, so exporter queries intentionally filter with:

```sql
Note.deleted = 1
NoteBook.deleted = 1
```

When the column is absent in a future or synthetic schema, the library treats rows as active instead of guessing.

## Core tables

| Table | Purpose | Important columns |
| --- | --- | --- |
| `NoteBook` | left-side note folder/notebook | `guid`, `name`, `sort`, `deleted` |
| `Note` | rich-text notes | `id`, `guid`, `noteBookGuid`, `title`, `contentNote`, `originContent`, `contentDigest`, `createTime`, `updateTime`, `contentUpdateTime`, `type`, `stickTop`, `deleted` |
| `Resource` | note attachments | `noteGuid`, `fileID`, `name`, `mime`, `deleted` |
| `Document` | document tab entries | `fileID`, `name`, `mime`, `documentSize`, `deleted` |
| `File` | local paths for resources/documents | `guid`, `path`, `mimeType`, `fileSize` |

## Body fields

The exporter reads note body HTML from:

1. `Note.contentNote` when present and non-empty;
2. otherwise `Note.originContent`;
3. otherwise an empty string.

`contentDigest` is only a preview and should not be treated as the complete note body.

## Timestamps

Known timestamp columns are Unix epoch milliseconds. CLI output formats them as local time strings:

```text
YYYY-MM-DD HH:MM:SS
```

## Privacy note

Schema documentation should never include real note text, real database snapshots, phone numbers, addresses, credentials, or other private values.
