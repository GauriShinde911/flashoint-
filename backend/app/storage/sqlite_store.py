import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from backend.app.storage.base import StorageInterface

DEFAULT_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../data/dpi_local.db")
)

class SQLiteStore(StorageInterface):
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_tables()

    from contextlib import contextmanager

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citizen_requests (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    admin2 TEXT,
                    data_quality TEXT,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS infrastructure_facilities (
                    facility_id TEXT PRIMARY KEY,
                    category TEXT,
                    admin2 TEXT,
                    data_quality TEXT,
                    payload TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS government_projects (
                    project_id TEXT PRIMARY KEY,
                    category TEXT,
                    admin2 TEXT,
                    status TEXT,
                    data_quality TEXT,
                    payload TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS demographics (
                    region_id TEXT PRIMARY KEY,
                    admin2 TEXT,
                    payload TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dataset_versions (
                    dataset_id TEXT PRIMARY KEY,
                    version TEXT,
                    payload TEXT,
                    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_citizen_request(self, request_data: Dict[str, Any]) -> str:
        req_id = request_data["id"]
        cat = request_data.get("category", "")
        admin2 = request_data.get("admin_hierarchy", {}).get("admin2", "")
        quality = request_data.get("data_quality", "synthetic")
        payload = json.dumps(request_data, ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO citizen_requests (id, category, admin2, data_quality, payload) VALUES (?, ?, ?, ?, ?)",
                (req_id, cat, admin2, quality, payload)
            )
            conn.commit()
        return req_id

    def get_citizen_requests(
        self,
        limit: int = 100,
        category: Optional[str] = None,
        admin2: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT payload FROM citizen_requests WHERE 1=1"
        params: list = []
        if category:
            query += " AND category = ?"
            params.append(category)
        if admin2:
            query += " AND admin2 = ?"
            params.append(admin2)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [json.loads(row["payload"]) for row in rows]

    def save_infrastructure_facility(self, facility_data: Dict[str, Any]) -> str:
        fac_id = facility_data["facility_id"]
        cat = facility_data.get("category", "")
        admin2 = facility_data.get("admin_hierarchy", {}).get("admin2", "")
        quality = facility_data.get("data_quality", "real")
        payload = json.dumps(facility_data, ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO infrastructure_facilities (facility_id, category, admin2, data_quality, payload) VALUES (?, ?, ?, ?, ?)",
                (fac_id, cat, admin2, quality, payload)
            )
            conn.commit()
        return fac_id

    def get_infrastructure_facilities(
        self,
        admin2: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT payload FROM infrastructure_facilities WHERE 1=1"
        params: list = []
        if admin2:
            query += " AND admin2 = ?"
            params.append(admin2)
        if category:
            query += " AND category = ?"
            params.append(category)
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [json.loads(row["payload"]) for row in rows]

    def save_government_project(self, project_data: Dict[str, Any]) -> str:
        p_id = project_data["project_id"]
        cat = project_data.get("category", "")
        admin2 = project_data.get("admin_hierarchy", {}).get("admin2", "")
        status = project_data.get("status", "Ongoing")
        quality = project_data.get("data_quality", "real")
        payload = json.dumps(project_data, ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO government_projects (project_id, category, admin2, status, data_quality, payload) VALUES (?, ?, ?, ?, ?, ?)",
                (p_id, cat, admin2, status, quality, payload)
            )
            conn.commit()
        return p_id

    def get_government_projects(
        self,
        admin2: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT payload FROM government_projects WHERE 1=1"
        params: list = []
        if admin2:
            query += " AND admin2 = ?"
            params.append(admin2)
        if status:
            query += " AND status = ?"
            params.append(status)
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [json.loads(row["payload"]) for row in rows]

    def save_demographics(self, demo_data: Dict[str, Any]) -> str:
        reg_id = demo_data["region_id"]
        admin2 = demo_data.get("admin_hierarchy", {}).get("admin2", "")
        payload = json.dumps(demo_data, ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO demographics (region_id, admin2, payload) VALUES (?, ?, ?)",
                (reg_id, admin2, payload)
            )
            conn.commit()
        return reg_id

    def get_demographics(self, admin2: str) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT payload FROM demographics WHERE admin2 = ? LIMIT 1",
                (admin2,)
            ).fetchone()
            return json.loads(row["payload"]) if row else None

    def record_dataset_version(self, version_data: Dict[str, Any]) -> str:
        d_id = version_data["dataset_id"]
        ver = version_data.get("version", "1.0")
        payload = json.dumps(version_data, ensure_ascii=False)
        with self._connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO dataset_versions (dataset_id, version, payload) VALUES (?, ?, ?)",
                (d_id, ver, payload)
            )
            conn.commit()
        return d_id

    def get_dataset_versions(self) -> List[Dict[str, Any]]:
        with self._connection() as conn:
            rows = conn.execute("SELECT payload FROM dataset_versions ORDER BY ingested_at DESC").fetchall()
            return [json.loads(row["payload"]) for row in rows]
