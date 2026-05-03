import json
import unittest

from ziderdata.encoding import decode_median, decode_path, encode_median, encode_path

SAMPLE_PATH = 'M 323 706 Q 325 699 328 694 Q 334 686 367 671 Q 474 619 574 561 Q 600 545 617 543 Q 627 545 631 559 Q 641 576 613 621 Q 575 684 334 717 Q 321 719 323 706 Z'
SAMPLE_MEDIAN = [[336, 704], [450, 666], [554, 620], [587, 595], [614, 558]]


class TestEncodePath(unittest.TestCase):
    def test_roundtrip_m_z(self):
        path = 'M 100 200 Z'
        self.assertEqual(decode_path(encode_path(path)), path)

    def test_roundtrip_q(self):
        path = 'M 100 200 Q 150 250 200 300 Z'
        self.assertEqual(decode_path(encode_path(path)), path)

    def test_roundtrip_l(self):
        path = 'M 100 200 L 300 400 Z'
        self.assertEqual(decode_path(encode_path(path)), path)

    def test_roundtrip_c(self):
        path = 'M 100 200 C 110 210 120 220 130 230 Z'
        self.assertEqual(decode_path(encode_path(path)), path)

    def test_roundtrip_real_path(self):
        self.assertEqual(decode_path(encode_path(SAMPLE_PATH)), SAMPLE_PATH)

    def test_smaller_than_text(self):
        encoded = encode_path(SAMPLE_PATH)
        self.assertLess(len(encoded), len(SAMPLE_PATH.encode('utf-8')))

    def test_boundary_coordinates(self):
        path = 'M 0 0 L 1023 1023 Z'
        self.assertEqual(decode_path(encode_path(path)), path)

    def test_negative_coordinates(self):
        path = 'M 500 500 Q 472 -10 423 -59 Z'
        self.assertEqual(decode_path(encode_path(path)), path)


class TestEncodeMedian(unittest.TestCase):
    def test_roundtrip_single_point(self):
        median = [[100, 200]]
        self.assertEqual(decode_median(encode_median(median)), median)

    def test_roundtrip_multiple_points(self):
        self.assertEqual(decode_median(encode_median(SAMPLE_MEDIAN)), SAMPLE_MEDIAN)

    def test_smaller_than_json(self):
        encoded = encode_median(SAMPLE_MEDIAN)
        self.assertLess(len(encoded), len(json.dumps(SAMPLE_MEDIAN).encode('utf-8')))

    def test_byte_size(self):
        median = [[1, 2], [3, 4], [5, 6]]
        self.assertEqual(len(encode_median(median)), 9)  # 3 points × 22 bits = 66 bits → 9 bytes


if __name__ == '__main__':
    unittest.main()
