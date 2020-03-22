" File:         ipython-cell.vim
" Description:  Execute Python code cells in IPython directly from Vim.
" Author:       Hans Chen <contact@hanschen.org>

if exists('g:loaded_ipython_cell')
    finish
endif
let g:loaded_ipython_cell = 1

if !has("python") && !has("python3")
    echo 'ipython-cell requires py >= 2.7 or py3'
    finish
endif

let g:ipython_cell_delimit_cells_by = get(g:, 'ipython_cell_delimit_cells_by', 'marks')
let g:ipython_cell_tag = get(g:, 'ipython_cell_tag', '##')
let g:ipython_cell_valid_marks = get(g:, 'ipython_cell_valid_marks', 'abcdefghijklmnopqrstuvqxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')

function! s:UsingPython3()
  if has('python3')
    return 1
  endif
    return 0
endfunction

let s:using_python3 = s:UsingPython3()
let s:python_until_eof = s:using_python3 ? "python3 << EOF" : "python << EOF"
let s:python_command = s:using_python3 ? "py3 " : "py "

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

exec s:python_until_eof
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import ipython_cell
EOF

function! IPythonCellClear()
    exec s:python_command "ipython_cell.clear()"
endfunction

function! IPythonCellClose()
    exec s:python_command "ipython_cell.close_all()"
endfunction

function! IPythonCellExecuteCell(...)
    let arg1 = get(a:, 1, 0)
    let arg2 = get(a:, 2, 0)
    exec s:python_command "ipython_cell.execute_cell(" . arg1 . ")"
    if arg2
        exec s:python_command "ipython_cell.jump_next_cell()"
    endif
endfunction

function! IPythonCellNextCell()
    exec s:python_command "ipython_cell.jump_next_cell()"
endfunction

function! IPythonCellPrevCell()
    exec s:python_command "ipython_cell.jump_prev_cell()"
endfunction

function! IPythonCellPrevCommand()
    exec s:python_command "ipython_cell.previous_command()"
endfunction

function! IPythonCellRestart()
    exec s:python_command "ipython_cell.restart_ipython()"
endfunction

function! IPythonCellRun(...)
    exec s:python_command "ipython_cell.run('" . join(a:000, ',') . "')"
endfunction

command! -nargs=0 IPythonCellClear call IPythonCellClear()
command! -nargs=0 IPythonCellClose call IPythonCellClose()
command! -nargs=0 IPythonCellExecuteCell call IPythonCellExecuteCell()
command! -nargs=0 IPythonCellExecuteCellJump call IPythonCellExecuteCell(1, 1)
command! -nargs=0 IPythonCellExecuteCellVerbose call IPythonCellExecuteCell(1)
command! -nargs=0 IPythonCellExecuteCellVerboseJump call IPythonCellExecuteCell(1, 1)
command! -nargs=0 IPythonCellNextCell call IPythonCellNextCell()
command! -nargs=0 IPythonCellPrevCell call IPythonCellPrevCell()
command! -nargs=0 IPythonCellPrevCommand call IPythonCellPrevCommand()
command! -nargs=0 IPythonCellRestart call IPythonCellRestart()
command! -nargs=0 IPythonCellRun call IPythonCellRun()
command! -nargs=0 IPythonCellRunTime call IPythonCellRun('-t')
