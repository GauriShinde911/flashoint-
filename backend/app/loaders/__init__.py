"""
Data loaders package for real and synthetic public datasets.
"""

from backend.app.loaders.hospital_loader import load_hospitals
from backend.app.loaders.health_centre_loader import load_health_centres
from backend.app.loaders.demographics_loader import load_demographics
from backend.app.loaders.synthetic_requests_loader import load_synthetic_requests
from backend.app.loaders.projects_loader import load_government_projects

__all__ = [
    "load_hospitals",
    "load_health_centres",
    "load_demographics",
    "load_synthetic_requests",
    "load_government_projects",
]
