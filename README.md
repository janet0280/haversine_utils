# haversine_utils

Great-circle distance between two points on Earth, using the Haversine formula on the WGS84 volumetric mean-radius sphere.

```python
from haversine_utils import haversine, haversine_km, haversine_mi

# London to Paris, in metres.
m = haversine(51.5074, -0.1278, 48.8566, 2.3522)
km = haversine_km(51.5074, -0.1278, 48.8566, 2.3522)
mi = haversine_mi(51.5074, -0.1278, 48.8566, 2.3522)
```

## Why this exists

The problem is small and self-contained: given two latitude/longitude pairs in signed decimal degrees, return the shortest surface distance between them, assuming a spherical Earth. That is all this library does. No GeoJSON, no coordinate-system plumbing, no ellipsoidal refinements.

The trade-off is accuracy for simplicity. A sphere cannot model Earth's ~0.3% polar flattening; over transcontinental distances the error can reach ~0.3% versus a geodesic on the WGS84 ellipsoid. If you need sub-meter accuracy, use a geodesic library. For ranking, filtering, or display, the error is below the noise of most input data.

The default radius is the WGS84 volumetric mean (~6,371,000.8 m). Override it via the `radius_m` keyword if you need a different body or a local-radius approximation.

## Edges you will hit

Coordinates are validated, not wrapped. A latitude of `91.0` raises `ValueError` rather than silently meaning "1° past the pole." The reasoning: a caller passing `91` almost always has a sign error or a swapped lat/lng pair, and wrapping would hand back a plausible-looking wrong number instead of a crash. NaN and Inf inputs are also rejected before `math.radians` turns them into silent garbage.

The `+180°` and `-180°` longitudes are treated as the same meridian, so the distance between `(0, -180)` and `(0, 180)` is zero. For antipodal points the internal `sin²` term is clamped to 1.0 before `asin`, which absorbs the one-ULP float overshoot that would otherwise return `NaN`.

Run the suite with:

```
PYTHONPATH=src python -m unittest discover -s tests
```
