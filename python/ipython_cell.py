from __future__ import print_function

import re
from subprocess import Popen, PIPE
import sys

try:
    import vim
except ImportError:
    print("warning: importing ipython_cell outside vim, some functions will "
          "not work")


CTRL_N = '\x0e'
CTRL_O = '\x0f'
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
    cell_boundaries = _get_cell_boundaries(auto_include_first_line=False)

    # Include first line of buffer if necessary
    first_line_contains_cell_header = 1 in cell_boundaries
    if not first_line_contains_cell_header:
        cell_boundaries.insert(0, 1)

    start_row, end_row = _get_current_cell_boundaries(current_row,
                                                      cell_boundaries)
    # Required for Python 2
    if end_row is None:
        end_row = len(vim.current.buffer)

    # Send tags?
    if (vim.eval('g:ipython_cell_delimit_cells_by') == 'tags'
            and vim.eval('g:ipython_cell_send_cell_headers') != '0'):
        if start_row == 1 and not first_line_contains_cell_header:
            cell_header = "# cell 0"
        else:
            cell_header = vim.current.buffer[start_row-1]
        if vim.eval('g:ipython_cell_send_ctrl_u') != '0':
            _slimesend0(CTRL_U)
        _slimesend0(cell_header)
        _slimesend0(CTRL_O)
        _slimesend0(CTRL_N)

        if not use_cpaste:
            # Create a new line to account for Ctrl-U
            _slimesend0(CTRL_O)
            _slimesend0(CTRL_N)

    # Do not send the tag over
    if vim.eval('g:ipython_cell_delimit_cells_by') == 'tags':
        if first_line_contains_cell_header or start_row != 1:
            start_row += 1

    # start_row and end_row are 1-indexed, need to subtract 1
    cell = "\n".join(vim.current.buffer[start_row-1:end_row])

    if not use_cpaste:
        if cell:
            _copy_to_clipboard(cell)
            paste_command = vim.eval('g:ipython_cell_cell_command')
            _slimesend(paste_command)
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
        try:
            vim.current.window.cursor = (next_cell_row, 0)
        except vim.error:
            vim.command("echo 'Cell header is outside the buffer boundaries'")


def jump_prev_cell():
    """Move cursor to the start of the current or previous cell."""
    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    prev_cell_row = _get_prev_cell(current_row, cell_boundaries)
    if prev_cell_row != current_row:
        try:
            vim.current.window.cursor = (prev_cell_row, 0)
        except vim.error:
            vim.command("echo 'Cell header is outside the buffer boundaries'")


def insert_cell_below():
    insert_tag = vim.eval('g:ipython_cell_insert_tag')

    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries()
    _, end_row = _get_current_cell_boundaries(current_row, cell_boundaries)

    # Required for Python 2
    if end_row is None:
        end_row = len(vim.current.buffer)

    # Jump cursor to end_row
    if end_row != current_row:
        try:
            vim.current.window.cursor = (end_row, 0)
        except vim.error:
            vim.command("echo 'Cell header is outside the buffer boundaries'")

    # Insert tag bellow
    if vim.current.line != '':
        vim.command("normal!o")
    current_row, _ = vim.current.window.cursor
    if current_row != 1:
        vim.command("normal!o")
        current_row += 1
    if current_row != len(vim.current.buffer):
        vim.command("normal!O")
    vim.command("normal!i" + insert_tag)


def insert_cell_above():
    insert_tag = vim.eval('g:ipython_cell_insert_tag')

    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries(auto_include_first_line=False)

    # Include first line of buffer if necessary
    first_line_contains_cell_header = 1 in cell_boundaries
    if not first_line_contains_cell_header:
        cell_boundaries.insert(0, 1)

    start_row, _ = _get_current_cell_boundaries(current_row, cell_boundaries)

    # If the cursor not at the header of the current cell,
    # we move the cursor to the header
    if current_row != start_row:
        try:
            vim.current.window.cursor = (start_row, 0)
        except vim.error:
            vim.command("echo 'Cell header is outside the buffer boundaries'")

    # If the start_row is the first line and not contains header
    # We instert a cell header for the current cell
    if start_row == 1 and not first_line_contains_cell_header:
        vim.command("normal!O")
        vim.command("normal!i" + insert_tag)
    else:
        vim.command("normal!O")
        vim.command("normal!O")
        vim.command("normal!i" + insert_tag)

def to_markdown():
    insert_tag = vim.eval('g:ipython_cell_insert_tag')

    current_row, _ = vim.current.window.cursor
    cell_boundaries = _get_cell_boundaries(auto_include_first_line=False)

    # Include first line of buffer if necessary
    first_line_contains_cell_header = 1 in cell_boundaries
    if not first_line_contains_cell_header:
        cell_boundaries.insert(0, 1)

    start_row, end_row = _get_current_cell_boundaries(current_row, cell_boundaries)

    if end_row is None:
        end_row = len(vim.current.buffer)

    # Switch to end_row first as start_row will not change after insert """ line
    if current_row != end_row:
        try:
            vim.current.window.cursor = (end_row, 0)
        except vim.error:
            vim.command("echo 'Cell is outside the buffer boundaries'")

    if vim.current.line != '':
        vim.command("normal!o")

    current_row, _ = vim.current.window.cursor
    if current_row != len(vim.current.buffer):
        vim.command('normal!O')
    vim.command('normal!i"""')

    # We move the cursor to the header
    try:
        vim.current.window.cursor = (start_row, 0)
    except vim.error:
        vim.command("echo 'Cell is outside the buffer boundaries'")

    # If the start_row is the first line and not contains header
    # We instert a cell header for the current cell
    if start_row == 1 and not first_line_contains_cell_header:
        vim.command("normal!O")
        vim.command("normal!i" + insert_tag)

    # Now we at the header row
    vim.command('normal!A [markdown]')
    vim.command('normal!o')
    vim.command('normal!i"""')
    vim.command('normal!j')

def previous_command():
    """Run previous command."""
    _slimesend(CTRL_P)


def restart_ipython():
    """Quit ipython and start it again."""
    _slimesend("exit")
    _slimesend(CTRL_P)


def run(*args):
    """Run script."""
    options = " ".join(args)
    run_command = vim.eval('g:ipython_cell_run_command')
    run_command = run_command.format(options=options,
                                     filepath=vim.current.buffer.name)
    _slimesend(run_command)


def clear():
    """Clear screen."""
    _slimesend("%clear")


def close_all():
    """Close all figure windows."""
    _slimesend("plt.close('all')")


def _copy_to_clipboard(string, prefer_program=None):
    """Copy ``string`` to primary clipboard.

    If the +clipboard feature flag in Vim is present, the function will use Vim
    to copy the string, otherwise it will attempt to use an external program.

    Parameters
    ----------
    string : str
        String to copy to clipboard.
    prefer_program : None or str
        Which external program to use to copy to clipboard if +clipboard is
        absent.

    """
    if vim.eval('g:ipython_cell_prefer_external_copy') != '0':
        _copy_to_clipboard_external(string, prefer_program)
    else:
        copy_successful = _copy_to_clipboard_internal(string)
        if not copy_successful:
            _copy_to_clipboard_external(string, prefer_program)


def _copy_to_clipboard_external(string, prefer_program=None):
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


def _copy_to_clipboard_internal(string):
    """Copy ``string`` to primary clipboard using Vim.

    Return True if the copy is successful, otherwise return False.
    """
    if vim.eval("has('clipboard')") == '1':
        vim.command('let @+=' + _sanitize(string))
        return True
    else:
        return False


def _error(*args, **kwargs):
    """Print error message to stderr. Same parameters as print."""
    print(*args, file=sys.stderr, **kwargs)


def _get_cell_boundaries(auto_include_first_line=True):
    """Return a list of rows (1-indexed) for all cell boundaries.

    Parameters
    ----------
    auto_include_first_line : bool
        If True (default), include first line of the buffer automatically in
        the returned list even if it does not contain a cell header.

    """
    buffer = vim.current.buffer
    delimiter = vim.eval('g:ipython_cell_delimit_cells_by').strip()

    if delimiter == 'marks':
        valid_marks = vim.eval('g:ipython_cell_valid_marks').strip()
        cell_boundaries = _get_rows_with_marks(buffer, valid_marks)
    elif delimiter == 'tags':
        tag = vim.eval('g:ipython_cell_tag')
        regex_option = vim.eval('g:ipython_cell_regex').strip().lower()
        use_regex = regex_option in ['1', 'y', 'yes', 't', 'true']
        cell_boundaries = _get_rows_with_tag(buffer, tag, use_regex)
    else:
        _error("Invalid option value for g:ipython_cell_valid_marks: {}"
               .format(delimiter))
        return

    if auto_include_first_line:
        # Include beginning of buffer as a cell boundary
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


def _get_rows_with_tag(buffer, tags, use_regex=False):
    """Return a list of row numbers for lines containing tag in ``tags``.

    Parameters
    ----------
    buffer : iterable
        An iterable object that contains the lines of a buffer.
    tags : list or str
        Tag(s) to search for.

    Returns
    -------
    list:
        List of row numbers.

    """
    if not isinstance(tags, list):
        tags = [tags]

    rows_containing_tag = []
    for i, line in enumerate(buffer):
        for tag in tags:
            if not use_regex:
                tag_found = tag in line
            else:
                match = re.search(tag, line)
                tag_found = match is not None

            if tag_found:
                rows_containing_tag.append(i + 1)  # rows are counted from 1
                break

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
        if mark_loc is not None and mark_loc[0] != 0:
            rows_containing_marks.append(mark_loc[0])

    return rows_containing_marks


def _sanitize(string):
    return "'" + re.sub(re.compile("'"), "''", string) + "'"


def _slimesend(string):
    """Send ``string`` using vim-slime."""
    if not string:
        return

    if vim.eval('g:ipython_cell_send_ctrl_u') != '0':
        lineclear = CTRL_U
    else:
        lineclear = ""

    try:
        vim.command('SlimeSend1 ' + lineclear + '{}'.format(string))
    except vim.error:
        _error("Could not execute SlimeSend1 command, make sure vim-slime is "
               "installed")


def _slimesend0(string):
    """Similar to _slimesend, but use SlimeSend0 (do not include carriage
    return) instead of SlimeSend1, and do not send Ctrl-U.
    """
    if not string:
        return

    try:
        vim.command('SlimeSend0 "{}"'.format(string))
    except vim.error:
        _error("Could not execute SlimeSend0 command, make sure vim-slime is "
               "installed")
