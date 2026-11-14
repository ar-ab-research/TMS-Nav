#!/usr/bin/env python3
"""Start the local MRI/EEG API and the existing Parcel viewer together."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import threading
from src.viewer_service import make_server
from src.subject_ingest import DERIVATIVE_ROOT, VIEWER_ROOT, _export_viewer


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-only',action='store_true',help='Run API only (Parcel is already running)')
    args=parser.parse_args()
    if not args.api_only and DERIVATIVE_ROOT.exists():
        for manifest in sorted(DERIVATIVE_ROOT.glob('*/manifest.json')):
            if not manifest.parent.name.startswith('.'):
                _export_viewer(manifest.parent.name, manifest.parent, VIEWER_ROOT)
    server=make_server()
    threading.Thread(target=server.serve_forever,daemon=True).start()
    print('MRI/EEG API: http://127.0.0.1:8765; viewer: http://127.0.0.1:1234',flush=True)
    process=None
    try:
        if args.api_only:
            threading.Event().wait()
        else:
            # Parcel's persisted graph can retain imports from older checkouts.
            # Keep caching within this session without reusing that stale graph.
            with tempfile.TemporaryDirectory(prefix='tms-viewer-parcel-') as cache:
                process=subprocess.Popen(
                    ['npm','run','dev','--','--host','127.0.0.1','--cache-dir',cache],
                    cwd=Path(__file__).resolve().parent/'viewer')
                try:
                    return process.wait()
                finally:
                    if process.poll() is None:
                        process.terminate()
                        process.wait(timeout=10)
    except KeyboardInterrupt: pass
    finally:
        if process and process.poll() is None:
            process.terminate(); process.wait(timeout=10)
        server.shutdown(); server.server_close()


if __name__=='__main__': raise SystemExit(main())
