# Database Schema — SQLite + sqlite-vec

## Overview

Single SQLite database. All structured data and vector embeddings live in one file. No separate vector database service.

**File**: `db/hackathon26.db`

---

## Tables

### `temperature_cache`

Cached API responses to avoid re-fetching during demos.

```sql
CREATE TABLE temperature_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lat REAL NOT NULL,
  lng REAL NOT NULL,
  timestamp TEXT NOT NULL,          -- ISO-8601 of the measurement/forecast time
  data_json TEXT NOT NULL,          -- Full API response as JSON
  fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(lat, lng, timestamp)       -- Prevent duplicate cache entries
);

CREATE INDEX idx_cache_location ON temperature_cache(lat, lng);
CREATE INDEX idx_cache_time ON temperature_cache(timestamp);
```

### `heat_documents`

Reference documents for the RAG layer.

```sql
CREATE TABLE heat_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  source TEXT NOT NULL,             -- "WHO", "EPA", "City of Phoenix", etc.
  category TEXT NOT NULL,           -- who_guidelines, epa_standards, city_plans, research
  url TEXT,                         -- Original source URL if available
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_docs_category ON heat_documents(category);
```

### `heat_embeddings`

Vector embeddings for semantic search (sqlite-vec).

```sql
-- Requires sqlite-vec extension to be loaded
CREATE VIRTUAL TABLE heat_embeddings USING vec0(
  id INTEGER PRIMARY KEY,
  document_id INTEGER NOT NULL,     -- FK to heat_documents.id
  embedding FLOAT[384]              -- all-MiniLM-L6-v2 dimension
);

-- Alternative if sqlite-vec setup is problematic:
-- Store embeddings as BLOB and compute cosine similarity in application code
CREATE TABLE heat_embeddings_blob (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  document_id INTEGER NOT NULL,
  embedding BLOB NOT NULL,          -- Serialized float array
  model_name TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
  FOREIGN KEY (document_id) REFERENCES heat_documents(id)
);
```

### `evidence_log`

Every agent interaction logged with its reasoning chain.

```sql
CREATE TABLE evidence_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,         -- Groups a conversation
  tool_name TEXT NOT NULL,          -- Which MCP tool was called
  parameters TEXT NOT NULL,         -- JSON of input parameters
  result_summary TEXT,              -- Brief summary of what was returned
  reasoning TEXT,                   -- Agent's reasoning for calling this tool
  receipt_json TEXT,                -- Full evidence receipt
  timestamp TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_evidence_session ON evidence_log(session_id);
CREATE INDEX idx_evidence_tool ON evidence_log(tool_name);
```

### `sessions`

Chat session tracking.

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,              -- UUID
  title TEXT,                       -- Auto-generated or user-set
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### `messages`

Chat messages within sessions.

```sql
CREATE TABLE messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,               -- "user" or "assistant"
  content TEXT NOT NULL,
  tools_called TEXT,                -- JSON array of tool calls made
  evidence_ids TEXT,                -- JSON array of evidence_log.id references
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE INDEX idx_messages_session ON messages(session_id);
```

---

## Migration Strategy

Since this is a two-week hackathon, not a production system:

1. **Schema version 1**: Create all tables on first run
2. **No migration framework**: If schema changes, drop and recreate (it's a demo)
3. **Seed script**: `db/seed.ts` populates reference documents and cached API data

---

## Seed Data Plan

### Heat-Safety Documents (for RAG)

Target: 20-30 documents across categories:

| Category | Source | Count |
|----------|--------|-------|
| WHO guidelines | World Health Organization heat guidance | 3-5 |
| EPA standards | US EPA heat index documentation | 3-5 |
| City plans | Phoenix, Miami, Dubai heat action plans | 5-8 |
| Research | Key papers on urban heat islands | 3-5 |
| FortyGuard docs | API documentation, blog posts | 3-5 |

### Cached Temperature Data

Pre-seed for demo reliability:

| City | Why |
|------|-----|
| Phoenix, AZ | Classic extreme heat example |
| San Jose, CA | FortyGuard's US HQ location |
| Dubai, UAE | FortyGuard's UAE presence, extreme heat |
| Miami, FL | Humidity + heat combination |
| Delhi, India | Global south, massive heat exposure |

---

## sqlite-vec Setup Notes

sqlite-vec is a SQLite extension that adds vector search. Installation:

```bash
# Option 1: npm package (for TypeScript integration)
npm install sqlite-vec

# Option 2: Download pre-built binary
# Check https://github.com/asg017/sqlite-vec for releases
```

**Fallback**: If sqlite-vec is problematic, store embeddings as BLOBs and compute cosine similarity in application code. For a few dozen documents, this is fast enough.

```sql
-- Fallback: pure SQL cosine similarity for small doc sets
-- Application code deserializes BLOBs and computes dot product
SELECT d.title, d.content, d.source
FROM heat_documents d
JOIN heat_embeddings_blob e ON d.id = e.document_id
ORDER BY -- cosine similarity computed in app
LIMIT 5;
```
