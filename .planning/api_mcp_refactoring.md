# Refactoring-Plan: Gemeinsame Logik für API- und MCP-Endpunkte

## Ausgangslage
- **API-Endpunkte**: Stabil, getestet, funktionieren End-to-End.
- **MCP-Endpunkte**: Teilweise fehlerhaft, inkonsistente Logik im Vergleich zur API.
- **Problem**: Logik-Duplikation zwischen API und MCP (Validierung, Zugriff auf Services, Fehlerbehandlung).  
  → Wartungsaufwand und Risiko von Inkonsistenzen.

## Ziel
- **Zentrale Logik** für API und MCP in einer gemeinsamen Service-/Use-Case-Schicht.
- **API-Stabilität erhalten**: Beim Refactoring darf sich das Verhalten der API nicht ändern.
- **MCP-Endpunkte korrigieren**: Auf dieselbe geprüfte Logik setzen wie die API.

---

## Best Practices & Empfehlungen

### 1. Gemeinsame Service-/Use-Case-Schicht
- Alle wiederverwendbaren Operationen (Validierung, Geschäftslogik, Aufruf von `vector_service`) in **eine zentrale Funktion** verschieben.
- API- und MCP-Endpunkte sollen nur:
  - Eingaben ins richtige Format mappen
  - Service-Funktion aufrufen
  - Ergebnis ins Ziel-Format umwandeln

**Beispiel:**
```python
# application_layer/vector_search.py
async def search_vectors_use_case(query, collection_name, limit, similarity_threshold):
    if not query:
        raise ValueError("MISSING_QUERY")

    if limit < 1:
        raise ValueError("INVALID_LIMIT")

    if similarity_threshold < 0 or similarity_threshold > 1:
        raise ValueError("INVALID_THRESHOLD")

    if collection_name:
        await _validate_collection_exists(collection_name)

    if not vector_service.vector_available:
        raise RuntimeError("SERVICE_UNAVAILABLE")

    results = await vector_service.search_vectors(query, collection_name, limit, similarity_threshold)
    
    return [
        {
            **r.model_dump(),
            "similarity_score": r.score
        }
        for r in results
    ]
```

---

### 2. API-Endpunkt (unverändert im Verhalten)
```python
@app.post("/api/vector-sync/search")
async def search_vectors(request: dict):
    try:
        results = await search_vectors_use_case(
            query=request.get("query"),
            collection_name=request.get("collection_name"),
            limit=request.get("limit", 10),
            similarity_threshold=request.get("similarity_threshold", 0.7)
        )
        return {"success": True, "results": results}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.error(f"search_vectors error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### 3. MCP-Endpunkt (korrigiert, nutzt gemeinsame Logik)
```python
@mcp_server.tool()
async def search_collection_vectors(query: str, collection_name: Optional[str] = None, limit: int = 10, similarity_threshold: float = 0.7) -> str:
    try:
        results = await search_vectors_use_case(query, collection_name, limit, similarity_threshold)
        return json.dumps({"success": True, "results": results})
    except Exception as e:
        logger.error(f"MCP search_collection_vectors error: {e}")
        return json.dumps({"success": False, "error": str(e)})
```

---

## Vorteile
- **Homogenität**: API und MCP liefern konsistente Ergebnisse.
- **Wartbarkeit**: Änderungen nur an einer Stelle notwendig.
- **Erweiterbarkeit**: Weitere Schnittstellen (CLI, gRPC) können einfach eingebunden werden.
- **Fehlerbehandlung**: Einheitliche Struktur für Logging und Error-Codes.

---

## Refactoring-Vorgehen
1. **Use-Case-Funktion** erstellen und bestehende API-Logik dorthin verschieben.
2. **API-Endpunkt** so umbauen, dass er die neue Funktion nutzt (ohne das Verhalten zu ändern).
3. **MCP-Endpunkte** anpassen, sodass sie dieselbe Use-Case-Funktion verwenden.
4. **Tests**:
   - Bestehende API-Tests unverändert lassen (Regressionstest für Stabilität)
   - Neue Tests für MCP-Endpunkte hinzufügen
5. **Schrittweise Migration**:
   - Zuerst API → Use-Case
   - Danach MCP → Use-Case
   - Vermeiden, beide gleichzeitig zu ändern, um Debugging zu erleichtern.

---

