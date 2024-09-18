import unittest
import numpy as np
from ngawari import ftk

class TestFTK(unittest.TestCase):

    def test_getIDOfClosestFloat(self):
        float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(ftk.getIDOfClosestFloat(3.2, float_list), 2)
        self.assertEqual(ftk.getIDOfClosestFloat(1.8, float_list), 1)

    def test_getClosestFloat(self):
        float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
        self.assertEqual(ftk.getClosestFloat(3.2, float_list), 3.0)
        self.assertEqual(ftk.getClosestFloat(1.8, float_list), 2.0)

    def test_distPointPoints(self):
        point = [0, 0, 0]
        points = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        expected = [1, 1, 1]
        np.testing.assert_array_almost_equal(ftk.distPointPoints(point, points), expected)

    def test_normaliseArray(self):
        vecs = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        normalized = ftk.normaliseArray(vecs)
        expected = [[1.0/np.sqrt(3.), 1.0/np.sqrt(3.), 1.0/np.sqrt(3.)] for _ in range(3)]
        np.testing.assert_array_almost_equal(normalized, expected)

    def test_angleBetween2Vec(self):
        v1 = [1, 0, 0]
        v2 = [0, 1, 0]
        self.assertAlmostEqual(ftk.angleBetween2Vec(v1, v2), np.pi/2)
        self.assertAlmostEqual(ftk.angleBetween2Vec(v1, v2, RETURN_DEGREES=True), 90)

    def test_fitPlaneToPoints(self):
        points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]
        plane = ftk.fitPlaneToPoints(points)
        expected = [0, 0, 1, 0]  # z = 0 plane
        np.testing.assert_array_almost_equal(plane, expected)

    def test_projectPtsToPlane(self):
        pts = [[1, 1, 1], [2, 2, 2], [3, 3, 3]]
        plane = [0, 0, 1, -1]  # z = 1 plane
        projected = ftk.projectPtsToPlane(pts, plane)
        expected = [[1, 1, 1], [2, 2, 1], [3, 3, 1]]
        np.testing.assert_array_almost_equal(projected, expected)

    def test_buildCircle3D(self):
        center = [0, 0, 0]
        normal = [0, 0, 1]
        radius = 1
        circle = ftk.buildCircle3D(center, normal, radius, nPts=4)
        expected = [[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]]
        deltas = [np.min(ftk.distPointPoints(circle[i], expected)) for i in range(4)]
        np.testing.assert_array_less(deltas, 0.01)


    def test_RunningStats(self):
        stats = ftk.RunningStats()
        numbers = [1, 2, 3, 4, 5]
        for num in numbers:
            stats.push(num)
        self.assertAlmostEqual(stats.mean(), 3.0)
        self.assertAlmostEqual(stats.variance(), 2.5)
        self.assertAlmostEqual(stats.standard_deviation(), np.sqrt(2.5))

if __name__ == '__main__':
    unittest.main()
