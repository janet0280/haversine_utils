"""Core Haversine implementation.

Uses the canonical mean-radius form of the Haversine formula with
math.sqrt rather than pow() or **0.5 to avoid the tiny extra float noise
that the pow path introduces on CPython 3.11+ for the negative-exponent
fast path. Not a correctness issue, but it keeps test tolerances honest.
"""

from __future__ import annotations

import math
from typing import NamedTuple

# WGS84 semimajor (a) and semiminor (b) axes, metres.
_WGS84_A = 6_378_137.0
_WGS84_B = 6_356_752.314245

# Volumetric mean radius: r = (a^2 * b)^(1/3).
_EARTH_RADIUS_M = (_WGS84_A * _WGS84_A * _WGS84_B) ** (1.0 / 3.0)

_M_PER_KM = 1000.0
_M_PER_MI = 1609.344


class LatLng(NamedTuple):
    """Latitude/longitude in signed decimal degrees.

    Degrees are used at the API boundary because that is what every
    mapping provider returns; we convert to radians internally.
    """

    lat: float
    lng: float


def _validate(lat: float, lng: float) -> None:
    # We reject NaN/Inf before math.radians turns them into silent garbage.
    # We do NOT wrap latitude at the poles: a caller who passes 91 is almost
    # always holding a sign error or a flipped lat/lng pair, and wrapping
    # would return a plausible-looking wrong answer rather than a crash.
    if not math.isfinite(lat) or not math.isfinite(lng):
        raise ValueError("lat and lng must be finite numbers")
    if not -90.0 <= lat <= 90.0:
        raise ValueError(f"latitude must be in [-90, 90]; got {lat!r}")
    if not -180.0 <= lng <= 180.0:
        raise ValueError(f"longitude must be in [-180, 180]; got {lng!r}")


def haversine(
    a_lat: float,
    a_lng: float,
    b_lat: float,
    b_lng: float,
    *,
    radius_m: float = _EARTH_RADIUS_M,
) -> float:
    """Great-circle distance between two decimal-degree points.

    Args:
        a_lat, a_lng: First point, signed degrees.
        b_lat, b_lng: Second point, signed degrees.
        radius_m: Sphere radius in metres. Defaults to the WGS84
            volumetric mean radius (~6371000.8 m). Override for
            other bodies or to use a local-radius approximation.

    Returns:
        Distance in metres (same unit as ``radius_m``).

    Raises:
        ValueError: any coordinate is NaN, Inf, outside its signed range.
    """
    _validate(a_lat, a_lng)
    _validate(b_lat, b_lng)
    if not math.isfinite(radius_m) or radius_m <= 0:
        raise ValueError(f"radius_m must be finite and positive; got {radius_m!r}")

    lat1 = math.radians(a_lat)
    lat2 = math.radians(b_lat)
    dlat = lat2 - lat1
    dlng = math.radians(b_lng - a_lng)

    # Sine-half-angle form. sin^2(x) = (1 - cos(2x)) / 2; using math.sin of
    # the *half* angle keeps every intermediate in [-1, 1] so we never lose
    # precision the way sin^2(large) would near the equator.
    shlat = math.sin(dlat / 2.0)
    shlng = math.sin(dlng / 2.0)

    h = shlat * shlat + math.cos(lat1) * math.cos(lat2) * shlng * shlng
    # Clamp against the one-ULP overshoot that can push h marginally above 1
    # for antipodal points and turn a real distance into NaN via asin.
    if h > 1.0:
        h = 1.0
    elif h < 0.0:
        h = 0.0

    return 2.0 * radius_m * math.asin(math.sqrt(h))


def haversine_km(
    a_lat: float, a_lng: float, b_lat: float, b_lng: float
) -> float:
    """``haversine`` with the result converted to kilometres."""
    return haversine(a_lat, a_lng, b_lat, b_lng) / _M_PER_KM


def haversine_mi(
    a_lat: float, a_lng: float, b_lat: float, b_lng: float
) -> float:
    """``haversine`` with the result converted to statute miles."""
    return haversine(a_lat, a_lng, b_lat, b_lng) / _M_PER_MI
