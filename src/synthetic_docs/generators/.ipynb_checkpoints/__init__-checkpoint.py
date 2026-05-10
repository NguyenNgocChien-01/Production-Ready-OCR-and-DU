# generators/__init__.py
from .medicare import MedicareGenerator
from .passport import PassportGenerator
from .driver_licence import DriverLicenceGenerator
from .base import DocumentGenerator, GeneratedDoc

_REGISTRY = {
    "medicare": MedicareGenerator,
    "driver_licence":  DriverLicenceGenerator,
    "passport": PassportGenerator,
}

ALL_TYPES = list(_REGISTRY.keys())


def get_generator(doc_type: str, **kwargs):
    if doc_type not in _REGISTRY:
        raise ValueError(f"Unknown doc_type '{doc_type}'. Available: {ALL_TYPES}")
    return _REGISTRY[doc_type](**kwargs)