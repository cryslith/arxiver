#!/usr/bin/env python3

import unittest
from arxiver import strip_comments

class TestArxiver(unittest.TestCase):
    def test_strip_comments(self):
        self.assertEqual(strip_comments(r'a%b'), r'a')
        self.assertEqual(strip_comments(r'a\%b'), r'a\%b')
        self.assertEqual(strip_comments(r'a\\%b'), r'a\\')
        self.assertEqual(strip_comments(r'a\\\%b'), r'a\\\%b')
        self.assertEqual(strip_comments(r'a\\\\%b'), r'a\\\\')
        self.assertEqual(strip_comments(r'%b'), r'')
        self.assertEqual(strip_comments(r'\%b'), r'\%b')
        self.assertEqual(strip_comments(r'\\%b'), r'\\')
        self.assertEqual(strip_comments(r'\\\%b'), r'\\\%b')
        self.assertEqual(strip_comments(r'\\\\%b'), r'\\\\')

        self.assertEqual(strip_comments('a%\nb'), 'ab')

if __name__ == '__main__':
    unittest.main()
