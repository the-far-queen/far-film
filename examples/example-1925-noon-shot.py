"""
example-1925-noon-shot.py — example shot compiled from a public-domain 1925
silhouette animation. Demonstrates the far-film shot gate.

Source: archive.org / public-domain 1920s silhouette films
        (https://archive.org/details/silhouettefilmcollection)
        Also: gutenberg plays (pre-1928) for source_id when no specific script.

Shot: silhouette scene, medium-shot, low-key, hand-cranked aesthetic.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from shot import compile_shot, gate, shot_to_dict  # noqa: E402

axes = {
    "aspect_ratio": "1.33:1",       # 4:3 silent-era
    "fps": 16,                       # hand-cranked (~16fps)
    "shutter_angle": 180,
    "color_temp_k": 3200,            # tungsten/incandescent
    "iso_or_exposure": 100,
    "color_space": "rec709",
    "lens_mm": 75,
    "aperture": 4.0,
    "lens_series": "vintage",
    "depth_of_field": "deep",
    "breathing": "mild",
    "distortion": "barrel",
    "light_logic": "available",      # pre-electric location setups
    "key_dir": "side",
    "contrast": 0.85,                # silhouette = high contrast
    "exposure_bias": "under",
    "color_grade": ["black_and_white_silent"],
    "camera_height": "eye",
    "camera_move": "static",
    "axis_of_action": "none",
    "eyeline_match": True,
    "shot_size": "ms",
    "foreground_layer": "occluder",
    "background_density": "clean",
    "composition_grid": "centered",
    "symmetry": "symmetric",
    "negative_space": "high",
    "framing_edges": "tight",
    "composition_letterbox": "both",
    "duration_sec": 5.0,
    "speed_profile": "realtime",
    "motion_blur": "none",           # silent-era low fps = no motion blur
    "frame_blend": False,
    "source_id": "archive.org/silhouettefilmcollection/scene-001",
    "seq_id": "seq-001",
    "tool_id": "archive-source-pipeline",
    "model_id": "",
    "generator_may_propose": False,
    "commit_asset": "gate",
    "banned_motifs": ["modern_logos", "tiktok_aesthetic"],
}

shot = compile_shot(axes)

print(f"shot_id:    {shot.shot_id}")
print(f"aspect:     {shot.aspect_ratio}")
print(f"fps:        {shot.fps}")
print(f"lens_mm:    {shot.lens_mm}")
print(f"shot_size:  {shot.shot_size}")
print(f"color_grade:{shot.color_grade}")
print()

# Gate check
allow, reason = gate(shot)
print(f"gate: allow={allow}, reason={reason}")

# Check that the gate refuses a "naked" asset
allow, reason = gate(None)
print(f"gate(naked): allow={allow}, reason={reason}")

# Verify deterministic id
shot2 = compile_shot(axes)
assert shot.shot_id == shot2.shot_id, "id must be deterministic"
print(f"\ndeterministic: ✓")