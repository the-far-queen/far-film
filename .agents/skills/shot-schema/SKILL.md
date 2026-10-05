---
name: shot-schema
description: >-
  Use when the user wants to compile a film shot, run the F gate, or load public-domain
  source discipline. Triggers: "film shot", "shot axes", "compile shot", "F gate",
  "archive.org screenplays", "silhouette film".
---

# Shot schema (far-film)

The shot is the **canonical unit** of film in this repo. Every shot is a frozen dataclass with a deterministic id.

## Compile

```python
from far_film.tools.shot import compile_shot, gate

shot = compile_shot({
    "aspect_ratio": "2.39:1",
    "fps": 24,
    "lens_mm": 35,
    "aperture": 2.0,
    "shot_size": "ms",
    "source_id": "archive.org/screenplays/the-cat-1925",
    "camera_move": "static",
    "duration_sec": 4.0,
})
```

The shot_id is `sha256(canonical(axes))[:16]`. Same axes → same id.

## Gate

```python
allow, reason = gate(shot, asset_text="...")
```

`commit_asset="gate"` (default) refuses naked shots (`no_shot`) or shots without `source_id` (`no_source_id`), or shots with `banned_motifs` matching the asset text.

## Public-domain sources

See `docs/sources.md` in the repo. archive.org + gutenberg plays + wikisource.

## See also

- `AGENTS.md` in the repo — the contract
- `tests/test_shot.py` — F1..F5
- `examples/example-1925-noon-shot.py` — worked example