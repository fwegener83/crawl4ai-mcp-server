# Crawl4AI MCP Server - Initial Project Definition

## **FEATURE:**
* Minimaler MCP (Model Context Protocol) Server mit crawl4ai Integration
* Ein einzelnes Tool: `web_content_extract` für die Extraktion von sauberem Text-Inhalt aus Webseiten
* FastMCP Framework für schnelle Server-Implementierung
* Python-basiert mit uv für Dependency Management
* Einfache, fokussierte Funktionalität als Ausgangspunkt für spätere Erweiterungen

## **EXAMPLES:**
Das Projekt folgt den MCP Server Best Practices:
* `server.py` - Haupt-MCP Server mit FastMCP
* `tools/` - Ordner für Tool-Implementierungen
  * `tools/web_extract.py` - crawl4ai Integration für Content-Extraktion
* `tests/` - Unit Tests für Tools und Server
* `examples/` - Verwendungsbeispiele für den MCP Server

## **DOCUMENTATION:**
* FastMCP Documentation: https://github.com/jlowin/fastmcp
* crawl4ai Documentation: https://crawl4ai.com/
* MCP Specification: https://modelcontextprotocol.io/

## **OTHER CONSIDERATIONS:**
* `.env.example` für Konfigurationsvariablen
* `README.md` mit Setup-Anweisungen und Projektstruktur
* `pyproject.toml` mit uv-kompatiblen Dependencies
* `python_dotenv` für Umgebungsvariablen-Management
* Minimale crawl4ai Konfiguration (LLM-Provider optional für Start)
* Logging und Error Handling
* Type Hints und Pydantic Models für Tool-Parameter

## **INITIAL TOOL SPECIFICATION:**

### web_content_extract
**Beschreibung:** Extrahiert sauberen Text-Inhalt aus einer Webseite
**Parameter:** 
- `url` (string, required): URL der zu crawlenden Webseite
**Rückgabe:** Bereinigter Text-Inhalt ohne HTML-Tags und Navigation

**Crawl4ai Features für v1:**
- Basis Text-Extraktion
- User-Agent Rotation
- Einfache Error Handling

**Spätere Erweiterungen:**
- Screenshot-Funktionalität
- Strukturierte Datenextraktion
- PDF-Support
- Batch-Processing mehrerer URLs
