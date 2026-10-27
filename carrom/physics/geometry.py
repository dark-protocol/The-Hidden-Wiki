"""Phase 3 reference: direct-shot and bank-shot geometry in normalized board coords.

Board: square [0,1]x[0,1], y down. Units are board-widths. All values are estimates
until calibrated (SRS 6.4/6.5).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import hypot
from typing import List, Optional, Tuple

Vec = Tuple[float, float]
EPS = 1e-9


@dataclass(frozen=True)
class Disk:
    id: str
    pos: Vec
    r: float


@dataclass
class Shot:
    valid: bool
    reason: str = ""
    kind: str = "direct"          # direct | bank
    aim_point: Optional[Vec] = None  # striker center at contact
    path: List[Vec] = field(default_factory=list)  # striker polyline to contact
    coin_path: List[Vec] = field(default_factory=list)
    cut_angle_deg: float = 0.0


def _sub(a, b): return (a[0] - b[0], a[1] - b[1])
def _dist(a, b): return hypot(a[0] - b[0], a[1] - b[1])


def segment_hits_disk(a: Vec, b: Vec, c: Vec, radius: float) -> bool:
    """True if segment a-b comes within `radius` of point c (contact: |d| <= r)."""
    ab, ac = _sub(b, a), _sub(c, a)
    L2 = ab[0] ** 2 + ab[1] ** 2
    t = 0.0 if L2 < EPS else max(0.0, min(1.0, (ac[0] * ab[0] + ac[1] * ab[1]) / L2))
    return _dist((a[0] + t * ab[0], a[1] + t * ab[1]), c) <= radius


def reflect_point(p: Vec, wall: str, inset: float = 0.0) -> Vec:
    """Mirror p across a cushion line, inset by the disk radius for center paths."""
    lo, hi = inset, 1 - inset
    return {"left": (2 * lo - p[0], p[1]), "right": (2 * hi - p[0], p[1]),
            "top": (p[0], 2 * lo - p[1]), "bottom": (p[0], 2 * hi - p[1])}[wall]


def _wall_hit(a: Vec, b: Vec, wall: str, inset: float) -> Optional[Vec]:
    """Point where a->b crosses the cushion line (inset by disk radius)."""
    if wall in ("left", "right"):
        x = inset if wall == "left" else 1 - inset
        if abs(b[0] - a[0]) < EPS: return None
        t = (x - a[0]) / (b[0] - a[0])
        pt = (x, a[1] + t * (b[1] - a[1]))
    else:
        y = inset if wall == "top" else 1 - inset
        if abs(b[1] - a[1]) < EPS: return None
        t = (y - a[1]) / (b[1] - a[1])
        pt = (a[0] + t * (b[0] - a[0]), y)
    return pt if 0 < t < 1 else None


def plan_direct(striker: Disk, target: Disk, pocket: Vec, others: List[Disk],
                max_cut_deg: float = 80.0) -> Shot:
    """Striker must hit `target` so it travels toward `pocket`."""
    d = _sub(pocket, target.pos)
    n = hypot(*d)
    if n < EPS:
        return Shot(False, "target on pocket")
    u = (d[0] / n, d[1] / n)
    rs = striker.r + target.r
    # striker center at contact lies behind the target along the pocket line
    aim = (target.pos[0] - u[0] * rs, target.pos[1] - u[1] * rs)
    v = _sub(aim, striker.pos)
    vn = hypot(*v)
    if vn < EPS:
        return Shot(False, "striker already at contact point")
    # striker must approach from behind: direction must have positive component toward pocket line
    cos = (v[0] * u[0] + v[1] * u[1]) / vn
    cut = _acos_deg(cos)
    if (target.pos[0] - striker.pos[0]) * u[0] + (target.pos[1] - striker.pos[1]) * u[1] <= 0:
        return Shot(False, "striker is on pocket side of target")
    if cut > max_cut_deg:
        return Shot(False, f"cut angle {cut:.0f} deg too thin", cut_angle_deg=cut)
    if not (0 <= aim[0] <= 1 and 0 <= aim[1] <= 1):
        return Shot(False, "contact point outside board")
    for o in others:
        if o.id in (striker.id, target.id): continue
        if segment_hits_disk(striker.pos, aim, o.pos, striker.r + o.r):
            return Shot(False, f"striker path blocked by {o.id}")
        if segment_hits_disk(target.pos, pocket, o.pos, target.r + o.r):
            return Shot(False, f"coin path blocked by {o.id}")
    return Shot(True, kind="direct", aim_point=aim, path=[striker.pos, aim],
                coin_path=[target.pos, pocket], cut_angle_deg=cut)


def plan_bank(striker: Disk, target: Disk, pocket: Vec, wall: str,
              others: List[Disk]) -> Shot:
    """Single-cushion bank for the target coin: reflect pocket across `wall`."""
    mirrored = reflect_point(pocket, wall, target.r)
    shot = plan_direct(striker, target, mirrored, [], max_cut_deg=80.0)
    if not shot.valid:
        return Shot(False, "bank: " + shot.reason, kind="bank")
    hit = _wall_hit(target.pos, mirrored, wall, target.r)
    if hit is None:
        return Shot(False, "bank: no cushion contact", kind="bank")
    legs = [(target.pos, hit), (hit, pocket)]
    for o in others:
        if o.id in (striker.id, target.id): continue
        if segment_hits_disk(striker.pos, shot.aim_point, o.pos, striker.r + o.r):
            return Shot(False, f"striker path blocked by {o.id}", kind="bank")
        for a, b in legs:
            if segment_hits_disk(a, b, o.pos, target.r + o.r):
                return Shot(False, f"coin path blocked by {o.id}", kind="bank")
    shot.kind = "bank"
    shot.coin_path = [target.pos, hit, pocket]
    return shot


def _acos_deg(c: float) -> float:
    from math import acos, degrees
    return degrees(acos(max(-1.0, min(1.0, c))))
