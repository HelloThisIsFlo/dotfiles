#!/usr/bin/env python3
"""BFS the Obsidian graph from seed zettels via the `obsidian eval` CLI.

Returns the depth-stratified zettel neighborhood as JSON.

Usage:
    neighborhood.py [--depth N] [--vault NAME] SEED [SEED ...]

Seeds: vault-relative paths (e.g. `_ZK_/Zettel/Foo.md`) or basenames /
wikilink-style names (e.g. `Foo`, `Having a system we can trust`). Names
resolve by basename match against all markdown files in the vault.

Filters: only includes notes under `_ZK_/Zettel/`, `_ZK_/Evergreen/`,
`_ZK_/Distill/Fragment/` — i.e. zettels and zettel-shaped fragments.

Preconditions:
    - Obsidian must be running (CLI talks to the live app over local IPC).
    - `obsidian` CLI must be in PATH.
"""

import argparse
import json
import shutil
import subprocess
import sys


JS_TEMPLATE = r"""
(() => {
  const seeds = __SEEDS__;
  const depth = __DEPTH__;
  const isZettel = (p) =>
    p.startsWith("_ZK_/Zettel/") ||
    p.startsWith("_ZK_/Evergreen/") ||
    p.startsWith("_ZK_/Distill/Fragment/");

  const allPaths = app.vault.getMarkdownFiles().map(f => f.path);
  const resolveSeed = (s) => {
    if (allPaths.includes(s)) return s;
    const base = s.split("/").pop().replace(/\.md$/, "");
    return allPaths.find(p => p.endsWith("/" + base + ".md") || p === base + ".md");
  };

  const resolved = seeds.map(s => [s, resolveSeed(s)]);
  const realSeeds = resolved.filter(r => r[1]).map(r => r[1]);
  const unresolved = resolved.filter(r => !r[1]).map(r => r[0]);

  if (realSeeds.length === 0) {
    return JSON.stringify({ error: "No seeds resolved", requested: seeds }, null, 2);
  }

  const graph = app.metadataCache.resolvedLinks;
  const reverse = {};
  for (const [src, targets] of Object.entries(graph)) {
    for (const tgt of Object.keys(targets)) {
      if (!reverse[tgt]) reverse[tgt] = new Set();
      reverse[tgt].add(src);
    }
  }

  const visited = new Set(realSeeds);
  const layers = [];
  let frontier = new Set(realSeeds);
  for (let d = 0; d < depth; d++) {
    const next = new Set();
    for (const node of frontier) {
      const out = Object.keys(graph[node] || {});
      const inc = [...(reverse[node] || [])];
      for (const n of [...out, ...inc]) {
        if (!visited.has(n) && isZettel(n)) {
          visited.add(n);
          next.add(n);
        }
      }
    }
    if (next.size === 0) break;
    layers.push({ depth: d + 1, count: next.size, paths: [...next].sort() });
    frontier = next;
  }

  return JSON.stringify({
    seeds: realSeeds,
    unresolvedSeeds: unresolved,
    totalNeighborhood: visited.size - realSeeds.length,
    layers
  }, null, 2);
})()
"""


def main():
    parser = argparse.ArgumentParser(
        description="BFS the Obsidian graph from seed zettels.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--depth", type=int, default=2,
                        help="Number of BFS layers (default: 2)")
    parser.add_argument("--vault", default="TheVault",
                        help="Obsidian vault name (default: TheVault)")
    parser.add_argument("seeds", nargs="+",
                        help="Seed paths or basenames")
    args = parser.parse_args()

    if not shutil.which("obsidian"):
        sys.exit("Error: `obsidian` CLI not found in PATH")

    js = (
        JS_TEMPLATE
        .replace("__SEEDS__", json.dumps(args.seeds))
        .replace("__DEPTH__", str(args.depth))
    )

    result = subprocess.run(
        ["obsidian", f"vault={args.vault}", "eval", f"code={js}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"obsidian CLI failed (exit {result.returncode}):\n{result.stderr}")

    output = result.stdout
    # `obsidian eval` prefixes the first line with "=> "
    if output.startswith("=> "):
        output = output[3:]
    sys.stdout.write(output)
    if not output.endswith("\n"):
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
