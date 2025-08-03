## FEATURE:

Migration von File-basiertem Collection Storage zu SQLite-basiertem Storage für bessere Performance, ACID-Transaktionen und erweiterte Query-Funktionen.

## EXAMPLES:

- Bestehende File Collections (`~/.crawl4ai/collections/collection_name/`) sollen in SQLite DB migriert werden
- API-Endpunkte (`/api/file-collections/*`) behalten identische Interfaces 
- Frontend File Explorer und Editor funktionieren unverändert
- Beispiel DB-Schema:
  ```sql
  CREATE TABLE collections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP,
    file_count INTEGER DEFAULT 0
  );
  
  CREATE TABLE files (
    id TEXT PRIMARY KEY, 
    collection_id TEXT REFERENCES collections(id),
    filename TEXT NOT NULL,
    folder_path TEXT DEFAULT '',
    content TEXT,
    content_hash TEXT,
    created_at TIMESTAMP,
    source_url TEXT
  );
  ```

## DOCUMENTATION:

- **SQLite Python Docs**: https://docs.python.org/3/library/sqlite3.html
- **Bestehende Collection Manager**: `tools/collection_manager.py` - alle Methoden müssen DB-kompatibel werden
- **HTTP API**: `http_server.py` - File Collection Endpunkte (Zeilen 200-400)
- **Frontend API Service**: `frontend/src/services/api.ts` - FileCollection API calls
- **Pydantic Models**: `tools/collection_manager.py` - CollectionMetadata, FileMetadata
- **Tests**: `tests/test_collection_manager.py` - alle Tests müssen weiterhin passieren

## OTHER CONSIDERATIONS:

- **Backward Compatibility**: Migration-Script für bestehende File Collections
- **Database Location**: Konsistent mit bisheriger Strategie (`~/.crawl4ai/collections.db` mit temp fallback)
- **ACID Requirements**: Alle File-Operationen müssen transaktional sein
- **Schema Migrations**: Zukünftige DB-Schema-Updates vorbereiten
- **Security**: Path traversal Schutz muss in DB-Queries übertragen werden  
- **Performance**: Indizes für häufige Queries (collection_id, filename, folder_path)
- **Content Storage**: Large text content direkt in DB vs. hybrid approach evaluieren
- **Connection Management**: Connection pooling für FastAPI HTTP server
- **Error Handling**: SQLite-spezifische Errors in API Error Format übersetzen
- **Testing Strategy**: Alle bestehenden Tests müssen passieren + neue DB-spezifische Tests
- **Rollback Plan**: Möglichkeit DB zurück zu Files zu migrieren falls Probleme auftreten