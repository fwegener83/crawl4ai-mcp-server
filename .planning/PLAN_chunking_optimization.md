# Full-Stack Feature Plan: Chunking Optimization

## Planning Overview
- **Input**: .planning/INITIAL_chunking_optimization.md
- **Branch**: feature/chunking_optimization
- **Complexity Score**: 7/15 (Einfach bis Moderat)
- **Test Strategy**: Essential Test-First Development
- **Generated**: 2025-01-21 15:00:00 CET

## Phase 1: Deep Exploration Results

### Problem Analysis
**Kern-Problem**: Trotz Konfiguration von `distiluse-base-multilingual-cased-v1` in der .env werden deutsche Queries gegen englische Doku sehr schlecht beantwortet (Threshold unter 0.1 nötig). Im Notebook funktioniert dasselbe Setup perfekt (0.919 cross-language similarity).

**Vermutung**: Das System lädt immer noch das alte `all-MiniLM-L6-v2` Modell, obwohl die Konfiguration geändert wurde.

### Context Research Findings
- **SentenceTransformers**: Modelle werden gecacht, alte Modelle können "hängenbleiben"
- **ChromaDB**: Embeddings sind an das Modell gebunden - Modelländerung erfordert Re-embedding
- **Multilingual Models**: `distiluse-base-multilingual-cased-v1` hat 512 Dimensionen vs. 384 bei MiniLM

## Phase 2: Realistic Complexity Assessment

### Backend Complexity: 2/5 (Einfach)
- Model loading debugging und fix
- Einfache API endpoints für model info
- Collection cleanup workflow erweitern

### Frontend Complexity: 2/5 (Einfach)  
- Display components für model info
- Enhanced sync button mit force option
- Integration in bestehende UX

### Integration Complexity: 3/5 (Moderat)
- Root cause debugging kann tricky sein
- Model consistency zwischen chunking und query

### Total Score: 7/15 (Einfach bis Moderat)

### Selected Test Strategy: Essential Test-First Development
**Fokus auf kritische Pfade**: Model loading, force resync, cleanup workflow
**Coverage Target**: 75% - konzentriert auf neue/geänderte Funktionalität

## Implementation Roadmap

### Phase 1: Root Cause Investigation & Model Fix
**Priorität: Hoch - Das ist der Hauptfehler**

#### Task 1: Model Loading Debugging
```python
# Test: Verify actual loaded model
def test_embedding_service_loads_correct_model():
    service = EmbeddingService()
    assert service.model_name == "distiluse-base-multilingual-cased-v1"
    assert service.model.get_sentence_embedding_dimension() == 512

# Implementation: Enhanced logging in embeddings.py
logger.info(f"Loading model: {self.model_name}")
logger.info(f"Model dimensions: {self.model.get_sentence_embedding_dimension()}")
```

#### Task 2: Cache Clearing & Model Consistency
```python
# Clear old model cache if needed
# Verify .env propagation through unified_server.py
# Ensure embeddings.py uses correct config
```

### Phase 2: Enhanced Vector Operations
**Priorität: Hoch - User braucht force resync**

#### Task 3: Force Resync API
```python
# Backend: Enhanced sync endpoint
POST /api/vector-sync/collections/{name}/force-resync
{
  "delete_existing_vectors": true,
  "chunking_strategy": "auto" 
}

# Test: Force resync deletes all vectors first
def test_force_resync_deletes_existing_vectors():
    # Add some vectors
    # Call force resync 
    # Verify all old vectors gone, new ones created
```

#### Task 4: Collection Cleanup Fix
```python
# Backend: Enhanced collection deletion
async def delete_collection_cascade(collection_name: str):
    # 1. Delete all files in collection
    # 2. Delete all vectors in ChromaDB  
    # 3. Delete collection metadata
    # 4. Handle partial failure scenarios

# Test: Collection deletion removes everything
def test_delete_collection_removes_files_and_vectors():
    # Create collection with files and vectors
    # Delete collection
    # Verify files gone, vectors gone, metadata gone
```

### Phase 3: Frontend Visibility & Controls
**Priorität: Mittel - UX improvement**

#### Task 5: Model Info Display
```tsx
// Frontend: Simple model info component
interface ModelInfo {
  name: string;
  dimensions: number;
  device: string;
  loaded_at: string;
}

// Component: ModelInfoDisplay
const ModelInfoDisplay = ({ modelInfo }: { modelInfo: ModelInfo }) => {
  return (
    <Box>
      <Typography variant="body2">
        Active Model: {modelInfo.name} ({modelInfo.dimensions}D)
      </Typography>
      <Chip label={modelInfo.device} size="small" />
    </Box>
  );
};
```

#### Task 6: Enhanced Sync Controls  
```tsx
// Frontend: Force resync option
const EnhancedSyncButton = ({ collectionId, onSync, onForceSync }) => {
  return (
    <ButtonGroup>
      <Button onClick={onSync}>Sync</Button>
      <Button 
        onClick={onForceSync}
        color="warning"
        startIcon={<WarningIcon />}
      >
        Force Resync
      </Button>
    </ButtonGroup>
  );
};
```

### Phase 4: Integration & Validation
**Priorität: Hoch - Verify fix works**

#### Task 7: End-to-End Validation
```python
# Test: German query quality improvement
def test_german_query_improved_results():
    # Sync collection with new model
    # Query: "Welche verschiedenen Arten von Speicher gibt es in Claude Code?"
    # Assert similarity > 0.5 (instead of current < 0.1)
```

## Simple API Changes

### New Backend Endpoints (Minimal)
```python
# GET /api/vector-sync/model-info
{
  "model_name": "distiluse-base-multilingual-cased-v1",
  "dimensions": 512,
  "device": "cpu",
  "loaded_at": "2025-01-21T15:00:00Z"
}

# POST /api/vector-sync/collections/{name}/force-resync
# DELETE /api/collections/{name} (enhanced to cleanup vectors)
```

### Frontend Changes (Minimal)
```tsx
// Add to existing CollectionSidebar:
<ModelInfoDisplay />

// Enhance existing CollectionSyncButton:
<EnhancedSyncControls />
```

## Success Criteria (Realistic)
1. **Deutsche Queries funktionieren**: Similarity > 0.5 statt < 0.1
2. **Korrektes Modell geladen**: Frontend zeigt `distiluse-base-multilingual-cased-v1`  
3. **Force Resync funktioniert**: User kann alle Chunks löschen und neu syncen
4. **Collection Cleanup funktioniert**: Löschen entfernt files UND vectors
5. **UX Integration**: Neue Features fügen sich natürlich in bestehende UI ein

## Risk Mitigation (Pragmatisch)
- **Model Loading Fail**: Fallback auf default model mit Error message
- **ChromaDB Issues**: Graceful error handling, retry logic
- **Partial Cleanup Fail**: Log errors, continue with what's possible

## Dependencies (Minimal)
- Existing RAG dependencies already installed
- Current collection management system works
- ChromaDB instance running

## Execution Instructions
```bash
/execute .planning/PLAN_chunking_optimization.md
```

**Key Principle**: Fix the core model loading issue first, then add user-facing improvements. Keep it simple and focused on the actual requirements.

**Estimate**: 2-3 days implementation + testing, not weeks.