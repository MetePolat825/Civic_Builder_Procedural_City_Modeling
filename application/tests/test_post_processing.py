import unittest
import numpy as np
import cv2
from post_processing import simplify_contours, smooth_contours, fill_holes, bounding_boxes, convex_hulls

class TestPostProcessing(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.contours = [np.array([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]], dtype=np.int32)]
        self.mask = np.zeros((20, 20), dtype=np.uint8)
        cv2.rectangle(self.mask, (5, 5), (15, 15), 255, -1)  # Create a filled rectangle in the mask

    def test_simplify_contours(self):
        simplified = simplify_contours(self.contours)
        self.assertEqual(len(simplified), 1)
        self.assertTrue(np.array_equal(simplified[0], self.contours[0]))

    def test_smooth_contours(self):
        smoothed = smooth_contours(self.contours, epsilon_factor=0.1)
        self.assertEqual(len(smoothed), 1)
        self.assertTrue(np.array_equal(smoothed[0], self.contours[0]))

    def test_fill_holes(self):
        contours = fill_holes(self.mask)
        self.assertEqual(len(contours), 1)
        self.assertTrue(cv2.contourArea(contours[0]) > 0)

    def test_bounding_boxes(self):
        boxes = bounding_boxes(self.contours)
        self.assertEqual(len(boxes), 1)
        self.assertTrue(np.array_equal(boxes[0], np.array([[0, 0], [10, 0], [10, 10], [0, 10]])))

    def test_convex_hulls(self):
        hulls = convex_hulls(self.contours)
        self.assertEqual(len(hulls), 1)
        self.assertTrue(np.array_equal(hulls[0], self.contours[0]))

if __name__ == '__main__':
    unittest.main()