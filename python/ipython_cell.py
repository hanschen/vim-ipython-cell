from __future__ import print_function

from subprocess import Popen, PIPE
import sys

import vim


def execute_cell(jump_to_next_cell=False):
    """Execute code within cell.

    Parameters
    ----------
    jump_to_next_cell : bool
        If True, jump to the beginning of the next cell after executing the
        current cell.

    """
    current_row, _ = vim.current.window.cursor
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

    cell_indices = _get_current_cell_boundary(current_row, cell_boundaries)
    cell_start, cell_end, next_cell_start = cell_indices

    cell = "\n".join(buffer[cell_start-1:cell_end])
    _copy_to_clipboard(cell)
    _slimesend("%paste -q")

    if jump_to_next_cell:
        vim.current.window.cursor = (next_cell_start, 0)


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
    """Copy ``string`` to primary clipboard using xsel or xclip.

    Parameters
    ----------
    string : str
        String to copy to clipboard.
    prefer_program : None or str
        Which external program to use to copy to clipboard.

    """
    PROGRAMS = [
        ["xsel", "-i", "--clipboard"],
        ["xclip", "-i", "-selection", "clipboard"],
    ]

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
        _error("Could not find xsel or xclip executable")
        return

    byte = string.encode()
    p.communicate(input=byte)


def _error(*args, **kwargs):
    """Print error message to stderr. Same parameters as print."""
    print(*args, file=sys.stderr, **kwargs)


def _get_current_cell_boundary(current_row, cell_boundaries):
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
    int:
        Start index for the next cell.

    """
    cell_boundaries = list(cell_boundaries)

    # Include beginning of file as a cell boundary
    cell_boundaries.append(1)

    cell_boundaries = sorted(set(cell_boundaries))

    cell_start = [boundary for boundary in cell_boundaries
                  if boundary <= current_row][-1]

    next_cell_start = [boundary for boundary in cell_boundaries
                       if boundary > current_row]

    if next_cell_start:
        next_cell_start = next_cell_start[0]
        cell_end = next_cell_start - 1
    else:
        next_cell_start = current_row
        cell_end = None  # end of file

    return cell_start, cell_end, next_cell_start


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


def _slimesend(string):
    """Send ``string`` using vim-slime."""
    vim.command('SlimeSend1 {}'.format(string))
