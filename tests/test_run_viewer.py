"""Launcher cache isolation and failure propagation."""
from pathlib import Path
from unittest.mock import Mock

import run_viewer


def test_launch_uses_fresh_cache_and_returns_child_status(monkeypatch, tmp_path):
    monkeypatch.setattr('sys.argv', ['run_viewer.py'])
    monkeypatch.setattr(run_viewer, 'DERIVATIVE_ROOT', tmp_path / 'absent')
    server = Mock()
    monkeypatch.setattr(run_viewer, 'make_server', lambda: server)
    monkeypatch.setattr(run_viewer.threading, 'Thread', Mock())
    caches = []

    def popen(command, cwd):
        cache = Path(command[command.index('--cache-dir') + 1])
        assert cache.is_dir()
        assert cwd == Path(run_viewer.__file__).resolve().parent / 'viewer'
        caches.append(cache)
        return Mock(wait=Mock(return_value=7), poll=Mock(return_value=7))

    monkeypatch.setattr(run_viewer.subprocess, 'Popen', popen)
    assert run_viewer.main() == 7
    assert run_viewer.main() == 7
    assert caches[0] != caches[1]
    assert all(not cache.exists() for cache in caches)
    assert server.shutdown.call_count == 2
    assert server.server_close.call_count == 2
