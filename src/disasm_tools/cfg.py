"""Build inter-procedural call graph from NFS ROM disassembly output.

Constructs a networkx DiGraph where nodes are subroutines and edges
represent JSR/JMP call relationships. Supports JSON node-link and
Graphviz DOT output, plus queries (leaves, roots, depth, sub detail).
"""

import bisect
import json
import sys
from pathlib import Path

import networkx as nx

# Memory regions: subroutines only extend within their region
MEMORY_REGIONS = [
    (0x0016, 0x0076),   # zero page workspace
    (0x0400, 0x04FF),   # relocated page 4
    (0x0500, 0x05FF),   # relocated page 5
    (0x0600, 0x06FF),   # relocated page 6
    (0x0D00, 0x0DFF),   # NMI workspace
    (0x8000, 0x9FFF),   # ROM
]


def _region_for_addr(addr):
    """Return the memory region (start, end) containing addr, or None."""
    for start, end in MEMORY_REGIONS:
        if start <= addr <= end:
            return (start, end)
    return None


def build_call_graph(json_filepath):
    """Build a networkx DiGraph from the py8dis JSON output.

    Nodes represent subroutines (internal and external OS entry points).
    Edges represent JSR (call) and JMP (tail-call) relationships.
    """
    data = json.loads(Path(json_filepath).read_text())
    items = data["items"]
    raw_subs = data.get("subroutines", [])
    external_labels = data.get("external_labels", {})

    # addr → subroutine (all, including OS stubs)
    addr_to_sub = {s["addr"]: s for s in raw_subs}

    # Invert external_labels: addr → name (for OS calls not in subroutines)
    ext_addr_to_name = {v: k for k, v in external_labels.items()}

    # ROM subroutines sorted by address (exclude OS stubs for extent computation)
    rom_subs = sorted(
        [s for s in raw_subs if s["addr"] < 0xFF00],
        key=lambda s: s["addr"],
    )

    # Compute subroutine extent boundaries
    sub_extents = {}
    for idx, sub in enumerate(rom_subs):
        sub_addr = sub["addr"]
        sub_region = _region_for_addr(sub_addr)
        extent_end = None
        for j in range(idx + 1, len(rom_subs)):
            if _region_for_addr(rom_subs[j]["addr"]) == sub_region:
                extent_end = rom_subs[j]["addr"]
                break
        sub_extents[sub_addr] = (sub_addr, extent_end)

    rom_sub_addrs = [s["addr"] for s in rom_subs]

    def containing_sub_addr(item_addr):
        """Find the subroutine entry address containing item_addr."""
        idx = bisect.bisect_right(rom_sub_addrs, item_addr) - 1
        if idx < 0:
            return None
        sub_addr = rom_sub_addrs[idx]
        if _region_for_addr(item_addr) != _region_for_addr(sub_addr):
            return None
        _, extent_end = sub_extents[sub_addr]
        if extent_end is not None and item_addr >= extent_end:
            return None
        return sub_addr

    # Build graph
    G = nx.DiGraph()

    # Add ROM subroutine nodes
    for sub in rom_subs:
        G.add_node(
            f"0x{sub['addr']:04X}",
            name=sub.get("name", f"sub_c{sub['addr']:04x}"),
            title=sub.get("title", ""),
            external=False,
        )

    # Accumulate edge data: (source_id, target_id) → {call_sites, types}
    edge_data = {}

    for item in items:
        mnemonic = item.get("mnemonic")
        if mnemonic not in ("jsr", "jmp"):
            continue

        target = item.get("target")
        if target is None:
            continue

        source_sub = containing_sub_addr(item["addr"])
        if source_sub is None:
            continue

        source_id = f"0x{source_sub:04X}"

        # Resolve target to a graph node
        if target in addr_to_sub:
            target_id = f"0x{target:04X}"
            target_sub = addr_to_sub[target]

            # Skip intra-procedural JMPs (loops within same subroutine)
            if mnemonic == "jmp" and target_id == source_id:
                continue

            if not G.has_node(target_id):
                G.add_node(
                    target_id,
                    name=target_sub.get("name", f"sub_c{target:04x}"),
                    title=target_sub.get("title", ""),
                    external=target >= 0xFF00,
                )

        elif target >= 0xFF00:
            # External OS call not in subroutines list
            target_id = f"0x{target:04X}"
            if not G.has_node(target_id):
                name = ext_addr_to_name.get(target, f"os_{target:04x}")
                G.add_node(target_id, name=name, title="", external=True)
        else:
            continue

        key = (source_id, target_id)
        if key not in edge_data:
            edge_data[key] = {"call_sites": [], "types": set()}
        edge_data[key]["call_sites"].append(f"0x{item['addr']:04X}")
        edge_data[key]["types"].add(mnemonic)

    # Add edges
    for (source_id, target_id), edata in edge_data.items():
        edge_type = "jsr" if "jsr" in edata["types"] else "jmp"
        G.add_edge(
            source_id, target_id,
            call_sites=sorted(edata["call_sites"]),
            type=edge_type,
        )

    return G


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_json(G):
    """Output the graph in node-link JSON format."""
    data = nx.node_link_data(G)
    print(json.dumps(data, indent=2))


def format_dot(G):
    """Output the graph in Graphviz DOT format."""
    print("digraph call_graph {")
    print("  rankdir=LR;")
    print('  node [shape=box, fontname=monospace, fontsize=10];')
    print('  edge [fontname=monospace, fontsize=8];')
    print()

    for node_id in sorted(G.nodes):
        attrs = G.nodes[node_id]
        name = attrs.get("name", node_id)
        dot_attrs = [f'label="{name}"']
        if attrs.get("external"):
            dot_attrs.extend(["style=dashed", "color=gray"])
        print(f'  "{node_id}" [{", ".join(dot_attrs)}];')

    print()

    for source, target, data in sorted(G.edges(data=True)):
        edge_attrs = []
        if data.get("type") == "jmp":
            edge_attrs.append("style=dashed")
        sites = data.get("call_sites", [])
        if len(sites) > 1:
            edge_attrs.append(f'label="{len(sites)}"')
        attr_str = f" [{', '.join(edge_attrs)}]" if edge_attrs else ""
        print(f'  "{source}" -> "{target}"{attr_str};')

    print("}")


def format_leaves(G):
    """List leaf subroutines (out_degree=0, make no calls)."""
    internal = []
    external = []
    for node_id in sorted(G.nodes):
        if G.out_degree(node_id) == 0:
            attrs = G.nodes[node_id]
            if attrs.get("external"):
                external.append((node_id, attrs))
            else:
                internal.append((node_id, attrs))

    print(f"Leaf subroutines ({len(internal)} internal, "
          f"{len(external)} external):\n")
    print(f"{'ADDR':<9s} {'NAME':<32s} {'IN_DEG':>6s}  TITLE")
    print(f"{'----':<9s} {'----':<32s} {'------':>6s}  -----")

    for node_id, attrs in internal:
        name = attrs.get("name", node_id)[:31]
        title = attrs.get("title", "")[:40]
        in_deg = G.in_degree(node_id)
        print(f"{node_id:<9s} {name:<32s} {in_deg:>6d}  {title}")

    if external:
        print(f"\nExternal ({len(external)}):")
        for node_id, attrs in external:
            name = attrs.get("name", node_id)[:31]
            in_deg = G.in_degree(node_id)
            print(f"{node_id:<9s} {name:<32s} {in_deg:>6d}")


def format_roots(G):
    """List root subroutines (in_degree=0, not called by others)."""
    roots = [
        (nid, G.nodes[nid])
        for nid in sorted(G.nodes)
        if G.in_degree(nid) == 0 and not G.nodes[nid].get("external")
    ]

    if not roots:
        print("No root subroutines found.")
        return

    print(f"Root subroutines ({len(roots)}, in_degree=0):\n")
    print(f"{'ADDR':<9s} {'NAME':<32s} {'OUT_DEG':>7s}  TITLE")
    print(f"{'----':<9s} {'----':<32s} {'-------':>7s}  -----")

    for node_id, attrs in roots:
        name = attrs.get("name", node_id)[:31]
        title = attrs.get("title", "")[:40]
        out_deg = G.out_degree(node_id)
        print(f"{node_id:<9s} {name:<32s} {out_deg:>7d}  {title}")


def _resolve_sub(G, target):
    """Resolve a target string (hex address or name) to a node ID."""
    clean = target.strip().lstrip("$&").removeprefix("0x")
    try:
        addr = int(clean, 16)
        node_id = f"0x{addr:04X}"
        if G.has_node(node_id):
            return node_id
    except ValueError:
        pass

    # Exact name match
    for nid in G.nodes:
        if G.nodes[nid].get("name") == target:
            return nid

    # Partial name match
    matches = [nid for nid in G.nodes if target in G.nodes[nid].get("name", "")]
    if len(matches) == 1:
        return matches[0]
    if matches:
        print(f"Ambiguous name '{target}', matches:", file=sys.stderr)
        for nid in matches:
            print(f"  {nid} {G.nodes[nid].get('name', '?')}", file=sys.stderr)
    else:
        print(f"Subroutine '{target}' not found", file=sys.stderr)
    return None


def format_sub(G, target):
    """Show callers and callees of a specific subroutine."""
    node_id = _resolve_sub(G, target)
    if node_id is None:
        return

    attrs = G.nodes[node_id]
    name = attrs.get("name", node_id)
    title = attrs.get("title", "")

    print(f"{name} ({node_id})")
    if title:
        print(f"  {title}")
    print(f"  in_degree={G.in_degree(node_id)}, "
          f"out_degree={G.out_degree(node_id)}")

    # Callers
    callers = sorted(G.predecessors(node_id))
    if callers:
        print(f"\n  Called by ({len(callers)}):")
        for pred in callers:
            edge = G.edges[pred, node_id]
            cname = G.nodes[pred].get("name", pred)
            sites = edge.get("call_sites", [])
            etype = edge.get("type", "jsr")
            suffix = f" [{etype.upper()}]" if etype != "jsr" else ""
            plural = "s" if len(sites) != 1 else ""
            print(f"    {pred} {cname} ({len(sites)} site{plural}){suffix}")
    else:
        print(f"\n  Called by: none (root)")

    # Callees
    callees = sorted(G.successors(node_id))
    if callees:
        print(f"\n  Calls ({len(callees)}):")
        for succ in callees:
            edge = G.edges[node_id, succ]
            cname = G.nodes[succ].get("name", succ)
            sites = edge.get("call_sites", [])
            etype = edge.get("type", "jsr")
            ext = " [external]" if G.nodes[succ].get("external") else ""
            suffix = f" [{etype.upper()}]" if etype != "jsr" else ""
            plural = "s" if len(sites) != 1 else ""
            print(f"    {succ} {cname} "
                  f"({len(sites)} site{plural}){suffix}{ext}")
    else:
        print(f"\n  Calls: none (leaf)")


def format_depth(G):
    """Show subroutines sorted by call depth from leaves.

    Depth 0 = leaf (no outgoing calls to internal subroutines).
    Depth N = 1 + max depth of callees.
    Cycles are collapsed via strongly-connected component condensation.
    """
    internal = {n for n in G.nodes if not G.nodes[n].get("external")}
    H = G.subgraph(internal).copy()

    cycles = list(nx.simple_cycles(H))

    if nx.is_directed_acyclic_graph(H):
        depths = {}
        for node in reversed(list(nx.topological_sort(H))):
            succs = list(H.successors(node))
            depths[node] = 1 + max(depths[s] for s in succs) if succs else 0
    else:
        condensation = nx.condensation(H)
        mapping = condensation.graph["mapping"]
        scc_depths = {}
        for scc_node in reversed(list(nx.topological_sort(condensation))):
            succs = list(condensation.successors(scc_node))
            scc_depths[scc_node] = (
                1 + max(scc_depths[s] for s in succs) if succs else 0
            )
        depths = {node: scc_depths[mapping[node]] for node in internal}

    if cycles:
        print(f"Note: {len(cycles)} cycle(s) detected "
              f"(collapsed via SCC condensation).\n")

    sorted_nodes = sorted(depths.items(), key=lambda x: (-x[1], x[0]))
    max_depth = max(depths.values()) if depths else 0

    print(f"{'DEPTH':>5s}  {'ADDR':<9s} {'NAME':<32s} "
          f"{'OUT':>3s} {'IN':>3s}  TITLE")
    print(f"{'-----':>5s}  {'----':<9s} {'----':<32s} "
          f"{'---':>3s} {'--':>3s}  -----")

    for node_id, depth in sorted_nodes:
        attrs = G.nodes[node_id]
        name = attrs.get("name", node_id)[:31]
        title = attrs.get("title", "")[:35]
        out_deg = G.out_degree(node_id)
        in_deg = G.in_degree(node_id)
        print(f"{depth:>5d}  {node_id:<9s} {name:<32s} "
              f"{out_deg:>3d} {in_deg:>3d}  {title}")

    print(f"\nMax depth: {max_depth}, "
          f"{len(depths)} internal subroutines")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def cfg(version_dirpath, version, fmt="json", leaves=False, roots=False,
        sub=None, depth=False):
    """Main entry point. Returns exit code."""
    from disasm_tools.paths import rom_prefix
    pfx = rom_prefix(version_dirpath)
    json_filepath = version_dirpath / "output" / f"{pfx}-{version}.json"

    if not json_filepath.exists():
        print(f"Error: {json_filepath} not found (run disassemble first)",
              file=sys.stderr)
        return 1

    G = build_call_graph(json_filepath)

    if leaves:
        format_leaves(G)
    elif roots:
        format_roots(G)
    elif sub:
        format_sub(G, sub)
    elif depth:
        format_depth(G)
    elif fmt == "dot":
        format_dot(G)
    else:
        format_json(G)

    return 0
