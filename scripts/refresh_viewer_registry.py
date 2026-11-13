"""Refresh public and ignored local viewer registries before Parcel starts."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.export_web import write_registry

if __name__ == '__main__':
    write_registry(ROOT / 'viewer/src/data', ROOT / 'viewer/src/datasetRegistry.js')
