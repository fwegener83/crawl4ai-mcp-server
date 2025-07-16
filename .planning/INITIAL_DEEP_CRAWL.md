# FEATURE: Domain Deep Crawler MCP Tool

Ein neues MCP Tool für Crawl4AI, das Domain-basiertes Deep Crawling mit konfigurierbarer Tiefe ermöglicht. Das Tool nutzt Crawl4AI's Deep Crawling Strategien um Links innerhalb einer Domain systematisch zu folgen und zu crawlen.

## HAUPTFUNKTIONEN:

### 1. `domain_deep_crawl` - Hauptfunktion
Crawlt eine komplette Domain mit konfigurierbarer Tiefe und verschiedenen Strategien.

**Parameter:**
- `domain_url` (required, string): Die Basis-URL/Domain zum Crawlen 
- `max_depth` (optional, int, default: 2): Wie tief in die Domain gecrawlt werden soll (0 = nur Startseite)
- `crawl_strategy` (optional, string, default: "bfs"): Crawling-Strategie
  - "bfs" = Breadth-First Search (alle Links einer Ebene vor der nächsten)
  - "dfs" = Depth-First Search (so tief wie möglich vor Backtracking)
  - "best_first" = Intelligente Priorisierung basierend auf Relevanz
- `max_pages` (optional, int): Maximale Anzahl zu crawlender Seiten (Schutz vor runaway crawls)
- `include_external` (optional, bool, default: false): Ob externe Links verfolgt werden sollen
- `url_patterns` (optional, array): Array von URL-Mustern zum Filtern (z.B. ["*blog*", "*docs*"])
- `exclude_patterns` (optional, array): Array von auszuschließenden Mustern (z.B. ["*admin*", "*login*"])
- `keywords` (optional, array): Keywords für BestFirst-Scoring (nur bei crawl_strategy="best_first")
- `stream_results` (optional, bool, default: false): Ob Ergebnisse gestreamt werden sollen

**Rückgabe:**
```json
{
  "success": true,
  "crawl_summary": {
    "total_pages": 45,
    "max_depth_reached": 2,
    "strategy_used": "bfs",
    "pages_by_depth": {"0": 1, "1": 12, "2": 32}
  },
  "pages": [
    {
      "url": "https://example.com/page1",
      "depth": 1,
      "title": "Page Title", 
      "content": "markdown content...",
      "success": true,
      "metadata": {
        "score": 0.8,
        "crawl_time": "2025-07-16T10:30:00Z"
      }
    }
  ]
}
```

### 2. `domain_link_preview` - Hilfsfunktion
Schnelle Vorschau der verfügbaren Links einer Domain ohne vollständiges Crawling.

**Parameter:**
- `domain_url` (required, string): Die Basis-URL zum Analysieren
- `include_external` (optional, bool, default: false): Ob externe Links mit angezeigt werden sollen

**Rückgabe:**
```json
{
  "success": true,
  "domain": "example.com",
  "total_links": 23,
  "internal_links": 18,
  "external_links": 5,
  "links": [
    {
      "url": "https://example.com/about",
      "text": "About Us",
      "type": "internal"
    }
  ]
}
```

## TECHNISCHE UMSETZUNG:

### Dateien Structure:
```
tools/
├── domain_crawler.py          # Hauptlogik für Domain Deep Crawling
├── domain_link_preview.py     # Link-Vorschau Funktionalität  
├── error_sanitizer.py         # Bereits vorhanden, wiederverwenden
└── __init__.py                # Tool-Registrierung

tests/
├── test_domain_crawler.py     # Unit Tests für Domain Crawler
├── test_domain_link_preview.py # Unit Tests für Link Preview
└── test_domain_integration.py # Integration Tests
```

### Crawl4AI Integration:
- **BFSDeepCrawlStrategy**: Für breadth-first Crawling
- **DFSDeepCrawlStrategy**: Für depth-first Crawling  
- **BestFirstCrawlingStrategy**: Für intelligente, keyword-basierte Priorisierung
- **FilterChain**: Für URL-Pattern Filtering
- **KeywordRelevanceScorer**: Für BestFirst-Strategie

### Sicherheit & Performance:
- Domain-Validation (nur HTTP/HTTPS URLs)
- Maximale Crawl-Limits als Schutz vor runaway crawls
- Error Message Sanitization (bestehende error_sanitizer.py verwenden)
- Asynchrone Implementierung mit proper error handling
- Stream-Modus für große Crawls zur Memory-Effizienz

### FastMCP Integration:
```python
# In server.py registrieren:
mcp.tool()(domain_deep_crawl)
mcp.tool()(domain_link_preview)
```

## BEISPIELE:

### Basis Domain Crawl:
```json
{
  "name": "domain_deep_crawl",
  "arguments": {
    "domain_url": "https://docs.example.com",
    "max_depth": 2,
    "max_pages": 50
  }
}
```

### Fokussiertes Crawling mit Patterns:
```json
{
  "name": "domain_deep_crawl", 
  "arguments": {
    "domain_url": "https://blog.example.com",
    "max_depth": 3,
    "crawl_strategy": "best_first",
    "url_patterns": ["*tutorial*", "*guide*"],
    "exclude_patterns": ["*admin*", "*login*"],
    "keywords": ["python", "crawling", "tutorial"],
    "max_pages": 25
  }
}
```

### Link Vorschau:
```json
{
  "name": "domain_link_preview",
  "arguments": {
    "domain_url": "https://example.com"
  }
}
```

## ENTWICKLUNGSSCHRITTE:

1. **Phase 1**: Basis-Implementierung von `domain_deep_crawl` mit BFS-Strategie
2. **Phase 2**: DFS und BestFirst-Strategien hinzufügen
3. **Phase 3**: URL-Pattern Filtering implementieren
4. **Phase 4**: `domain_link_preview` Hilfsfunktion
5. **Phase 5**: Stream-Modus für große Crawls
6. **Phase 6**: Umfassende Tests und Dokumentation

## TESTING STRATEGY:

### Fast Tests (Mock-basiert):
- Unit Tests für Strategie-Auswahl
- Parameter-Validation Tests
- Error Handling Tests mit Mock Crawler

### Integration Tests:
- Echte Domain-Crawls mit kleinen Test-Sites
- Performance Tests mit verschiedenen Strategien
- Edge Cases (leere Domains, Fehlerhafte URLs)

### CI/CD Integration:
- Fast Tests in PR-Pipeline
- Integration Tests nur auf main branch
- Performance Regression Tests

## DOKUMENTATION:

- README Update mit neuen Tools
- API Dokumentation für beide Funktionen
- Beispiele für verschiedene Use Cases
- Best Practices für Domain Crawling
