import unittest
from math import isclose, hypot
from geometry import *

POCKET = (0.0, 0.0)
R_S, R_C = 0.03, 0.02


class T(unittest.TestCase):
    def test_direct_contact_distance(self):
        s = Disk("s", (0.5, 0.9), R_S); t = Disk("c", (0.3, 0.3), R_C)
        shot = plan_direct(s, t, POCKET, [])
        self.assertTrue(shot.valid)
        self.assertTrue(isclose(hypot(shot.aim_point[0]-t.pos[0], shot.aim_point[1]-t.pos[1]), R_S+R_C))

    def test_blocked_rejected(self):
        t = Disk("c", (0.3, 0.3), R_C)
        s = Disk("s", (0.5, 0.9), R_S)
        aim = plan_direct(s, t, POCKET, []).aim_point
        mid = ((s.pos[0]+aim[0])/2, (s.pos[1]+aim[1])/2)
        shot = plan_direct(s, t, POCKET, [Disk("b", mid, R_C)])
        self.assertFalse(shot.valid); self.assertIn("blocked", shot.reason)

    def test_coin_path_blocked(self):
        s = Disk("s", (0.5, 0.9), R_S); t = Disk("c", (0.3, 0.3), R_C)
        shot = plan_direct(s, t, POCKET, [Disk("b", (0.15, 0.15), R_C)])
        self.assertFalse(shot.valid)

    def test_thin_cut_rejected(self):
        s = Disk("s", (0.9, 0.31), R_S); t = Disk("c", (0.3, 0.3), R_C)
        self.assertFalse(plan_direct(s, t, (0.3, 0.0), []).valid)

    def test_striker_behind_pocket_side(self):
        s = Disk("s", (0.1, 0.1), R_S); t = Disk("c", (0.3, 0.3), R_C)
        self.assertFalse(plan_direct(s, t, POCKET, []).valid)

    def test_reflection(self):
        self.assertEqual(reflect_point((0.2, 0.1), "right"), (1.8, 0.1))
        self.assertEqual(reflect_point((0.2, 0.1), "bottom"), (0.2, 1.9))

    def test_bank_angle_equality(self):
        s = Disk("s", (0.5, 0.9), R_S); t = Disk("c", (0.6, 0.5), R_C)
        shot = plan_bank(s, t, (0.0, 0.0), "right", [])
        self.assertTrue(shot.valid, shot.reason)
        (a, h, b) = shot.coin_path
        # incidence == reflection: |dy/dx| equal on both legs
        self.assertTrue(isclose(abs((h[1]-a[1])/(h[0]-a[0])), abs((b[1]-h[1])/(b[0]-h[0])), rel_tol=1e-6))
        self.assertTrue(isclose(h[0], 1 - R_C))

    def test_bank_blocked(self):
        s = Disk("s", (0.5, 0.9), R_S); t = Disk("c", (0.6, 0.5), R_C)
        ok = plan_bank(s, t, (0.0, 0.0), "right", [])
        h = ok.coin_path[1]
        mid = ((h[0]+0)/2, (h[1]+0)/2)
        self.assertFalse(plan_bank(s, t, (0.0, 0.0), "right", [Disk("b", mid, R_C)]).valid)

    def test_grazing_boundary(self):
        self.assertTrue(segment_hits_disk((0, 0), (1, 0), (0.5, 0.05), 0.05))
        self.assertFalse(segment_hits_disk((0, 0), (1, 0), (0.5, 0.0501), 0.05))


if __name__ == "__main__":
    unittest.main()
