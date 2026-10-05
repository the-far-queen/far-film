"""
compile_shot.py — CLI for compiling a shot YAML/JSON file.

Usage:
    python tools/compile_shot.py path/to/shot.yaml
    python tools/compile_shot.py --stdin    # JSON via stdin
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from shot import compile_shot, shot_to_dict  # noqa: E402


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    out = {}
    for line in text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Cannot parse YAML line: {line!r}")
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
            val = val[1:-1]
        if val.startswith("[") and val.endswith("]"):
            items = val[1:-1].split(",")
            val = [i.strip().strip('"').strip("'") for i in items if i.strip()]
        elif isinstance(val, str):
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
        out[key] = val
    return out


def main(argv):
    p = argparse.ArgumentParser(description="Compile a far-film shot.")
    p.add_argument("path", nargs="?", help="Path to shot YAML/JSON file.")
    p.add_argument("--stdin", action="store_true", help="Read JSON from stdin.")
    args = p.parse_args(argv)

    if args.stdin:
        axes = json.loads(sys.stdin.read())
    elif args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            return 2
        axes = _load_yaml(path)
    else:
        # No arg: show schema summary
        from shot import (ASPECT_RATIOS, COLOR_SPACES, LIGHT_LOGICS, KEY_DIRS,
                          CAMERA_HEIGHTS, CAMERA_MOVES, SHOT_SIZES)
        print("far-film shot schema summary:")
        print(f"  aspect_ratios: {sorted(ASPECT_RATIOS)}")
        print(f"  color_spaces: {sorted(COLOR_SPACES)}")
        print(f"  light_logics: {sorted(LIGHT_LOGICS)}")
        print(f"  key_dirs: {sorted(KEY_DIRS)}")
        print(f"  camera_heights: {sorted(CAMERA_HEIGHTS)}")
        print(f"  camera_moves: {sorted(CAMERA_MOVES)}")
        print(f"  shot_sizes: {sorted(SHOT_SIZES)}")
        return 0

    try:
        shot = compile_shot(axes)
    except (KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out = shot_to_dict(shot)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))