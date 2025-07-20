# Crawl4AI MCP Server

MCP Server für Web-Content-Extraktion mit [Crawl4AI](https://github.com/unclecode/crawl4ai).

## Installation

```bash
git clone <repository-url>
cd crawl4ai-mcp-server
uv install
playwright install
```

## MCP Inspector Setup

```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector --config mcp-inspector-config.json --server crawl4ai
```

Öffnet Browser auf http://localhost:3000

## Claude Desktop Integration

Konfiguration in `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "/absolute/path/to/crawl4ai-mcp-server/.venv/bin/python",
      "args": ["/absolute/path/to/crawl4ai-mcp-server/server.py"]
    }
  }
}
```

**Alternative mit uv (falls global installiert):**
```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/crawl4ai-mcp-server", "python", "server.py"]
    }
  }
}
```

## Verfügbare Tools

### `web_content_extract`
Extrahiert Content von einzelnen Webseiten als Markdown.

**Parameter:**
- `url` (string, required): URL der zu crawlenden Webseite

**Beispiel:**
```json
{
  "name": "web_content_extract",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### `domain_deep_crawl_tool`
Tiefes Crawling einer ganzen Domain mit konfigurierbaren Strategien.

**Parameter:**
- `domain_url` (string, required): Basis-URL/Domain zum Crawlen
- `max_depth` (int, default: 1): Maximale Crawl-Tiefe (0-10)
- `crawl_strategy` (string, default: "bfs"): Crawling-Strategie (bfs, dfs, best_first)
- `max_pages` (int, default: 10): Maximale Anzahl Seiten (1-1000)
- `include_external` (bool, default: false): Externe Links einschließen
- `url_patterns` (list, optional): URL-Patterns zum Einschließen
- `exclude_patterns` (list, optional): URL-Patterns zum Ausschließen
- `keywords` (list, optional): Keywords für BestFirst-Scoring

### `domain_link_preview_tool`
Schnelle Link-Vorschau einer Domain ohne vollständiges Crawling.

**Parameter:**
- `domain_url` (string, required): Basis-URL/Domain zum Analysieren  
- `include_external` (bool, default: false): Externe Links einschließen

## Tests

```bash
# Alle Tests
pytest

# Nur schnelle Tests (empfohlen für Entwicklung)
pytest -m "not slow"

# Mit Coverage
pytest --cov=. --cov-report=html
```

## Entwicklung

Server direkt starten:
```bash
uv run python server.py
```

## Troubleshooting

1. **Module not found**: Stelle sicher, dass alle Dependencies installiert sind: `uv install`
2. **Playwright fehlt**: Browser installieren: `playwright install`
3. **MCP Inspector verbindet nicht**: Prüfe ob Server läuft und Config korrekt ist

## Links

- [Crawl4AI Documentation](https://github.com/unclecode/crawl4ai)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [Claude Desktop Integration](https://docs.anthropic.com/en/docs/build-with-claude/mcp)