from __future__ import absolute_import

import unittest

from python import ipython_cell as ic


CELL_BOUNDARIES = [1, 4, 8, 15, 20]
TAG = '##'


class Buffer(object):
    """A simple buffer-like object for testing."""
    def __init__(self, contents=None, marks=None):
        if contents is None:
            contents = []
        if marks is None:
            marks = {}
        self.contents = contents
        self.marks = marks

    def __iter__(self):
        for element in self.contents:
            yield element

    def mark(self, mark):
        return self.marks.get(mark, None)


class TestIPythonCell(unittest.TestCase):
    def test_get_current_cell_boundaries_cursor_start_of_cell(self):
        current_row = 8
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 8)
        self.assertEqual(cell_end, 14)

    def test_get_current_cell_boundaries_cursor_middle_of_cell(self):
        current_row = 10
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 8)
        self.assertEqual(cell_end, 14)

    def test_get_current_cell_boundaries_cursor_end_of_cell(self):
        current_row = 14
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 8)
        self.assertEqual(cell_end, 14)

    def test_get_current_cell_boundaries_cursor_first_cell(self):
        current_row = 2
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 1)
        self.assertEqual(cell_end, 3)

    def test_get_current_cell_boundaries_cursor_last_cell(self):
        current_row = 20
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 20)
        self.assertEqual(cell_end, None)

    def test_get_current_cell_boundaries_cursor_start_of_file(self):
        current_row = 1
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 1)
        self.assertEqual(cell_end, 3)

    def test_get_current_cell_boundaries_cursor_end_of_file(self):
        current_row = 99
        cell_start, cell_end = ic._get_current_cell_boundaries(current_row,
                                                               CELL_BOUNDARIES)
        self.assertEqual(cell_start, 20)
        self.assertEqual(cell_end, None)

    def test_get_next_cell_cursor_start_of_cell(self):
        current_row = 8
        next_cell = ic._get_next_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(next_cell, 15)

    def test_get_next_cell_cursor_middle_of_cell(self):
        current_row = 12
        next_cell = ic._get_next_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(next_cell, 15)

    def test_get_next_cell_cursor_end_of_cell(self):
        current_row = 14
        next_cell = ic._get_next_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(next_cell, 15)

    def test_get_prev_cell_cursor_start_of_cell(self):
        current_row = 8
        prev_cell = ic._get_prev_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(prev_cell, 4)

    def test_get_prev_cell_cursor_middle_of_cell(self):
        current_row = 10
        prev_cell = ic._get_prev_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(prev_cell, 8)

    def test_get_prev_cell_cursor_end_of_cell(self):
        current_row = 14
        prev_cell = ic._get_prev_cell(current_row, CELL_BOUNDARIES)
        self.assertEqual(prev_cell, 8)

    def test_get_rows_with_tag(self):
        buffer = [
            "",
            "## cell header",
            "print('cell content')",
        ]
        rows = ic._get_rows_with_tag(buffer, "##")
        self.assertEqual(rows, [2])

    def test_get_rows_with_tag_multiple_rows(self):
        buffer = [
            "## cell header 1",
            "print('cell content')",
            "",
            "## cell header 2",
            "# this is a normal comment",
            "numbers = [1, 2, 3]",
            "for i in numbers:",
            "    ## cell header 3",
            "    print(i)",
        ]
        rows = ic._get_rows_with_tag(buffer, "##")
        self.assertEqual(rows, [1, 4, 8])

    def test_get_rows_with_marks(self):
        marks = {
            'a': (2, 1),
        }
        buffer = Buffer(marks=marks)
        rows = ic._get_rows_with_marks(buffer, valid_marks='abcdefg')
        self.assertEqual(rows, [2])

    def test_get_rows_with_marks_multiple_rows(self):
        marks = {
            'a': (1, 1),
            'b': (4, 1),
            'c': (8, 1),
        }
        buffer = Buffer(marks=marks)
        rows = ic._get_rows_with_marks(buffer, valid_marks='abcdefg')
        self.assertEqual(rows, [1, 4, 8])
