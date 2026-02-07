"""CLI adapters package for monocli.

Provides detection and registry for available CLI tools.
"""

from monocli.adapters.detection import CLIDetector, DetectionRegistry, DetectionResult

__all__ = ["CLIDetector", "DetectionRegistry", "DetectionResult"]
