"""
FilesystemMetadataReconciler - Handles reconciliation between filesystem state and metadata.

Detects and handles external changes to filesystem-based collection content:
- New files added externally
- Files modified externally (via content hash comparison)
- Files deleted externally
- Updates vector sync status appropriately (not_synced for changes)
"""

import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, NamedTuple
import logging

logger = logging.getLogger(__name__)


class FileInfo(NamedTuple):
    """Information about a file in the filesystem."""
    path: str  # Relative path from collection root
    content_hash: str
    size: int
    modified_time: datetime


class ReconciliationResult(NamedTuple):
    """Result of reconciliation operation."""
    files_added: int
    files_modified: int
    files_deleted: int
    actions: List[Dict[str, Any]]
    
    @property
    def has_changes(self) -> bool:
        """Check if any changes were detected."""
        return self.files_added > 0 or self.files_modified > 0 or self.files_deleted > 0


class FilesystemMetadataReconciler:
    """Handles reconciliation between filesystem state and metadata database."""
    
    # Security: Allowed file extensions (consistent with FilesystemCollectionManager)
    ALLOWED_EXTENSIONS = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv'}
    
    def __init__(self, filesystem_base: Path, metadata_store):
        """
        Initialize filesystem reconciler.
        
        Args:
            filesystem_base: Base directory for filesystem content
            metadata_store: FilesystemMetadataStore instance
        """
        self.fs_base = Path(filesystem_base)
        self.metadata_store = metadata_store
        
        logger.info(f"FilesystemMetadataReconciler initialized: {filesystem_base}")
    
    async def reconcile_collection(self, collection_name: str) -> ReconciliationResult:
        """
        Reconcile filesystem with metadata database for a collection.
        
        Args:
            collection_name: Name of the collection to reconcile
            
        Returns:
            ReconciliationResult with details of changes detected
        """
        try:
            logger.debug(f"Starting reconciliation for collection '{collection_name}'")
            
            # 1. Scan filesystem for actual files
            fs_files = await self._scan_filesystem_files(collection_name)
            logger.debug(f"Found {len(fs_files)} files in filesystem for '{collection_name}'")
            
            # 2. Get current metadata from database
            db_metadata_result = await self.metadata_store.get_collection_files(collection_name)
            
            if not db_metadata_result.get("success", False):
                logger.warning(f"Failed to get metadata for collection '{collection_name}': {db_metadata_result.get('error')}")
                return ReconciliationResult(0, 0, 0, [])
            
            db_files = {f["file_path"]: f for f in db_metadata_result.get("files", [])}
            logger.debug(f"Found {len(db_files)} files in metadata for '{collection_name}'")
            
            # 3. Detect differences
            fs_file_paths = {f.path for f in fs_files}
            db_file_paths = set(db_files.keys())
            
            new_files = fs_file_paths - db_file_paths
            deleted_files = db_file_paths - fs_file_paths
            potential_modified_files = fs_file_paths & db_file_paths
            
            # 4. Process changes
            reconciliation_actions = []
            
            # NEW FILES: In filesystem but not in database
            for file_path in new_files:
                fs_file = next(f for f in fs_files if f.path == file_path)
                await self._handle_new_file(collection_name, fs_file, reconciliation_actions)
            
            # DELETED FILES: In database but not in filesystem
            for file_path in deleted_files:
                await self._handle_deleted_file(collection_name, file_path, reconciliation_actions)
            
            # POTENTIALLY MODIFIED FILES: Compare content hashes
            modified_count = 0
            for file_path in potential_modified_files:
                fs_file = next(f for f in fs_files if f.path == file_path)
                db_file = db_files[file_path]
                
                if await self._handle_potentially_modified_file(collection_name, fs_file, db_file, reconciliation_actions):
                    modified_count += 1
            
            # 5. Log reconciliation
            result = ReconciliationResult(
                files_added=len(new_files),
                files_modified=modified_count,
                files_deleted=len(deleted_files),
                actions=reconciliation_actions
            )
            
            if result.has_changes:
                await self.metadata_store.log_reconciliation(
                    collection_name=collection_name,
                    actions=reconciliation_actions,
                    files_added=result.files_added,
                    files_modified=result.files_modified,
                    files_deleted=result.files_deleted
                )
                
                logger.info(f"Reconciliation completed for '{collection_name}': "
                          f"+{result.files_added} ~{result.files_modified} -{result.files_deleted}")
            else:
                logger.debug(f"No changes detected for collection '{collection_name}'")
            
            return result
            
        except Exception as e:
            logger.error(f"Reconciliation failed for collection '{collection_name}': {e}")
            return ReconciliationResult(0, 0, 0, [])
    
    async def _scan_filesystem_files(self, collection_name: str) -> List[FileInfo]:
        """
        Scan filesystem directory for files in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of FileInfo objects for files found
        """
        collection_path = self.fs_base / collection_name
        
        if not collection_path.exists() or not collection_path.is_dir():
            logger.debug(f"Collection directory does not exist: {collection_path}")
            return []
        
        files = []
        
        try:
            # Recursively scan for files
            for file_path in collection_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip hidden files and metadata files
                if file_path.name.startswith('.'):
                    continue
                
                # Check file extension
                if not self._is_allowed_file(file_path):
                    continue
                
                # Get relative path from collection root
                relative_path = file_path.relative_to(collection_path)
                
                # Calculate file info
                try:
                    content = file_path.read_text(encoding='utf-8')
                    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                    size = len(content.encode('utf-8'))
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime, timezone.utc)
                    
                    files.append(FileInfo(
                        path=str(relative_path),
                        content_hash=content_hash,
                        size=size,
                        modified_time=modified_time
                    ))
                    
                except Exception as e:
                    logger.warning(f"Failed to process file {file_path}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to scan collection directory {collection_path}: {e}")
            return []
        
        return files
    
    async def _handle_new_file(self, collection_name: str, fs_file: FileInfo, actions: List[Dict[str, Any]]):
        """
        Handle a new file found in filesystem but not in metadata.
        
        Args:
            collection_name: Name of the collection
            fs_file: FileInfo for the new file
            actions: List to append reconciliation actions to
        """
        try:
            # Add to metadata database with "not_synced" status
            result = await self.metadata_store.update_file_metadata(
                collection_name=collection_name,
                file_path=fs_file.path,
                content_hash=fs_file.content_hash,
                file_size=fs_file.size,
                vector_sync_status="not_synced"  # User must manually sync
            )
            
            if result.get("success", False):
                actions.append({
                    "action": "added_to_metadata",
                    "file": fs_file.path,
                    "reason": "New file detected in filesystem",
                    "content_hash": fs_file.content_hash,
                    "size": fs_file.size
                })
                logger.debug(f"Added new file to metadata: {collection_name}/{fs_file.path}")
            else:
                logger.error(f"Failed to add new file to metadata: {result.get('error')}")
                actions.append({
                    "action": "failed_to_add",
                    "file": fs_file.path,
                    "reason": f"Metadata update failed: {result.get('error')}"
                })
                
        except Exception as e:
            logger.error(f"Error handling new file {fs_file.path}: {e}")
            actions.append({
                "action": "error",
                "file": fs_file.path,
                "reason": f"Exception during processing: {str(e)}"
            })
    
    async def _handle_deleted_file(self, collection_name: str, file_path: str, actions: List[Dict[str, Any]]):
        """
        Handle a file that exists in metadata but not in filesystem.
        
        Args:
            collection_name: Name of the collection
            file_path: Path of the deleted file
            actions: List to append reconciliation actions to
        """
        try:
            # Remove from metadata database
            result = await self.metadata_store.delete_file_metadata(collection_name, file_path)
            
            if result.get("success", False):
                actions.append({
                    "action": "removed_from_metadata",
                    "file": file_path,
                    "reason": "File no longer exists in filesystem"
                })
                logger.debug(f"Removed deleted file from metadata: {collection_name}/{file_path}")
            else:
                logger.error(f"Failed to remove deleted file from metadata: {result.get('error')}")
                actions.append({
                    "action": "failed_to_remove",
                    "file": file_path,
                    "reason": f"Metadata removal failed: {result.get('error')}"
                })
                
        except Exception as e:
            logger.error(f"Error handling deleted file {file_path}: {e}")
            actions.append({
                "action": "error",
                "file": file_path,
                "reason": f"Exception during processing: {str(e)}"
            })
    
    async def _handle_potentially_modified_file(self, collection_name: str, fs_file: FileInfo, 
                                               db_file: Dict[str, Any], actions: List[Dict[str, Any]]) -> bool:
        """
        Handle a file that exists in both filesystem and metadata - check for modifications.
        
        Args:
            collection_name: Name of the collection
            fs_file: FileInfo from filesystem
            db_file: File metadata from database
            actions: List to append reconciliation actions to
            
        Returns:
            True if file was modified, False otherwise
        """
        try:
            current_hash = fs_file.content_hash
            stored_hash = db_file.get("content_hash", "")
            
            if current_hash != stored_hash:
                # File was modified externally
                previous_status = db_file.get("vector_sync_status", "not_synced")
                new_status = "not_synced"  # Always goes back to not_synced when modified
                
                result = await self.metadata_store.update_file_metadata(
                    collection_name=collection_name,
                    file_path=fs_file.path,
                    content_hash=current_hash,
                    file_size=fs_file.size,
                    vector_sync_status=new_status,
                    source_url=db_file.get("source_url")  # Preserve source URL if it exists
                )
                
                if result.get("success", False):
                    actions.append({
                        "action": "detected_modification",
                        "file": fs_file.path,
                        "reason": f"Content hash changed: {stored_hash[:8]} -> {current_hash[:8]}",
                        "previous_sync_status": previous_status,
                        "new_sync_status": new_status,
                        "size_change": fs_file.size - db_file.get("file_size", 0)
                    })
                    logger.debug(f"Detected modification: {collection_name}/{fs_file.path}")
                    return True
                else:
                    logger.error(f"Failed to update modified file metadata: {result.get('error')}")
                    actions.append({
                        "action": "failed_to_update",
                        "file": fs_file.path,
                        "reason": f"Metadata update failed: {result.get('error')}"
                    })
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling potentially modified file {fs_file.path}: {e}")
            actions.append({
                "action": "error",
                "file": fs_file.path,
                "reason": f"Exception during processing: {str(e)}"
            })
            return False
    
    def _is_allowed_file(self, file_path: Path) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file extension is allowed, False otherwise
        """
        return file_path.suffix.lower() in self.ALLOWED_EXTENSIONS
    
    async def get_collection_sync_summary(self, collection_name: str) -> Dict[str, Any]:
        """
        Get sync status summary for a collection after reconciliation.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with sync status summary
        """
        try:
            # Get all files with their sync status
            files_result = await self.metadata_store.get_collection_files(collection_name)
            
            if not files_result.get("success", False):
                return {
                    "success": False,
                    "error": files_result.get("error", "Failed to get collection files")
                }
            
            files = files_result.get("files", [])
            
            # Count files by sync status
            status_counts = {
                "not_synced": 0,
                "syncing": 0,
                "synced": 0,
                "sync_error": 0
            }
            
            for file in files:
                status = file.get("vector_sync_status", "not_synced")
                if status in status_counts:
                    status_counts[status] += 1
            
            # Determine overall collection status
            if status_counts["not_synced"] > 0:
                overall_status = "has_unsynced_files"
                sync_available = True
            elif status_counts["syncing"] > 0:
                overall_status = "sync_in_progress"
                sync_available = False
            elif status_counts["sync_error"] > 0:
                overall_status = "has_sync_errors"
                sync_available = True
            else:
                overall_status = "fully_synced"
                sync_available = False
            
            # Get last reconciliation info
            last_reconciliation = await self.metadata_store.get_last_reconciliation(collection_name)
            
            return {
                "success": True,
                "collection_name": collection_name,
                "overall_status": overall_status,
                "status_counts": status_counts,
                "sync_available": sync_available,
                "total_files": sum(status_counts.values()),
                "last_reconciliation": last_reconciliation
            }
            
        except Exception as e:
            logger.error(f"Failed to get sync summary for collection '{collection_name}': {e}")
            return {
                "success": False,
                "error": str(e)
            }