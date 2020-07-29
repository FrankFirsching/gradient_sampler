import unittest

import stroke_utils

class TestStrokeUtils(unittest.TestCase):

    def test_bbox(self):
        s = [(1,1),(3,1),(3,6)]
        bbox = stroke_utils.bbox(s)
        self.assertEqual(bbox['left'], 1)
        self.assertEqual(bbox['top'], 1)
        self.assertEqual(bbox['width'], 3)
        self.assertEqual(bbox['height'], 6)

    def test_transformed(self):
        s = [(1,1),(3,1),(3,6)]
        s2 = stroke_utils.transformed(s, -1,2, 10, 20)
        self.assertEqual(s2[0], (9,22))
        self.assertEqual(s2[1], (7,22))
        self.assertEqual(s2[2], (7,32))

    def test_connect(self):
        s = [(1,1),(3,1)]
        s2 = stroke_utils.connect(s)
        self.assertEqual(len(s2), 3)
        self.assertEqual(s2[0], (1,1))
        self.assertEqual(s2[1], (2,1))
        self.assertEqual(s2[2], (3,1))

        s = [(1,1),(3,1),(3,3)]
        s2 = stroke_utils.connect(s)
        self.assertEqual(len(s2), 5)
        self.assertEqual(s2[0], (1,1))
        self.assertEqual(s2[1], (2,1))
        self.assertEqual(s2[2], (3,1))
        self.assertEqual(s2[3], (3,2))
        self.assertEqual(s2[4], (3,3))

        s = [(3,1),(1,2)]
        s2 = stroke_utils.connect(s)
        self.assertEqual(len(s2), 3)
        self.assertEqual(s2[0], (3,1))
        self.assertEqual(s2[1], (2,1))
        self.assertEqual(s2[2], (1,2))

if __name__ == '__main__':
    unittest.main()