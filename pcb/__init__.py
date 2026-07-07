"""Design-Aware Population Conformal Bands.

Public API:
    from pcb import dapcb          # safe adaptive design-aware conformal band
"""
from .dapcb import dapcb, DapcbResult

__all__ = ["dapcb", "DapcbResult"]
