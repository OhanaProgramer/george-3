"""Tailnet node discovery.

Purpose: Report visible Tailscale nodes as structured data.
Phase: Tailscale Discovery v1.
Last updated: 2026-05-31.
Notes: Read-only inventory; does not ping or control nodes.
"""

from __future__ import annotations

import json

from modules.tailscale.tailscale_status import (
    clean_error,
    is_tailscale_installed,
    run_command,
)


def load_tailnet_status(command_runner=run_command):
    if not is_tailscale_installed():
        return {
            "ok": False,
            "message": "Tailscale is not installed.",
            "self": None,
            "nodes": [],
        }

    result = command_runner(["tailscale", "status", "--json"])

    if result.returncode != 0:
        return {
            "ok": False,
            "message": clean_error(result.stderr) or "Tailscale is installed but not responding.",
            "self": None,
            "nodes": [],
        }

    try:
        raw_status = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "message": "Tailscale returned node data George could not read.",
            "self": None,
            "nodes": [],
        }

    return build_tailnet_inventory(raw_status)


def build_tailnet_inventory(raw_status):
    self_node = normalize_node(raw_status.get("Self", {}), is_self=True)
    peers = raw_status.get("Peer", {}) or {}
    peer_nodes = [normalize_node(peer, is_self=False) for peer in peers.values()]
    nodes = sorted([self_node, *peer_nodes], key=node_sort_key)
    online_count = sum(1 for node in nodes if node["online"])

    return {
        "ok": True,
        "message": "Tailnet node inventory loaded.",
        "backend_state": raw_status.get("BackendState", "unknown"),
        "tailnet": raw_status.get("CurrentTailnet", {}).get("Name", "unknown"),
        "self": self_node,
        "nodes": nodes,
        "node_count": len(nodes),
        "online_count": online_count,
        "offline_count": len(nodes) - online_count,
    }


def normalize_node(raw_node, is_self):
    ips = raw_node.get("TailscaleIPs") or []
    return {
        "name": raw_node.get("HostName") or raw_node.get("DNSName") or "unknown",
        "dns_name": raw_node.get("DNSName") or "",
        "os": raw_node.get("OS") or "unknown",
        "tailscale_ips": ips,
        "primary_ip": ips[0] if ips else None,
        "online": bool(raw_node.get("Online")),
        "active": bool(raw_node.get("Active")),
        "is_self": is_self,
        "last_seen": raw_node.get("LastSeen") or "",
    }


def node_sort_key(node):
    return (not node["is_self"], not node["online"], node["name"].lower())


def format_node_line(node):
    flags = []

    if node["is_self"]:
        flags.append("self")
    flags.append("online" if node["online"] else "offline")

    ip = node["primary_ip"] or "no ip"
    os_name = node["os"]
    flag_text = ", ".join(flags)

    return f"- {node['name']} | {ip} | {os_name} | {flag_text}"


def format_tailnet_summary(inventory):
    if not inventory["ok"]:
        return "\n".join(["George 3 Tailnet Nodes", f"OK: no", f"Message: {inventory['message']}"])

    lines = [
        "George 3 Tailnet Nodes",
        f"Tailnet: {inventory['tailnet']}",
        f"Backend state: {inventory['backend_state']}",
        f"Nodes: {inventory['node_count']} total, {inventory['online_count']} online, {inventory['offline_count']} offline",
        "",
        "Nodes:",
    ]

    lines.extend(format_node_line(node) for node in inventory["nodes"])
    return "\n".join(lines)


def main():
    print(format_tailnet_summary(load_tailnet_status()))


if __name__ == "__main__":
    main()
