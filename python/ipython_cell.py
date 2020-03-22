from __future__ import print_function

from subprocess import Popen, PIPE
import sys

try:
    import vim
except ImportError:
    print("warning: importing ipython_cell outside vim, some functions will "
          "not work")


CTRL_P = '\x10'
CTRL_U = '\x15'


def execute_cell(use_cpaste=False):
    """Execute code within cell.

    Parameters
    ----------
    use_cpaste : bool
        Set to True to use %cpaste instead of %paste to send cell to ipython.

    """
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    start_row, end_row = _get_current_cell_boundaries(current_row,
                                                      cell_boundaries)

    # Required for Python 2
    if end_row is None:
        end_row = len(vim.current.buffer)

    # start_row and end_row are 1-indexed, need to subtract 1
    cell = "\n".join(vim.current.buffer[start_row-1:end_row])

    if not use_cpaste:
        if cell:
            _copy_to_clipboard(cell)
            _slimesend("%paste -q")
        else:
            _slimesend("# empty cell")
    else:
        try:
            slime_python_ipython = vim.eval('g:slime_python_ipython')
        except vim.error:
            slime_python_ipython = False

        if slime_python_ipython:
            _slimesend(cell)
        else:
            _slimesend("%cpaste -q")
            # Send 25 lines at a time to avoid potential issues when sending
            # a large number of lines
            remaining_chunks = cell.splitlines()
            while remaining_chunks:
                chunk = remaining_chunks[:25]
                remaining_chunks[:25] = []
                _slimesend("\n".join(chunk))
            _slimesend("--")


def jump_next_cell():
    """Move cursor to the start of the next cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    next_cell_row = _get_next_cell(current_row, cell_boundaries)
    if next_cell_row != current_row:
        vim.current.window.cursor = (next_cell_row, 0)


def jump_prev_cell():
    """Move cursor to the start of the current or previous cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    prev_cell_row = _get_prev_cell(current_row, cell_boundaries)
    if prev_cell_row != current_row:
        vim.current.window.cursor = (prev_cell_row, 0)


def previous_command():
    """Run previous command."""
    _slimesend(CTRL_P)


def restart_ipython():
    """Quit ipython and start it again."""
    _slimesend("exit")
    _slimesend(CTRL_P)


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
    """Copy ``string`` to primary clipboard using pbcopy, xclip or xsel.

    Parameters
    ----------
    string : str
        String to copy to clipboard.
    prefer_program : None or str
        Which external program to use to copy to clipboard.

    """
    PROGRAMS = [
        ["pbcopy"],
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
    """Return a list of rows (1-indexed) for all cell boundaries."""
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

    # Include beginning of file as a cell boundary
    cell_boundaries.append(1)

    return sorted(set(cell_boundaries))


def _get_current_cell_boundaries(current_row, cell_boundaries):
    """Return the start and end row numbers (1-indexed) for the current cell.

    Parameters
    ----------
    current_row : int
        Current row number.
    cell_boundaries : list
        A list of row numbers for the cell boundaries.

    Returns
    -------
    int:
        Start row number for the current cell.
    int:
        End row number for the current cell.

    """
    next_cell_row = None
    for boundary in cell_boundaries:
        if boundary <= current_row:
            start_row = boundary
        else:
            next_cell_row = boundary
            break

    if next_cell_row is None:
        end_row = None  # end of file
    else:
        end_row = next_cell_row - 1

    return start_row, end_row


def _get_next_cell(current_row, cell_boundaries):
    """Return start row number of the next cell.

    If there is no next cell, the current row number is returned.

    Parameters
    ----------
    current_row : int
        Current row number.
    cell_boundaries : list
        A list of row numbers for the cell boundaries.

    Returns
    -------
    int:
        Start row number for the next cell.

    """
    next_cell_row = None
    for boundary in cell_boundaries:
        if boundary > current_row:
            next_cell_row = boundary
            break

    if next_cell_row is None:
        return current_row
    else:
        return next_cell_row


def _get_prev_cell(current_row, cell_boundaries):
    """Return start row number of the current or previous cell.

    If ``current_row`` is a cell header, the previous cell header is returned,
    otherwise the current cell header is returned.

    If there is no previous cell, the current row number is returned.

    Parameters
    ----------
    current_row : int
        Current row number.
    cell_boundaries : list
        A list of row numbers for the cell boundaries.

    Returns
    -------
    int:
        Start row number for the current or previous cell.

    """
    prev_cell_row = None
    for boundary in cell_boundaries:
        if boundary < current_row:
            prev_cell_row = boundary
        else:
            break

    if prev_cell_row is None:
        return current_row
    else:
        return prev_cell_row


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
            rows_containing_tag.append(i + 1)  # rows are counted from 1

    return rows_containing_tag


def _get_rows_with_marks(buffer, valid_marks):
    """Return a list of row numbers for lines containing a mark.

    Parameters
    ----------
    buffer : buffer object
        An object with a ``mark`` method.
    valid_marks : list
        A list of marks to search for.

    Returns
    -------
    list:
        List of row numbers.

    """
    rows_containing_marks = []
    for mark in valid_marks:
        mark_loc = buffer.mark(mark)
        if mark_loc is not None:
            rows_containing_marks.append(mark_loc[0])

    return rows_containing_marks


def _slimesend(string):
    """Send ``string`` using vim-slime."""
    if not string:
        return

    try:
        vim.command('SlimeSend1 ' + CTRL_U + '{}'.format(string))
    except vim.error:
        _error("Could not execute SlimeSend1 command, make sure vim-slime is "
               "installed")
