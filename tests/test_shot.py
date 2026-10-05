"""
test_shot.py — F1..F5 gate tests for far-film/tools/shot.py.

Mirrors the far-art R1..R5 + far-writing W1..W5 pattern.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))

from shot import compile_shot, gate, shot_to_dict  # noqa: E402


def _base_axes(**overrides):
    axes = {
        "aspect_ratio": "2.39:1",
        "lens_mm": 35,
        "aperture": 2.0,
        "fps": 24,
        "shot_size": "ms",
        "source_id": "archive.org/screenplays/the-cat-1925",
        "camera_move": "static",
        "duration_sec": 4.0,
    }
    axes.update(overrides)
    return axes


def test_F1_repro_id():
    """F1: same axes -> same id; different axes -> different id."""
    s1 = compile_shot(_base_axes())
    s2 = compile_shot(_base_axes())
    s3 = compile_shot(_base_axes(lens_mm=50))
    assert s1.shot_id == s2.shot_id, "F1: same axes must produce same id"
    assert s1.shot_id != s3.shot_id, "F1: different axes must produce different id"
    print("F1: ok")


def test_F2_seq_ids():
    """F2: same input dict -> same id, roundtrip stable."""
    # User-supplied axes (full set, no relying on defaults)
    axes = {
        "aspect_ratio": "2.39:1", "lens_mm": 35, "aperture": 2.0,
        "fps": 24, "shot_size": "ms", "camera_move": "static",
        "duration_sec": 4.0, "source_id": "src-A", "seq_id": "seq-001",
        "color_space": "rec709", "light_logic": "natural",
        "key_dir": "three_quarter", "camera_height": "eye",
        "depth_of_field": "deep", "breathing": "none",
        "composition_grid": "rule_of_thirds", "reading_path": "z",
        "symmetry": "asymmetric", "exposure_bias": "normal",
        "speed_profile": "realtime", "motion_blur": "mild",
        "commit_asset": "gate",
    }
    s = compile_shot(axes)
    # roundtrip: same input dict → same id
    s2 = compile_shot(axes)
    assert s.shot_id == s2.shot_id, "F2: same axes must produce same id"
    assert s.seq_id == s2.seq_id, "F2: seq_id must roundtrip"
    assert s.source_id == s2.source_id, "F2: source_id must roundtrip"
    print("F2: ok")


def test_F3_banned_motif():
    """F3: banned_motifs in shot + matching asset text -> refused."""
    s = compile_shot(_base_axes(banned_motifs=["blood"]))
    allow, reason = gate(s, "the scene has blood and gore everywhere")
    assert not allow and "banned_motif" in reason, f"F3 fail: {reason}"
    # empty asset text -> still allowed
    allow, reason = gate(s, "")
    assert allow and reason == "ok", f"F3 clean fail: {reason}"
    print("F3: ok")


def test_F4_lens_aspect_distinct():
    """F4: varying lens_mm OR aspect_ratio must produce different ids."""
    s_base = compile_shot(_base_axes())
    s_lens = compile_shot(_base_axes(lens_mm=85))
    s_aspect = compile_shot(_base_axes(aspect_ratio="1.85:1"))
    s_fps = compile_shot(_base_axes(fps=30))
    assert len({s_base.shot_id, s_lens.shot_id, s_aspect.shot_id, s_fps.shot_id}) == 4, "F4 fail"
    print("F4: ok")


def test_F5_no_house_default():
    """F5: naked prompt + gate -> refused, no fallback."""
    allow, reason = gate(None)
    assert not allow and reason == "no_shot", f"F5 fail: {reason}"
    # shot with commit_asset=forbid
    s_forbid = compile_shot(_base_axes(commit_asset="forbid"))
    allow, reason = gate(s_forbid)
    assert not allow and reason == "commit_forbidden", f"F5 forbid fail: {reason}"
    print("F5: ok")


def main():
    test_F1_repro_id()
    test_F2_seq_ids()
    test_F3_banned_motif()
    test_F4_lens_aspect_distinct()
    test_F5_no_house_default()
    print("\nALL F1..F5 PASS")


if __name__ == "__main__":
    main()