# Frontend Anpassungen für neue Vector API

## Überblick der API-Änderungen

Die Vector Sync API wurde grundlegend überarbeitet für bessere REST-Konformität und vereinfachtes Design.

## 🚨 Breaking Changes

### 1. Collection ID Konsistenz eingeführt
**Vorher**: Gemischte Verwendung von `collection_name` und `collection_id` in verschiedenen Endpoints
**Jetzt**: **Einheitlich `collection_id` überall** - `name` dient als eindeutige ID

| Endpoint-Typ | Vorher | Jetzt | Action Required |
|--------------|--------|-------|-----------------|
| File Collections | `collection_id` | `collection_id` ✅ | Keine Änderung |
| Vector Sync | `collection_name` | **`collection_id`** | **Frontend URLs anpassen** |
| Response Format | Nur `name` | **`id` + `name`** | **Response-Parsing erweitern** |

### 2. HTTP Status Codes geändert
**Vorher**: Alle Responses waren 200, Fehler in `success: false`
**Jetzt**: RESTful Status Codes

| Szenario | Alt | Neu | Action Required |
|----------|-----|-----|-----------------|
| Collection nicht gefunden | 200 + `success: false` | **404** | Error-Handling anpassen |
| Ungültige Parameter | 200 + `success: false` | **400** | Validation-Errors abfangen |
| Ungültige Dateierweiterung | 200 + `success: false` | **500** | File-Upload Validation |
| RAG nicht verfügbar | 200 + `success: false` | **503** | Service-Unavailable behandeln |
| Sync-Fehler | 200 + `success: false` | **500** | Server-Errors unterscheiden |

### 3. Error Response Format geändert
**Vorher:**
```json
{
  "success": false,
  "error": "Simple error message"
}
```

**Jetzt:**
```json
{
  "detail": {
    "error": {
      "code": "COLLECTION_NOT_FOUND",
      "message": "Collection 'xyz' does not exist",
      "details": {
        "collection_name": "xyz"
      }
    }
  }
}
```

### 4. Endpoints entfernt
**Diese Endpoints existieren nicht mehr:**
- ❌ `POST /api/vector-sync/collections/{name}/enable`
- ❌ `POST /api/vector-sync/collections/{name}/disable`

**Grund**: Vereinfachung - Sync erfolgt nur noch manuell, keine automatischen Trigger.

## 📋 Erforderliche Frontend-Änderungen

### 1. APIService.ts anpassen

#### A) Collection Response Format erweitern
```typescript
// NEU: Collections haben jetzt ein 'id' Feld
interface Collection {
  id: string;          // Eindeutige ID (gleich wie name)
  name: string;        // Collection Name  
  description: string;
  file_count: number;
  created_at: string;
  updated_at: string;
  metadata: object;
}

// Alle Collection-API Calls geben jetzt 'id' zurück:
const collection = await apiService.createCollection(name, description);
console.log(collection.id); // Funktioniert jetzt!
```

#### B) Vector Sync URLs anpassen
```typescript
// ÄNDERN: Alle Vector-Sync URLs verwenden jetzt collection_id
// Vorher: /api/vector-sync/collections/{collection_name}/sync
// Jetzt:  /api/vector-sync/collections/{collection_id}/sync

async syncCollection(collectionId: string, options?: SyncOptions) {
  const response = await fetch(`/api/vector-sync/collections/${collectionId}/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options || {})
  });
  // ...rest unchanged
}

async getCollectionSyncStatus(collectionId: string) {
  return fetch(`/api/vector-sync/collections/${collectionId}/status`);
}

async deleteCollectionVectors(collectionId: string) {
  return fetch(`/api/vector-sync/collections/${collectionId}/vectors`, {
    method: 'DELETE'
  });
}
```

#### C) Error-Handling erweitern
```typescript
// ENTFERNEN: Diese Methoden nicht mehr verfügbar
// async enableCollectionSync(collectionName: string)
// async disableCollectionSync(collectionName: string)

// ANPASSEN: Error-Handling für alle APIs (nicht nur vector-sync)
async syncCollection(collectionId: string, options?: SyncOptions) {
  try {
    const response = await fetch(`/api/vector-sync/collections/${collectionId}/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(options || {})
    });
    
    // NEU: Status-Code-basiertes Error-Handling
    if (!response.ok) {
      const errorData = await response.json();
      const error = errorData.detail?.error;
      
      switch (response.status) {
        case 404:
          throw new CollectionNotFoundError(error?.message || 'Collection not found');
        case 503:
          throw new ServiceUnavailableError(error?.message || 'Vector service unavailable');
        case 500:
          throw new SyncFailedError(error?.message || 'Sync failed');
        default:
          throw new APIError(`HTTP ${response.status}: ${error?.message || 'Unknown error'}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    // Handle network errors, etc.
    throw error;
  }
}
```

// NEU: Auch File-Upload Errors abfangen
async createFileInCollection(collectionId: string, filename: string, content: string) {
  try {
    const response = await fetch(`/api/file-collections/${collectionId}/files`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename, content })
    });
    
    if (!response.ok) {
      switch (response.status) {
        case 404:
          throw new CollectionNotFoundError('Collection not found');
        case 500:
          const error = await response.json();
          if (error.detail?.includes('extension not allowed')) {
            throw new InvalidFileExtensionError('Invalid file extension. Only .md, .txt, .json allowed');
          }
          throw new APIError('Server error');
      }
    }
    
    return await response.json();
  } catch (error) {
    throw error;
  }
}
```

### 2. Error-Klassen definieren

```typescript
// Neue Error-Klassen für spezifische Fälle
export class CollectionNotFoundError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CollectionNotFoundError';
  }
}

export class ServiceUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ServiceUnavailableError';
  }
}

export class SyncFailedError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'SyncFailedError';
  }
}

export class InvalidFileExtensionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'InvalidFileExtensionError';
  }
}
```

### 3. UI-Komponenten anpassen

#### Enable/Disable Buttons entfernen
```tsx
// ENTFERNEN: Diese UI-Elemente
// <button onClick={() => enableSync(collection.name)}>Enable Sync</button>
// <button onClick={() => disableSync(collection.name)}>Disable Sync</button>

// ERSETZEN mit:
<button onClick={() => triggerManualSync(collection.name)}>
  Sync Now (Manual)
</button>
```

#### Error-Handling in Components
```tsx
// ÄNDERN: Parameter von collectionName zu collectionId
const handleSync = async (collectionId: string) => {
  try {
    setLoading(true);
    await apiService.syncCollection(collectionId);
    setSuccess('Sync completed successfully');
  } catch (error) {
    if (error instanceof CollectionNotFoundError) {
      setError('Collection not found - it may have been deleted');
    } else if (error instanceof ServiceUnavailableError) {
      setError('Vector search is not available. Please install RAG dependencies.');
    } else if (error instanceof SyncFailedError) {
      setError(`Sync failed: ${error.message}`);
    } else if (error instanceof InvalidFileExtensionError) {
      setError(`File upload failed: ${error.message}`);
    } else {
      setError('An unexpected error occurred');
    }
  } finally {
    setLoading(false);
  }
};
```

### 4. Status-Anzeige vereinfachen

**Vorher**: Collections hatten `enabled/disabled` Status
**Jetzt**: Collections haben nur noch Sync-Status (`never_synced`, `completed`, `error`)

```tsx
// ENTFERNEN: enabled/disabled Logik
// const isEnabled = collection.is_enabled;

// VEREINFACHEN: Status-Display
const getSyncStatus = (collection: Collection) => {
  switch (collection.sync_status) {
    case 'never_synced': return 'Not synced yet';
    case 'completed': return 'Synced';
    case 'error': return 'Sync failed';
    default: return 'Unknown';
  }
};
```

## 🎯 Testing-Checkliste

### Manual Testing
- [ ] Collection sync mit existierender Collection → 200 + sync result
- [ ] Collection sync mit nicht-existenter Collection → 404 + error
- [ ] Search mit leerer Query → 400 + validation error
- [ ] Search mit ungültigem Limit → 400 + validation error
- [ ] Alle Operations wenn RAG nicht verfügbar → 503 + service error

### Error-Handling Testing
- [ ] 404-Fehler werden korrekt angezeigt
- [ ] 503-Fehler zeigen "Service nicht verfügbar" Message
- [ ] 500-Fehler werden als "Sync failed" behandelt
- [ ] Enable/Disable Buttons wurden entfernt
- [ ] Manuelle Sync-Buttons funktionieren

## 📝 Neue API-Dokumentation

### Verfügbare Endpoints (nach Änderungen)
#### Collection Management (konsistente collection_id)
- `GET /api/file-collections` - List all collections
- `POST /api/file-collections` - Create collection → **Response enthält jetzt `id` Feld**
- `GET /api/file-collections/{collection_id}` - Get collection info
- `DELETE /api/file-collections/{collection_id}` - Delete collection

#### File Management (RESTful Status Codes)
- `GET /api/file-collections/{collection_id}/files` - List files (404 if collection not found)
- `POST /api/file-collections/{collection_id}/files` - Create file (404/500 errors)
- `GET /api/file-collections/{collection_id}/files/{filename}` - Get file (404 errors)
- `PUT /api/file-collections/{collection_id}/files/{filename}` - Update file (404 errors)
- `DELETE /api/file-collections/{collection_id}/files/{filename}` - Delete file (404 errors)

#### Vector Sync (URL Parameter geändert zu collection_id)
- `POST /api/vector-sync/collections/{collection_id}/sync` - Manual sync trigger
- `GET /api/vector-sync/collections/{collection_id}/status` - Get sync status
- `GET /api/vector-sync/collections/statuses` - Get all statuses  
- `POST /api/vector-sync/search` - Semantic search
- `DELETE /api/vector-sync/collections/{collection_id}/vectors` - Delete all vectors

### Error Codes
- `COLLECTION_NOT_FOUND` (404) - Collection existiert nicht
- `MISSING_QUERY` (400) - Query-Parameter fehlt
- `INVALID_LIMIT` (400) - Limit-Parameter ungültig
- `INVALID_THRESHOLD` (400) - Similarity-Threshold ungültig
- `SERVICE_UNAVAILABLE` (503) - RAG-Dependencies nicht installiert
- `SYNC_FAILED` (500) - Technischer Sync-Fehler

## 🚀 Migration-Strategie

### Priorisierung der Änderungen:

1. **Phase 1 (KRITISCH)**: Collection ID Konsistenz
   - [ ] Collection Interface um `id` Feld erweitern
   - [ ] Vector-Sync URLs auf `collection_id` umstellen
   - [ ] API-Calls entsprechend anpassen
   - **Ohne diese Änderungen funktioniert Vector Sync nicht mehr!**

2. **Phase 2 (HOCH)**: RESTful Error-Handling
   - [ ] Status-Code-basiertes Error-Handling implementieren
   - [ ] File-Upload Validation für Extensions hinzufügen
   - [ ] Error-Klassen definieren und verwenden

3. **Phase 3 (MITTEL)**: UI-Verbesserungen
   - [ ] Enable/Disable UI entfernen  
   - [ ] Success-Messages anpassen
   - [ ] Error-Messages verbessern

4. **Phase 4 (NIEDRIG)**: Testing und Bugfixes
   - [ ] Manuelle Tests der neuen Error-Handling
   - [ ] Regression-Tests für Collection ID Änderungen

**Zeitaufwand**: 
- **Phase 1**: ~2-3 Stunden (kritisch)
- **Phase 2**: ~1-2 Stunden  
- **Phase 3+4**: ~1-2 Stunden

**Total**: ~4-7 Stunden für vollständige Migration