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
command! -nargs=0 IPythonCellClear call IPythonCellClear()

function! IPythonCellClose()
    exec s:python_command "ipython_cell.close_all()"
endfunction
command! -nargs=0 IPythonCellClose call IPythonCellClose()

function! IPythonCellExecuteCell()
    exec s:python_command "ipython_cell.execute_cell()"
endfunction
command! -nargs=0 IPythonCellExecuteCell call IPythonCellExecuteCell()

function! IPythonCellExecuteCellJump()
    exec s:python_command "ipython_cell.execute_cell()"
    exec s:python_command "ipython_cell.jump_next_cell()"
endfunction
command! -nargs=0 IPythonCellExecuteCellJump call IPythonCellExecuteCellJump()

function! IPythonCellNextCell()
    exec s:python_command "ipython_cell.jump_next_cell()"
endfunction
command! -nargs=0 IPythonCellNextCell call IPythonCellNextCell()

function! IPythonCellPrevCell()
    exec s:python_command "ipython_cell.jump_prev_cell()"
endfunction
command! -nargs=0 IPythonCellPrevCell call IPythonCellPrevCell()

function! IPythonCellRun()
    exec s:python_command "ipython_cell.run()"
endfunction
command! -nargs=0 IPythonCellRun call IPythonCellRun()

function! IPythonCellRunTime()
    exec s:python_command "ipython_cell.run('-t')"
endfunction
command! -nargs=0 IPythonCellRunTime call IPythonCellRunTime()
