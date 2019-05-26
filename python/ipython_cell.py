from __future__ import print_function

from subprocess import Popen, PIPE
import sys

import vim


def execute_cell():
    """Execute code within cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    cell_start, cell_end = _get_current_cell_boundaries(current_row,
                                                        cell_boundaries)

    # Required for Python 2
    if cell_end is None:
        cell_end = len(vim.current.buffer)

    cell = "\n".join(vim.current.buffer[cell_start-1:cell_end])
    _copy_to_clipboard(cell)
    _slimesend("%paste -q")


def jump_next_cell():
    """Move cursor to the start of the next cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    next_cell_start = _get_next_cell(current_row, cell_boundaries)
    if next_cell_start != current_row:
        vim.current.window.cursor = (next_cell_start, 0)


def jump_prev_cell():
    """Move cursor to the start of the current or previous cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    prev_cell_start = _get_prev_cell(current_row, cell_boundaries)
    if prev_cell_start != current_row:
        vim.current.window.cursor = (prev_cell_start, 0)


def run(*args):
    """Run script."""
    opts = " ".join(args)
    _slimesend("%run {} {}".format(opts, vim.current.buffer.name))


def clear():
    """Clear screen."""
    _slimesend("%clear")


def close_all():
    """Close all figure windows."""
    _slimesend("plt.close('all')")


def _copy_to_clipboard(string, prefer_program=None):
    """Copy ``string`` to primary clipboard using xclip or xsel.

    Parameters
    ----------
    string : str
        String to copy to clipboard.
    prefer_program : None or str
        Which external program to use to copy to clipboard.

    """
    PROGRAMS = [
        ["xclip", "-i", "-selection", "clipboard"],
        ["xsel", "-i", "--clipboard"],
    ]

    # Python 2 compatibility
    try:
        FileNotFoundError
    except NameError:
        FileNotFoundError = OSError

    for program in PROGRAMS:
        if prefer_program is not None and program[0] != prefer_program:
            continue

        try:
            p = Popen(program, stdin=PIPE)
        except FileNotFoundError:
            program_found = False
        else:
            program_found = True
            break

    if not program_found:
        _error("Could not find xclip or xsel executable")
        return

    byte = string.encode()
    p.communicate(input=byte)


def _error(*args, **kwargs):
    """Print error message to stderr. Same parameters as print."""
    print(*args, file=sys.stderr, **kwargs)


def _get_cell_boundaries():
    """Return a list of row indices for all cell boundaries."""
    buffer = vim.current.buffer
    delimiter = vim.eval('g:ipython_cell_delimit_cells_by').strip()

    if delimiter == 'marks':
        valid_marks = vim.eval('g:ipython_cell_valid_marks').strip()
        cell_boundaries = _get_rows_with_marks(buffer, valid_marks)
    elif delimiter == 'tags':
        tag = vim.eval('g:ipython_cell_tag')
        cell_boundaries = _get_rows_with_tag(buffer, tag)
    else:
        _error("Invalid option value for g:ipython_cell_valid_marks: {}"
               .format(delimiter))
        return

    return cell_boundaries


def _get_current_cell_boundaries(current_row, cell_boundaries):
    """Return the start and end indices for the current cell and the start
    index for the next cell.

    Parameters
    ----------
    current_row : int
        Index of the current row.
    cell_boundaries : list
        A list of indices for the cell boundaries.

    Returns
    -------
    int:
        Start index for the current cell.
    int:
        End index for the current cell.

    """
    cell_boundaries = _get_sorted_unique_cell_boundaries(cell_boundaries)

    next_cell_start = None
    for boundary in cell_boundaries:
        if boundary <= current_row:
            cell_start = boundary
        else:
            next_cell_start = boundary
            break

    if next_cell_start is None:
        cell_end = None  # end of file
    else:
        cell_end = next_cell_start - 1

    return cell_start, cell_end


def _get_next_cell(current_row, cell_boundaries):
    """Return start index of the next cell.

    If there is no next cell, the current row is returned.

    Parameters
    ----------
    current_row : int
        Index of the current row.
    cell_boundaries : list
        A list of indices for the cell boundaries.

    Returns
    -------
    int:
        Start index for the next cell.

    """
    cell_boundaries = _get_sorted_unique_cell_boundaries(cell_boundaries)

    next_cell_start = None
    for boundary in cell_boundaries:
        if boundary > current_row:
            next_cell_start = boundary
            break

    if next_cell_start is None:
        return current_row
    else:
        return next_cell_start


def _get_prev_cell(current_row, cell_boundaries):
    """Return start index of the current or previous cell.

    If ``current_row`` is on the same line as the cell header, the previous
    cell header is returned, otherwise the current cell header is returned.

    If there is no previous cell, the current row is returned.

    Parameters
    ----------
    current_row : int
        Index of the current row.
    cell_boundaries : list
        A list of indices for the cell boundaries.

    Returns
    -------
    int:
        Start index for the previous cell.

    """
    cell_boundaries = _get_sorted_unique_cell_boundaries(cell_boundaries)

    prev_cell_start = None
    for boundary in cell_boundaries:
        if boundary < current_row:
            prev_cell_start = boundary
        else:
            break

    if prev_cell_start is None:
        return current_row
    else:
        return prev_cell_start


def _get_rows_with_tag(buffer, tag):
    """Return a list of row numbers for lines containing ``tag``.

    Parameters
    ----------
    buffer : iterable
        An iterable object that contains the lines of a buffer.
    tag : str
        Tag to search for.

    Returns
    -------
    list:
        List of row numbers.

    """
    rows_containing_tag = []
    for i, line in enumerate(buffer):
        if tag in line:
            rows_containing_tag.append(i + 1)  # lines are counted from 1

    return rows_containing_tag


def _get_rows_with_marks(buffer, valid_marks):
    """Return a list of row indices for lines containing a mark.

    Parameters
    ----------
    buffer : buffer object
        An object with a ``mark`` method.
    valid_marks : list
        A list of marks to search for.

    Returns
    -------
    list:
        List of row indices.

    """
    rows_containing_marks = []
    for mark in valid_marks:
        mark_loc = buffer.mark(mark)
        if mark_loc is not None:
            rows_containing_marks.append(mark_loc[0])

    return rows_containing_marks


def _get_sorted_unique_cell_boundaries(cell_boundaries):
    """Return a list of unique and sorted cell boundaries, including the first
    line of the file as a boundary.

    Parameters
    ----------
    cell_boundaries : list
        A list of indices for the cell boundaries.

    Returns
    -------
    list:
        A list of unique and sorted indices for the cell boundaries.

    """
    cell_boundaries = list(cell_boundaries)

    # Include beginning of file as a cell boundary
    cell_boundaries.append(1)

    return sorted(set(cell_boundaries))


def _slimesend(string):
    """Send ``string`` using vim-slime."""
    vim.command('SlimeSend1 {}'.format(string))
