# Frontend Anpassungen für neue Vector API

## Überblick der API-Änderungen

Die Vector Sync API wurde grundlegend überarbeitet für bessere REST-Konformität und vereinfachtes Design.

## 🚨 Breaking Changes

### 1. HTTP Status Codes geändert
**Vorher**: Alle Responses waren 200, Fehler in `success: false`
**Jetzt**: RESTful Status Codes

| Szenario | Alt | Neu | Action Required |
|----------|-----|-----|-----------------|
| Collection nicht gefunden | 200 + `success: false` | **404** | Error-Handling anpassen |
| Ungültige Parameter | 200 + `success: false` | **400** | Validation-Errors abfangen |
| RAG nicht verfügbar | 200 + `success: false` | **503** | Service-Unavailable behandeln |
| Sync-Fehler | 200 + `success: false` | **500** | Server-Errors unterscheiden |

### 2. Error Response Format geändert
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

### 3. Endpoints entfernt
**Diese Endpoints existieren nicht mehr:**
- ❌ `POST /api/vector-sync/collections/{name}/enable`
- ❌ `POST /api/vector-sync/collections/{name}/disable`

**Grund**: Vereinfachung - Sync erfolgt nur noch manuell, keine automatischen Trigger.

## 📋 Erforderliche Frontend-Änderungen

### 1. APIService.ts anpassen

```typescript
// ENTFERNEN: Diese Methoden nicht mehr verfügbar
// async enableCollectionSync(collectionName: string)
// async disableCollectionSync(collectionName: string)

// ANPASSEN: Error-Handling für alle vector-sync Methoden
async syncCollection(collectionName: string, options?: SyncOptions) {
  try {
    const response = await fetch(`/api/vector-sync/collections/${collectionName}/sync`, {
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
const handleSync = async (collectionName: string) => {
  try {
    setLoading(true);
    await apiService.syncCollection(collectionName);
    setSuccess('Sync completed successfully');
  } catch (error) {
    if (error instanceof CollectionNotFoundError) {
      setError('Collection not found - it may have been deleted');
    } else if (error instanceof ServiceUnavailableError) {
      setError('Vector search is not available. Please install RAG dependencies.');
    } else if (error instanceof SyncFailedError) {
      setError(`Sync failed: ${error.message}`);
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
- `POST /api/vector-sync/collections/{name}/sync` - Manual sync trigger
- `GET /api/vector-sync/collections/{name}/status` - Get sync status
- `GET /api/vector-sync/collections/statuses` - Get all statuses  
- `POST /api/vector-sync/search` - Semantic search
- `DELETE /api/vector-sync/collections/{name}/vectors` - Delete all vectors

### Error Codes
- `COLLECTION_NOT_FOUND` (404) - Collection existiert nicht
- `MISSING_QUERY` (400) - Query-Parameter fehlt
- `INVALID_LIMIT` (400) - Limit-Parameter ungültig
- `INVALID_THRESHOLD` (400) - Similarity-Threshold ungültig
- `SERVICE_UNAVAILABLE` (503) - RAG-Dependencies nicht installiert
- `SYNC_FAILED` (500) - Technischer Sync-Fehler

## 🚀 Migration-Strategie

1. **Phase 1**: Error-Handling anpassen (kritisch)
2. **Phase 2**: Enable/Disable UI entfernen  
3. **Phase 3**: Success-Messages anpassen
4. **Phase 4**: Testing und Bugfixes

**Zeitaufwand**: ~2-3 Stunden für vollständige Anpassung