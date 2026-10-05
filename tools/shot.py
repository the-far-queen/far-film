"""
shot.py — Shot compile + gate (far-film).

Mirrors far-art/tools/sheet.py structure. The schema (axes) is the
contract declared in AGENTS.md. Naked shots (no shot_id) are refused
with reason 'no_shot'. Banned motifs are refused with reason
'banned_motif'.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enums (the contract — see AGENTS.md)
# ---------------------------------------------------------------------------

ASPECT_RATIOS = {"1.33:1", "1.66:1", "1.78:1", "1.85:1", "2.39:1", "2.55:1"}
COLOR_SPACES = {"rec709", "rec2020", "p3", "log_c", "s_log3", "linear"}
LIGHT_LOGICS = {"natural", "studio", "motivated", "mixed", "available"}
KEY_DIRS = {"front", "side", "back", "top", "bottom", "three_quarter"}
CAMERA_HEIGHTS = {"eye", "high", "low", "worm", "overhead", "dutch"}
CAMERA_MOVES = {"static", "pan", "tilt", "dolly", "track", "crane",
                "handheld", "steadicam"}
SHOT_SIZES = {"els", "ls", "ms", "mcu", "cu", "ecu", "insert"}
DEPTH_OF_FIELDS = {"shallow", "deep", "rack"}
BREATHING = {"none", "mild", "heavy"}
DISTORTION = {"none", "barrel", "pincushion", "mustache"}
SPEED_PROFILES = {"realtime", "slow_mo_2x", "slow_mo_4x",
                  "time_lapse", "ramping"}
MOTION_BLUR = {"none", "mild", "heavy", "smearing"}
COMPOSITION_GRIDS = {"rule_of_thirds", "golden", "centered", "diagonal", "custom"}
READING_PATHS = {"z", "l", "reverse_z", "scanline", "free"}
SYMMETRY = {"symmetric", "near", "asymmetric"}
EXPOSURE_BIAS = {"under", "normal", "over"}
COMMIT_ASSET = {"gate", "allow", "forbid"}


# ---------------------------------------------------------------------------
# Shot (the canonical record — see AGENTS.md)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Shot:
    """A film shot — frozen record of axes per AGENTS.md."""

    # identity / source
    shot_id: str
    seq_id: str
    variant_of: str
    source_id: str  # every shot traces back to a script

    # Group A — Frame
    aspect_ratio: str
    resolution_w: int
    resolution_h: int
    color_space: str
    fps: int
    shutter_angle: float
    color_temp_k: int
    iso_or_exposure: float
    print_or_screen: str

    # Group B — Lens
    lens_mm: float
    aperture: float
    lens_series: str
    filter: str
    depth_of_field: str
    focus_pull: Tuple[str, ...]
    breathing: str
    distortion: str

    # Group C — Light
    light_logic: str
    key_dir: str
    contrast: float
    practicals: Tuple[str, ...]
    shadow_hue: str
    exposure_bias: str
    lut_ref: str
    color_grade: Tuple[str, ...]

    # Group D — Blocking
    camera_height: str
    camera_move: str
    axis_of_action: str
    eyeline_match: bool
    shot_size: str
    camera_subject_dist: str
    foreground_layer: str
    background_density: str

    # Group E — Composition
    composition_grid: str
    reading_path: str
    symmetry: str
    negative_space: str
    framing_edges: str
    aspect_of_subject: str
    composition_letterbox: str
    title_safe_action: bool

    # Group F — Movement + Time
    duration_sec: float
    speed_profile: str
    motion_blur: str
    frame_blend: bool
    in_point: float
    out_point: float

    # Group G — Pipeline
    tool_id: str
    model_id: str
    generator_may_propose: bool
    commit_asset: str

    # ban-list (carried in axes per AGENTS.md)
    banned_motifs: Tuple[str, ...]


# ---------------------------------------------------------------------------
# Compile (the canonical form for hashing)
# ---------------------------------------------------------------------------

def _canonical(axes: Dict[str, Any]) -> str:
    """Return a canonical JSON string for hashing.

    Derived identity fields (shot_id) are stripped before hashing — they
    are outputs of this function, not inputs.
    """
    derived = {"shot_id"}
    filtered = {k: v for k, v in axes.items() if k not in derived}

    def norm(v):
        if isinstance(v, (list, tuple)):
            return sorted([norm(x) for x in v if x is not None])
        if isinstance(v, dict):
            return {k: norm(val) for k, val in sorted(v.items())}
        if v is None:
            return None
        return v

    return json.dumps(norm(filtered), sort_keys=True, separators=(",", ":"))


def compile_shot(axes: Dict[str, Any]) -> Shot:
    """Compile a dict of shot axes into a frozen Shot.

    The shot_id is sha256(canonical(axes)) truncated to 16 hex chars.
    """
    canonical = _canonical(axes)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    # Validate enums
    for k, vs, label in [
        ("aspect_ratio", ASPECT_RATIOS, "Frame"),
        ("color_space", COLOR_SPACES, "Frame"),
        ("light_logic", LIGHT_LOGICS, "Light"),
        ("key_dir", KEY_DIRS, "Light"),
        ("camera_height", CAMERA_HEIGHTS, "Blocking"),
        ("camera_move", CAMERA_MOVES, "Blocking"),
        ("shot_size", SHOT_SIZES, "Blocking"),
        ("depth_of_field", DEPTH_OF_FIELDS, "Lens"),
        ("breathing", BREATHING, "Lens"),
        ("distortion", DISTORTION, "Lens"),
        ("speed_profile", SPEED_PROFILES, "Time"),
        ("motion_blur", MOTION_BLUR, "Time"),
        ("composition_grid", COMPOSITION_GRIDS, "Composition"),
        ("reading_path", READING_PATHS, "Composition"),
        ("symmetry", SYMMETRY, "Composition"),
        ("exposure_bias", EXPOSURE_BIAS, "Light"),
        ("commit_asset", COMMIT_ASSET, "Pipeline"),
    ]:
        v = axes.get(k)
        if v is not None and v not in vs:
            raise ValueError(f"{label} axis {k!r}={v!r} not in {sorted(vs)}")

    return Shot(
        shot_id=digest,
        seq_id=axes.get("seq_id", ""),
        variant_of=axes.get("variant_of", ""),
        source_id=axes.get("source_id", ""),
        aspect_ratio=axes.get("aspect_ratio", "2.39:1"),
        resolution_w=int(axes.get("resolution_w", 1920)),
        resolution_h=int(axes.get("resolution_h", 1080)),
        color_space=axes.get("color_space", "rec709"),
        fps=int(axes.get("fps", 24)),
        shutter_angle=float(axes.get("shutter_angle", 180)),
        color_temp_k=int(axes.get("color_temp_k", 5600)),
        iso_or_exposure=float(axes.get("iso_or_exposure", 800)),
        print_or_screen=axes.get("print_or_screen", "screen"),
        lens_mm=float(axes.get("lens_mm", 50)),
        aperture=float(axes.get("aperture", 4.0)),
        lens_series=axes.get("lens_series", "modern"),
        filter=axes.get("filter", ""),
        depth_of_field=axes.get("depth_of_field", "deep"),
        focus_pull=tuple(axes.get("focus_pull", [])),
        breathing=axes.get("breathing", "none"),
        distortion=axes.get("distortion", "none"),
        light_logic=axes.get("light_logic", "natural"),
        key_dir=axes.get("key_dir", "three_quarter"),
        contrast=float(axes.get("contrast", 0.5)),
        practicals=tuple(axes.get("practicals", [])),
        shadow_hue=axes.get("shadow_hue", "#000000"),
        exposure_bias=axes.get("exposure_bias", "normal"),
        lut_ref=axes.get("lut_ref", ""),
        color_grade=tuple(axes.get("color_grade", [])),
        camera_height=axes.get("camera_height", "eye"),
        camera_move=axes.get("camera_move", "static"),
        axis_of_action=axes.get("axis_of_action", "none"),
        eyeline_match=bool(axes.get("eyeline_match", True)),
        shot_size=axes.get("shot_size", "ms"),
        camera_subject_dist=axes.get("camera_subject_dist", ""),
        foreground_layer=axes.get("foreground_layer", "none"),
        background_density=axes.get("background_density", "clean"),
        composition_grid=axes.get("composition_grid", "rule_of_thirds"),
        reading_path=axes.get("reading_path", "z"),
        symmetry=axes.get("symmetry", "asymmetric"),
        negative_space=axes.get("negative_space", "balanced"),
        framing_edges=axes.get("framing_edges", "loose"),
        aspect_of_subject=axes.get("aspect_of_subject", "full"),
        composition_letterbox=axes.get("composition_letterbox", "both"),
        title_safe_action=bool(axes.get("title_safe_action", True)),
        duration_sec=float(axes.get("duration_sec", 4.0)),
        speed_profile=axes.get("speed_profile", "realtime"),
        motion_blur=axes.get("motion_blur", "mild"),
        frame_blend=bool(axes.get("frame_blend", False)),
        in_point=float(axes.get("in_point", 0.0)),
        out_point=float(axes.get("out_point", 0.0)),
        tool_id=axes.get("tool_id", ""),
        model_id=axes.get("model_id", ""),
        generator_may_propose=bool(axes.get("generator_may_propose", False)),
        commit_asset=axes.get("commit_asset", "gate"),
        banned_motifs=tuple(axes.get("banned_motifs", [])),
    )


# ---------------------------------------------------------------------------
# Gate (the single commit_asset checker)
# ---------------------------------------------------------------------------

def gate(shot: Optional[Shot], asset_text: str = "") -> Tuple[bool, str]:
    """Check the gate. Returns (allow, reason)."""

    if shot is None:
        return False, "no_shot"

    if shot.commit_asset == "forbid":
        return False, "commit_forbidden"

    if shot.commit_asset == "allow":
        return True, "ok"

    # commit_asset == "gate" (default)
    if not shot.shot_id:
        return False, "no_shot_id"

    if not shot.source_id:
        # every shot traces back to a script (AGENTS.md Group G axis 56)
        return False, "no_source_id"

    if shot.banned_motifs:
        for motif in shot.banned_motifs:
            if re.search(re.escape(motif), asset_text, re.IGNORECASE):
                return False, f"banned_motif:{motif}"

    return True, "ok"


# ---------------------------------------------------------------------------
# to_dict (for serialization to YAML / JSON)
# ---------------------------------------------------------------------------

def shot_to_dict(shot: Shot) -> Dict[str, Any]:
    """Return a plain dict from a Shot. Field names match AGENTS.md axes."""
    d = asdict(shot)
    return {k: list(v) if isinstance(v, tuple) else v for k, v in d.items()}


__all__ = [
    "Shot",
    "compile_shot",
    "gate",
    "shot_to_dict",
    # enums (re-export for callers)
    "ASPECT_RATIOS", "COLOR_SPACES", "LIGHT_LOGICS", "KEY_DIRS",
    "CAMERA_HEIGHTS", "CAMERA_MOVES", "SHOT_SIZES", "DEPTH_OF_FIELDS",
    "BREATHING", "DISTORTION", "SPEED_PROFILES", "MOTION_BLUR",
    "COMPOSITION_GRIDS", "READING_PATHS", "SYMMETRY", "EXPOSURE_BIAS",
    "COMMIT_ASSET",
]