On-Demand Vector Store Sync für File Collections mit verbessertem Markdown-Chunking und benutzergesteuertem Sync-Workflow.

**KERNIDEE:**
- User arbeitet normal mit File Collections (erstellen, bearbeiten, löschen)
- UI zeigt \"Out of Sync\" Status nach Änderungen an
- User triggert manuell \"Sync to Vector Store\" wenn bereit
- Keine automatischen Background-Updates, volle Kontrolle beim User

**VORTEILE gegenüber Auto-Sync:**
- ✅ Performance-freundlich: Batch-Processing statt einzelne Updates
- ✅ Einfache Implementierung: Keine komplexe Event-Systeme
- ✅ User Control: Bewusste Entscheidung wann Vector Store aktualisiert wird
- ✅ Fehlerresistenz: Keine Race Conditions oder Inkonsistenzen durch parallele Updates
- ✅ Iteratives Arbeiten: User kann mehrere Änderungen sammeln, dann einmalig syncen

## EXAMPLES:

### 1. Verbesserter Markdown Content Processor:

```python
import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class MarkdownChunk:
    content: str
    chunk_type: str  # header_section, code_block, list, table, paragraph
    metadata: Dict[str, Any]

class MarkdownContentProcessor:
    \"\"\"Intelligenter Markdown-Processor für technische Dokumentation.\"\"\"
    
    def __init__(self, max_chunk_size: int = 1500, min_chunk_size: int = 100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def process_markdown_content(self, content: str, file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        \"\"\"
        Hauptverarbeitungslogik für Markdown-Content.
        
        Strategie:
        1. Header-basierte Segmentierung als primäre Chunk-Grenzen
        2. Code-Blocks immer komplett zusammenhalten
        3. Listen als semantische Einheiten behandeln
        4. Tabellen nicht aufteilen
        5. API-Dokumentation: Methoden-Beschreibungen zusammenhalten
        \"\"\"
        chunks = []
        
        # 1. Parse Markdown Struktur
        sections = self._parse_markdown_structure(content)
        
        # 2. Intelligente Chunking-Strategie
        for section in sections:
            section_chunks = self._process_section(section, file_metadata)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _parse_markdown_structure(self, content: str) -> List[Dict[str, Any]]:
        \"\"\"Parse Markdown in strukturierte Sektionen.\"\"\"
        lines = content.split('\
')
        sections = []
        current_section = {
            'header': '',
            'header_level': 0,
            'content_lines': [],
            'start_line': 0
        }
        
        for i, line in enumerate(lines):
            # Header-Erkennung
            header_match = re.match(r'^(#{1,6})\\s+(.+)$', line)
            if header_match:
                # Speichere vorherige Sektion
                if current_section['content_lines'] or current_section['header']:
                    current_section['content'] = '\
'.join(current_section['content_lines'])
                    sections.append(current_section.copy())
                
                # Starte neue Sektion
                level = len(header_match.group(1))
                current_section = {
                    'header': header_match.group(2),
                    'header_level': level,
                    'content_lines': [line],  # Header ist Teil des Contents
                    'start_line': i
                }
            else:
                current_section['content_lines'].append(line)
        
        # Letzte Sektion hinzufügen
        if current_section['content_lines']:
            current_section['content'] = '\
'.join(current_section['content_lines'])
            sections.append(current_section)
        
        return sections
    
    def _process_section(self, section: Dict[str, Any], file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        \"\"\"Verarbeite eine Markdown-Sektion in Chunks.\"\"\"
        content = section['content']
        chunks = []
        
        # 1. Code-Block Behandlung
        if self._contains_code_blocks(content):
            chunks.extend(self._process_content_with_code_blocks(content, section, file_metadata))
        
        # 2. Tabellen-Behandlung  
        elif self._contains_tables(content):
            chunks.extend(self._process_content_with_tables(content, section, file_metadata))
        
        # 3. Listen-Behandlung
        elif self._contains_lists(content):
            chunks.extend(self._process_content_with_lists(content, section, file_metadata))
        
        # 4. Standard-Text-Verarbeitung
        else:
            chunks.extend(self._process_standard_text(content, section, file_metadata))
        
        return chunks
    
    def _contains_code_blocks(self, content: str) -> bool:
        \"\"\"Prüfe ob Content Code-Blocks enthält.\"\"\"
        return '```' in content or content.count('    ') > 2  # Indented code blocks
    
    def _process_content_with_code_blocks(self, content: str, section: Dict[str, Any], file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        \"\"\"Verarbeite Content mit Code-Blocks - diese niemals aufteilen.\"\"\"
        chunks = []
        
        # Split by code blocks
        parts = re.split(r'(```[\\s\\S]*?```)', content)
        
        current_chunk_parts = []
        current_size = 0
        
        for part in parts:
            part_size = len(part)
            
            # Code-Block: Immer komplett zusammenhalten
            if part.strip().startswith('```'):
                # Wenn aktueller Chunk + Code-Block zu groß: Finalisiere aktuellen Chunk
                if current_size + part_size > self.max_chunk_size and current_chunk_parts:
                    chunk_content = ''.join(current_chunk_parts).strip()
                    if chunk_content:
                        chunks.append(self._create_chunk(
                            chunk_content, 'text_section', section, file_metadata
                        ))
                    current_chunk_parts = []
                    current_size = 0
                
                # Code-Block hinzufügen
                current_chunk_parts.append(part)
                current_size += part_size
                
                # Code-Block finalisieren
                chunk_content = ''.join(current_chunk_parts).strip()
                chunks.append(self._create_chunk(
                    chunk_content, 'code_section', section, file_metadata, 
                    extra_metadata={'programming_language': self._detect_language(part)}
                ))
                current_chunk_parts = []
                current_size = 0
            
            # Text-Part: Normal verarbeiten
            else:
                if current_size + part_size > self.max_chunk_size and current_chunk_parts:
                    chunk_content = ''.join(current_chunk_parts).strip()
                    if chunk_content:
                        chunks.append(self._create_chunk(
                            chunk_content, 'text_section', section, file_metadata
                        ))
                    current_chunk_parts = []
                    current_size = 0
                
                current_chunk_parts.append(part)
                current_size += part_size
        
        # Finaler Chunk
        if current_chunk_parts:
            chunk_content = ''.join(current_chunk_parts).strip()
            if chunk_content:
                chunks.append(self._create_chunk(
                    chunk_content, 'text_section', section, file_metadata
                ))
        
        return chunks
    
    def _detect_language(self, code_block: str) -> str:
        \"\"\"Erkenne Programmiersprache in Code-Block.\"\"\"
        first_line = code_block.split('\
')[0]
        if '```' in first_line:
            lang = first_line.replace('```', '').strip()
            return lang if lang else 'unknown'
        return 'unknown'
    
    def _create_chunk(self, content: str, chunk_type: str, section: Dict[str, Any], 
                     file_metadata: Dict[str, Any], extra_metadata: Dict[str, Any] = None) -> MarkdownChunk:
        \"\"\"Erstelle einen MarkdownChunk mit vollständigen Metadaten.\"\"\"
        metadata = {
            'collection_name': file_metadata.get('collection_name'),
            'source_file': file_metadata.get('filename'),
            'file_folder': file_metadata.get('folder', ''),
            'chunk_type': chunk_type,
            'header_text': section.get('header', ''),
            'header_level': section.get('header_level', 0),
            'content_length': len(content),
            'word_count': len(content.split()),
            'contains_code': 'code' in chunk_type,
            'last_updated': file_metadata.get('modified_at'),
            'file_hash': self._generate_content_hash(content)
        }
        
        if extra_metadata:
            metadata.update(extra_metadata)
        
        return MarkdownChunk(
            content=content,
            chunk_type=chunk_type,
            metadata=metadata
        )
    
    def _generate_content_hash(self, content: str) -> str:
        \"\"\"Generiere Content Hash für Change Detection.\"\"\"
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    # Weitere Hilfsmethoden...
    def _contains_tables(self, content: str) -> bool:
        return '|' in content and content.count('|') > 4
    
    def _contains_lists(self, content: str) -> bool:
        return bool(re.search(r'^[\\s]*[-*+]\\s', content, re.MULTILINE))
    
    def _process_content_with_tables(self, content: str, section: Dict[str, Any], file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        # Implementation für Tabellen-Verarbeitung
        return [self._create_chunk(content, 'table_section', section, file_metadata)]
    
    def _process_content_with_lists(self, content: str, section: Dict[str, Any], file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        # Implementation für Listen-Verarbeitung  
        return [self._create_chunk(content, 'list_section', section, file_metadata)]
    
    def _process_standard_text(self, content: str, section: Dict[str, Any], file_metadata: Dict[str, Any]) -> List[MarkdownChunk]:
        # Implementation für Standard-Text
        return [self._create_chunk(content, 'text_section', section, file_metadata)]
```

### 2. On-Demand Vector Sync Manager:

```python
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

class OnDemandVectorSyncManager:
    \"\"\"Manager für benutzergesteuerte Vector Store Synchronisation.\"\"\"
    
    def __init__(self, collection_manager, vector_store, markdown_processor):
        self.collection_manager = collection_manager
        self.vector_store = vector_store
        self.markdown_processor = markdown_processor
        self.sync_status = {}  # In-Memory Status, könnte in DB persistiert werden
        self.logger = logging.getLogger(__name__)
    
    def get_collection_sync_status(self, collection_name: str) -> Dict[str, Any]:
        \"\"\"Rufe aktuellen Sync-Status einer Collection ab.\"\"\"
        if collection_name not in self.sync_status:
            # Initialer Status
            self.sync_status[collection_name] = {
                'last_sync': None,
                'files_changed_since_sync': [],
                'vector_store_enabled': False,
                'total_chunks': 0,
                'last_error': None
            }
        
        status = self.sync_status[collection_name].copy()
        
        # Check if vector store collection exists
        vector_collections = self.vector_store.list_collections()
        status['vector_store_exists'] = collection_name in vector_collections
        
        # Calculate status flags
        status['is_out_of_sync'] = len(status['files_changed_since_sync']) > 0
        status['needs_initial_sync'] = not status['vector_store_exists'] and not status['last_sync']
        
        return status
    
    def mark_files_changed(self, collection_name: str, changed_files: List[str]):
        \"\"\"Markiere Files als geändert seit letztem Sync.\"\"\"
        if collection_name not in self.sync_status:
            self.sync_status[collection_name] = {
                'last_sync': None,
                'files_changed_since_sync': [],
                'vector_store_enabled': False,
                'total_chunks': 0
            }
        
        # Füge geänderte Files hinzu (ohne Duplikate)
        current_changed = set(self.sync_status[collection_name]['files_changed_since_sync'])
        current_changed.update(changed_files)
        self.sync_status[collection_name]['files_changed_since_sync'] = list(current_changed)
        
        self.logger.info(f\"Marked {len(changed_files)} files as changed in collection '{collection_name}'\")
    
    def sync_collection_to_vector_store(self, collection_name: str, 
                                       force_full_sync: bool = False) -> Dict[str, Any]:
        \"\"\"
        Hauptfunktion: Sync einer Collection in den Vector Store.
        
        Args:
            collection_name: Name der zu syncenden Collection
            force_full_sync: Wenn True, alle Files neu verarbeiten (nicht nur geänderte)
            
        Returns:
            Dict mit Sync-Ergebnissen
        \"\"\"
        self.logger.info(f\"Starting vector sync for collection '{collection_name}'\")
        
        try:
            # 1. Collection-Files laden
            files_result = self.collection_manager.list_files_in_collection(collection_name)
            if not files_result['success']:
                return {
                    'success': False,
                    'error': f\"Could not load collection files: {files_result['error']}\"
                }
            
            files = files_result['files']
            if not files:
                return {
                    'success': False,
                    'error': 'No files found in collection'
                }
            
            # 2. Bestimme welche Files verarbeitet werden müssen
            files_to_process = files
            if not force_full_sync:
                changed_files = self.sync_status.get(collection_name, {}).get('files_changed_since_sync', [])
                if changed_files:
                    files_to_process = [f for f in files if f['name'] in changed_files]
            
            if not files_to_process:
                return {
                    'success': True,
                    'message': 'No files need processing',
                    'chunks_processed': 0
                }
            
            # 3. Bei Full Sync: Vector Store Collection löschen
            if force_full_sync or not self.sync_status.get(collection_name, {}).get('last_sync'):
                self._clear_vector_store_collection(collection_name)
            
            # 4. Files verarbeiten und chunken
            all_chunks = []
            processed_files = []
            
            for file_info in files_to_process:
                try:
                    file_content_result = self.collection_manager.read_file(
                        collection_name, file_info['name'], file_info.get('folder', '')
                    )
                    
                    if not file_content_result['success']:
                        self.logger.warning(f\"Could not read file {file_info['name']}: {file_content_result['error']}\")
                        continue
                    
                    # Markdown-Processing
                    file_metadata = {
                        'collection_name': collection_name,
                        'filename': file_info['name'],
                        'folder': file_info.get('folder', ''),
                        'size': file_info.get('size', 0),
                        'modified_at': file_info.get('modified_at')
                    }
                    
                    chunks = self.markdown_processor.process_markdown_content(
                        file_content_result['content'], file_metadata
                    )
                    
                    all_chunks.extend(chunks)
                    processed_files.append(file_info['name'])
                    
                    self.logger.debug(f\"Processed file '{file_info['name']}' into {len(chunks)} chunks\")
                    
                except Exception as e:
                    self.logger.error(f\"Error processing file {file_info['name']}: {str(e)}\")
                    continue
            
            if not all_chunks:
                return {
                    'success': False,
                    'error': 'No chunks generated from files'
                }
            
            # 5. Chunks in Vector Store speichern
            vector_result = self._store_chunks_in_vector_store(collection_name, all_chunks)
            if not vector_result['success']:
                return vector_result
            
            # 6. Sync-Status aktualisieren
            self.sync_status[collection_name] = {
                'last_sync': datetime.now().isoformat(),
                'files_changed_since_sync': [],
                'vector_store_enabled': True,
                'total_chunks': len(all_chunks),
                'last_error': None,
                'processed_files': processed_files
            }
            
            self.logger.info(f\"Successfully synced {len(processed_files)} files ({len(all_chunks)} chunks) to vector store\")
            
            return {
                'success': True,
                'chunks_processed': len(all_chunks),
                'files_processed': len(processed_files),
                'collection_name': collection_name,
                'sync_timestamp': self.sync_status[collection_name]['last_sync']
            }
            
        except Exception as e:
            error_msg = f\"Vector sync failed: {str(e)}\"
            self.logger.error(error_msg)
            
            # Fehler in Status speichern
            if collection_name in self.sync_status:
                self.sync_status[collection_name]['last_error'] = error_msg
            
            return {
                'success': False,
                'error': error_msg
            }
    
    def _clear_vector_store_collection(self, collection_name: str):
        \"\"\"Lösche bestehende Vector Store Collection.\"\"\"
        try:
            existing_collections = self.vector_store.list_collections()
            if collection_name in existing_collections:
                self.vector_store.delete_collection(collection_name)
                self.logger.info(f\"Cleared existing vector store collection '{collection_name}'\")
        except Exception as e:
            self.logger.warning(f\"Could not clear vector store collection: {str(e)}\")
    
    def _store_chunks_in_vector_store(self, collection_name: str, chunks: List[MarkdownChunk]) -> Dict[str, Any]:
        \"\"\"Speichere Chunks im Vector Store.\"\"\"
        try:
            # Prepare data for vector store
            documents = [chunk.content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f\"{collection_name}_{i}_{chunk.metadata['file_hash']}\" for i, chunk in enumerate(chunks)]
            
            # Create/get collection
            self.vector_store.get_or_create_collection(collection_name)
            
            # Add documents in batches (für große Collections)
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_meta = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                self.vector_store.add_documents(
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids
                )
                
                self.logger.debug(f\"Stored batch {i//batch_size + 1} ({len(batch_docs)} documents)\")
            
            return {
                'success': True,
                'documents_stored': len(documents)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f\"Vector store operation failed: {str(e)}\"
            }
    
    def remove_collection_from_vector_store(self, collection_name: str) -> Dict[str, Any]:
        \"\"\"Entferne Collection komplett aus Vector Store.\"\"\"
        try:
            self.vector_store.delete_collection(collection_name)
            
            # Status zurücksetzen
            if collection_name in self.sync_status:
                self.sync_status[collection_name] = {
                    'last_sync': None,
                    'files_changed_since_sync': [],
                    'vector_store_enabled': False,
                    'total_chunks': 0
                }
            
            return {
                'success': True,
                'message': f\"Collection '{collection_name}' removed from vector store\"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f\"Failed to remove collection: {str(e)}\"
            }
```

### 3. Integration in Collection Manager:

```python
# Erweitere bestehenden CollectionFileManager
class CollectionFileManager:
    def __init__(self, base_dir: Path = None):
        # ... bestehende Initialisierung
        self.vector_sync_manager = None  # Wird bei Bedarf initialisiert
    
    def enable_vector_sync(self, vector_store, markdown_processor):
        \"\"\"Aktiviere Vector Store Integration.\"\"\"
        self.vector_sync_manager = OnDemandVectorSyncManager(
            collection_manager=self,
            vector_store=vector_store,
            markdown_processor=markdown_processor
        )
    
    def save_file(self, collection_name: str, filename: str, content: str, folder: str = \"\") -> Dict[str, Any]:
        \"\"\"Speichere File und markiere als geändert für Vector Sync.\"\"\"
        # Original save_file Logik
        result = super().save_file(collection_name, filename, content, folder)
        
        # Bei Erfolg: Vector Sync Status aktualisieren
        if result['success'] and self.vector_sync_manager:
            self.vector_sync_manager.mark_files_changed(collection_name, [filename])
        
        return result
    
    def delete_file(self, collection_name: str, filename: str, folder: str = \"\") -> Dict[str, Any]:
        \"\"\"Lösche File und markiere Collection als geändert.\"\"\"
        # Implementiere delete_file falls noch nicht vorhanden
        result = self._delete_file_implementation(collection_name, filename, folder)
        
        if result['success'] and self.vector_sync_manager:
            self.vector_sync_manager.mark_files_changed(collection_name, [filename])
        
        return result
    
    def get_vector_sync_status(self, collection_name: str) -> Dict[str, Any]:
        \"\"\"Rufe Vector Sync Status ab.\"\"\"
        if not self.vector_sync_manager:
            return {'vector_sync_available': False}
        
        status = self.vector_sync_manager.get_collection_sync_status(collection_name)
        status['vector_sync_available'] = True
        return status
    
    def sync_to_vector_store(self, collection_name: str, force_full_sync: bool = False) -> Dict[str, Any]:
        \"\"\"Sync Collection zu Vector Store.\"\"\"
        if not self.vector_sync_manager:
            return {
                'success': False,
                'error': 'Vector sync not enabled'
            }
        
        return self.vector_sync_manager.sync_collection_to_vector_store(
            collection_name, force_full_sync
        )
```

### 4. HTTP API Endpunkte:

```python
# Neue Endpunkte in http_server.py

@app.get(\"/api/file-collections/{collection_name}/vector-status\")
async def get_vector_sync_status(collection_name: str):
    \"\"\"Rufe Vector Sync Status einer Collection ab.\"\"\"
    try:
        status = collection_manager.get_vector_sync_status(collection_name)
        return {\"success\": True, \"status\": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(\"/api/file-collections/{collection_name}/sync-to-vector-store\")
async def sync_collection_to_vector_store(collection_name: str, force_full_sync: bool = False):
    \"\"\"Sync Collection zu Vector Store.\"\"\"
    try:
        result = collection_manager.sync_to_vector_store(collection_name, force_full_sync)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete(\"/api/file-collections/{collection_name}/vector-store\")
async def remove_collection_from_vector_store(collection_name: str):
    \"\"\"Entferne Collection aus Vector Store.\"\"\"
    try:
        if not collection_manager.vector_sync_manager:
            raise HTTPException(status_code=400, detail=\"Vector sync not enabled\")
        
        result = collection_manager.vector_sync_manager.remove_collection_from_vector_store(collection_name)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Integration mit bestehenden RAG Search Endpunkten
@app.get(\"/api/file-collections/{collection_name}/search\")
async def search_collection_vector_store(collection_name: str, query: str, n_results: int = 5):
    \"\"\"Durchsuche Collection Vector Store.\"\"\"
    try:
        if not RAG_AVAILABLE:
            raise HTTPException(status_code=400, detail=\"RAG functionality not available\")
        
        # Check if collection exists in vector store
        status = collection_manager.get_vector_sync_status(collection_name)
        if not status.get('vector_store_exists', False):
            raise HTTPException(
                status_code=400, 
                detail=\"Collection not synced to vector store. Please sync first.\"
            )
        
        # Perform search
        result = await search_knowledge_base(query, collection_name, n_results)
        return json.loads(result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## DOCUMENTATION:

### Bestehende Komponenten:
- **Collection Manager**: `tools/collection_manager.py` - Erweitern mit Vector Sync Integration
- **Vector Store**: `tools/knowledge_base/vector_store.py` - Bestehende API nutzen
- **Content Processor**: `tools/knowledge_base/content_processor.py` - Durch MarkdownContentProcessor ersetzen
- **RAG Tools**: `tools/knowledge_base/rag_tools.py` - Search-Funktionen erweitern
- **HTTP Server**: `http_server.py` - Neue Vector Sync Endpunkte hinzufügen

### Frontend Integration:
- **File Manager UI**: `frontend/src/components/FileManager/` - Sync Status und Button hinzufügen
- **API Service**: `frontend/src/services/api.ts` - Vector Sync API Calls
- **State Management**: Sync Status in Collection State integrieren

### TypeScript Interfaces:
```typescript
interface VectorSyncStatus {
  vector_sync_available: boolean;
  vector_store_exists: boolean;
  last_sync: string | null;
  files_changed_since_sync: string[];
  is_out_of_sync: boolean;
  needs_initial_sync: boolean;
  total_chunks: number;
  last_error: string | null;
}

interface SyncResult {
  success: boolean;
  chunks_processed: number;
  files_processed: number;
  collection_name: string;
  sync_timestamp: string;
  error?: string;
}
```

## OTHER CONSIDERATIONS:

### **IMPLEMENTIERUNGSREIHENFOLGE:**

**Phase 1: Intelligentes Chunking (2-3 Tage)**
1. MarkdownContentProcessor implementieren
2. Unit Tests für verschiedene Markdown-Strukturen
3. A/B Test gegen bestehenden RecursiveCharacterTextSplitter
4. Performance-Benchmarks für große Files

**Phase 2: Vector Sync Backend (3-4 Tage)**
1. OnDemandVectorSyncManager implementieren
2. Integration in CollectionFileManager
3. HTTP API Endpunkte
4. Error Handling und Logging
5. Integration Tests

**Phase 3: Frontend Integration (2-3 Tage)**
1. Sync Status UI Komponenten
2. \"Sync to Vector Store\" Button
3. Progress-Anzeige für große Collections
4. Error-Handling im UI
5. Search Integration im File Manager

### **PERFORMANCE ÜBERLEGUNGEN:**

- **Große Collections**: Batch-Processing für Vector Store Updates
- **Progress Tracking**: Für lange Sync-Operationen
- **Memory Management**: Stream-Processing für sehr große Files
- **Caching**: Content Hash für Change Detection

### **ERROR HANDLING:**

- **Partial Failures**: Wenn einzelne Files fehlschlagen, andere weiter verarbeiten
- **Rollback**: Bei Vector Store Fehlern Status nicht als \"synced\" markieren
- **User Feedback**: Klare Error Messages im UI
- **Retry Logic**: Für transiente Vector Store Fehler

### **TESTING STRATEGIE:**

```python
# Unit Tests für MarkdownContentProcessor
def test_code_block_preservation():
    content = \"\"\"
# Header
Some text
```python
def example():
    pass
```
More text
\"\"\"
    chunks = processor.process_markdown_content(content, {})
    code_chunks = [c for c in chunks if c.chunk_type == 'code_section']
    assert len(code_chunks) == 1
    assert 'def example():' in code_chunks[0].content

# Integration Tests für Vector Sync
def test_full_sync_workflow():
    # 1. Create collection with files
    # 2. Trigger sync
    # 3. Verify vector store contents
    # 4. Modify files
    # 5. Check out-of-sync status
    # 6. Re-sync and verify updates
```

### **SICHERHEITSÜBERLEGUNGEN:**

- **File Size Limits**: Schutz vor Memory-Exhaustion bei riesigen Files
- **Rate Limiting**: Verhindere Spam von Sync-Requests
- **Validation**: Sichere alle Collection/File Namen
- **Resource Monitoring**: Vector Store Speicherplatz überwachen
