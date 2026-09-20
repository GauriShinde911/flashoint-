import os
from backend.app.storage.base import StorageInterface
from backend.app.storage.sqlite_store import SQLiteStore

_storage_instance = None

def get_storage() -> StorageInterface:
    global _storage_instance
    if _storage_instance is None:
        backend = os.getenv("STORAGE_BACKEND", "sqlite").lower()
        if backend == "sqlite":
            _storage_instance = SQLiteStore()
        else:
            # Fallback to SQLite
            _storage_instance = SQLiteStore()
    return _storage_instance
