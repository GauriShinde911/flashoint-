from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class StorageInterface(ABC):
    """Abstract interface for local SQLite and cloud Firestore backends."""

    @abstractmethod
    def save_citizen_request(self, request_data: Dict[str, Any]) -> str:
        """Save a single citizen request, returns ID."""
        pass

    @abstractmethod
    def get_citizen_requests(
        self,
        limit: int = 100,
        category: Optional[str] = None,
        admin2: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve citizen requests with optional category/district filters."""
        pass

    @abstractmethod
    def save_infrastructure_facility(self, facility_data: Dict[str, Any]) -> str:
        """Save an infrastructure facility record."""
        pass

    @abstractmethod
    def get_infrastructure_facilities(
        self,
        admin2: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve facilities by district/category."""
        pass

    @abstractmethod
    def save_government_project(self, project_data: Dict[str, Any]) -> str:
        """Save a public project record."""
        pass

    @abstractmethod
    def get_government_projects(
        self,
        admin2: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve government projects."""
        pass

    @abstractmethod
    def save_demographics(self, demo_data: Dict[str, Any]) -> str:
        """Save or update district demographics."""
        pass

    @abstractmethod
    def get_demographics(self, admin2: str) -> Optional[Dict[str, Any]]:
        """Retrieve demographics for a district."""
        pass

    @abstractmethod
    def record_dataset_version(self, version_data: Dict[str, Any]) -> str:
        """Record dataset ingestion version lineage."""
        pass

    @abstractmethod
    def get_dataset_versions(self) -> List[Dict[str, Any]]:
        """List all tracked dataset versions."""
        pass
