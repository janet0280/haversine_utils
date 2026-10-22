import math
import unittest

from haversine_utils import haversine, haversine_km, haversine_mi


class TestHaversine(unittest.TestCase):
    # The Haversine formula is exact on a sphere; the only real float error
    # comes from the trig chain. 1e-6 relative keeps tests stable across
    # CPython versions without masking a genuinely broken implementation.
    REL = 1e-6

    def _close(self, got: float, want: float, msg: str = "") -> None:
        if want == 0.0:
            self.assertAlmostEqual(got, want, places=6, msg=msg)
        else:
            self.assertLessEqual(
                abs(got - want) / abs(want), self.REL, f"{msg}: {got} != {want}"
            )

    def test_same_point_is_zero(self):
        self.assertEqual(haversine(0.0, 0.0, 0.0, 0.0), 0.0)
        self.assertEqual(haversine(51.5, -0.12, 51.5, -0.12), 0.0)

    def test_small_distance(self):
        # ~111 km per degree of latitude at the equator; 0.001 deg ~= 111 m.
        d = haversine(0.0, 0.0, 0.001, 0.0)
        self._close(d, 111.194940, "0.001 deg latitude at equator")

    def test_one_degree_equator(self):
        d = haversine(0.0, 0.0, 1.0, 0.0)
        self._close(d, 111_194.93, "one degree of latitude")

    def test_london_to_paris(self):
        # London 51.5074, -0.1278; Paris 48.8566, 2.3522.
        d = haversine(51.5074, -0.1278, 48.8566, 2.3522)
        self._close(d, 343_556.0, "London to Paris")

    def test_new_york_to_los_angeles(self):
        d = haversine(40.7128, -74.0060, 34.0522, -118.2437)
        self._close(d, 3_935_746.0, "NYC to LA")

    def test_sydney_to_cape_town(self):
        d = haversine(-33.8688, 151.2093, -33.9249, 18.4241)
        self._close(d, 11_011_665.5, "Sydney to Cape Town")

    def test_north_pole_to_south_pole(self):
        # Antipodal on the same meridian: half the circumference.
        d = haversine(90.0, 0.0, -90.0, 0.0)
        self._close(d, math.pi * 6_371_000.8, "pole to pole")

    def test_point_to_antipode(self):
        # A point and its exact antipode: half-circumference, chosen to
        # stress the h>1 clamp in the implementation.
        d = haversine(45.0, 90.0, -45.0, -90.0)
        self._close(d, math.pi * 6_371_000.8, "antipodal")

    def test_longitude_wraparound_equivalence(self):
        # +180 and -180 are the same meridian; distance must be zero.
        self.assertAlmostEqual(haversine(0.0, -180.0, 0.0, 180.0), 0.0, places=6)

    def test_invalid_latitude_too_large(self):
        with self.assertRaises(ValueError):
            haversine(91.0, 0.0, 0.0, 0.0)

    def test_invalid_latitude_too_small(self):
        with self.assertRaises(ValueError):
            haversine(-91.0, 0.0, 0.0, 0.0)

    def test_invalid_longitude_too_large(self):
        with self.assertRaises(ValueError):
            haversine(0.0, 181.0, 0.0, 0.0)

    def test_invalid_longitude_too_small(self):
        with self.assertRaises(ValueError):
            haversine(0.0, -181.0, 0.0, 0.0)

    def test_nan_latitude_rejected(self):
        with self.assertRaises(ValueError):
            haversine(float("nan"), 0.0, 0.0, 0.0)

    def test_inf_longitude_rejected(self):
        with self.assertRaises(ValueError):
            haversine(0.0, float("inf"), 0.0, 0.0)

    def test_negative_radius_rejected(self):
        with self.assertRaises(ValueError):
            haversine(0.0, 0.0, 1.0, 0.0, radius_m=-1.0)

    def test_custom_radius(self):
        d = haversine(0.0, 0.0, 0.0, 90.0, radius_m=2.0)
        # Quarter of a unit-sphere's circumference.
        self._close(d, math.pi, "unit sphere quarter")

    def test_km_unit(self):
        d = haversine_km(0.0, 0.0, 1.0, 0.0)
        self._close(d, 111.1949, "km")

    def test_mi_unit(self):
        d = haversine_mi(0.0, 0.0, 1.0, 0.0)
        self._close(d, 69.0933, "miles")


if __name__ == "__main__":
    unittest.main()
