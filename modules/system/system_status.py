"""System status discovery.

Purpose: Report local machine, node, path, and resource state.
Phase: System Discovery v1.
Last updated: 2026-05-31.
Notes: Read-only status; does not manage processes or services.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from datetime import datetime, timezone

from config import settings


def get_system_status(
    memory_reader=None,
    disk_reader=None,
    cpu_reader=None,
    cwd_reader=None,
    timestamp_reader=None,
):
    memory_reader = memory_reader or get_memory_total_gb
    disk_reader = disk_reader or get_project_disk_gb
    cpu_reader = cpu_reader or os.cpu_count
    cwd_reader = cwd_reader or os.getcwd
    timestamp_reader = timestamp_reader or utc_timestamp

    disk_total_gb, disk_free_gb = safe_pair(disk_reader)

    return {
        "node": {
            "name": settings.GEORGE_NODE_NAME,
            "role": settings.GEORGE_NODE_ROLE,
            "environment": settings.GEORGE_ENV,
            "log_level": settings.GEORGE_LOG_LEVEL,
        },
        "host": {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.platform(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
        },
        "resources": {
            "cpu_count": cpu_reader() or 0,
            "memory_total_gb": memory_reader(),
            "disk_total_gb": disk_total_gb,
            "disk_free_gb": disk_free_gb,
        },
        "paths": {
            "cwd": cwd_reader(),
            "project_root": str(settings.PROJECT_ROOT),
        },
        "timestamp": timestamp_reader(),
    }


def get_memory_total_gb():
    if sys.platform != "darwin":
        return None

    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        physical_pages = os.sysconf("SC_PHYS_PAGES")
    except (AttributeError, OSError, ValueError):
        return None

    return bytes_to_gb(page_size * physical_pages)


def get_project_disk_gb():
    try:
        usage = shutil.disk_usage(settings.PROJECT_ROOT)
    except OSError:
        return None, None

    return bytes_to_gb(usage.total), bytes_to_gb(usage.free)


def bytes_to_gb(value):
    return round(value / (1024**3), 2)


def safe_pair(reader):
    value = reader()

    if not value:
        return None, None

    return value


def utc_timestamp():
    return datetime.now(timezone.utc).isoformat()


def format_system_summary(status):
    node = status["node"]
    host = status["host"]
    resources = status["resources"]
    paths = status["paths"]

    return "\n".join(
        [
            "George 3 System Status",
            f"Node: {node['name']} ({node['role']}, {node['environment']})",
            f"Host: {host['hostname']}",
            f"OS: {host['os']} {host['os_version']}",
            f"Architecture: {host['architecture']}",
            f"Python: {host['python_version']}",
            f"CPU count: {resources['cpu_count']}",
            f"Memory total GB: {format_optional(resources['memory_total_gb'])}",
            f"Disk total GB: {format_optional(resources['disk_total_gb'])}",
            f"Disk free GB: {format_optional(resources['disk_free_gb'])}",
            f"CWD: {paths['cwd']}",
            f"Project root: {paths['project_root']}",
            f"Timestamp: {status['timestamp']}",
        ]
    )


def format_optional(value):
    return "not available" if value is None else str(value)


def main():
    print(format_system_summary(get_system_status()))


if __name__ == "__main__":
    main()
