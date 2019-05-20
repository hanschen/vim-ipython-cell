ipython-cell
============

Seamlessly run Python code from Vim in IPython, including executing individual
code cells similar to Jupyter notebooks and MATLAB.


Demo
----

TODO


Requirements
------------

ipython-cell requires Vim or Neovim to be compiled with Python 2 or Python 3
support (`+python` or `+python3` when running `vim --version`). If both Python
versions are found, the plugin will prefer Python 3.

Additionally, the cell execution feature requires [xclip] or [xsel] to be
installed (preferring the former).

ipython-cell depends on [vim-slime] to send the code to IPython (see
Installation instructions below).

[xclip]: https://github.com/astrand/xclip
[xsel]: https://github.com/kfish/xsel
[vim-slime]: https://github.com/jpalardy/vim-slime


Installation
------------

It is easiest to install ipython-cell using a plugin manager. I personally
recommend [vim-plug]. See respective plugin manager's documentation for more
information about how to install plugins.

### [vim-plug]

~~~vim
Plug 'jpalardy/vim-slime', { 'for': 'python' }
Plug 'hanschen/vim-ipython-cell', { 'for': 'python' }
~~~

### [Vundle]

~~~vim
Plugin 'jpalardy/vim-slime'
Plugin 'hanschen/vim-ipython-cell'
~~~

### [NeoBundle]

~~~vim
NeoBundle 'jpalardy/vim-slime', { 'on_ft': 'python' }
NeoBundle 'hanschen/vim-ipython-cell', { 'on_ft': 'python' }
~~~

### [Dein]

~~~vim
call dein#add('jpalardy/vim-slime', { 'on_ft': 'python' })
call dein#add('hanschen/vim-ipython-cell', { 'on_ft': 'python' })
~~~

### [Pathogen]

~~~sh
cd ~/.vim/bundle
git clone https://github.com/hanschen/vim-ipython-cell.git
~~~

[vim-plug]: https://github.com/junegunn/vim-plug
[Vundle]: https://github.com/VundleVim/Vundle.vim
[NeoBundle]: https://github.com/Shougo/neobundle.vim
[Dein]: https://github.com/Shougo/dein.vim
[Pathogen]: https://github.com/tpope/vim-pathogen


Usage
-----

ipython-cell sends code from Vim to IPython running in a GNU screen / tmux /
whimrepl / ConEmu session / NeoVim Terminal / Vim Terminal using [vim-slime].
It is recommended that you familiarize yourself with [vim-slime] first before
using ipython-cell. Once you grasp the basics of vim-slime, using ipython-cell
will be a breeze.

(I personally prefer tmux, but you will find screen installed on most *nix
systems.)

The plugin includes the following commands:

    :IPythonCellExecuteCell

Execute the current code cell in IPython.

    :IPythonCellExecuteCellJump

Execute the current code cell in IPython and jump to the next cell.

    :IPythonCellExecuteRun

Run the whole script in IPython.

    :IPythonCellExecuteRunTime

Run and time the whole script in IPython.

    :IPythonCellExecuteClear

Clear IPython screen.

    :IPythonCellExecuteClose

Close all figure windows.

These commands can be bound to key mappings, see Example configuration below.

[vim-slime]: https://github.com/jpalardy/vim-slime


Configuration
-------------

    g:ipython_cell_delimit_cells_by

If cells should be delimited by `marks` or `tags`. Default: `marks`

    g:ipython_cell_tag

If cells are delimited by tags, specify the format of the tags. Default: `##`

    g:ipython_cell_valid_marks

If cells are delimited by marks, specify which marks to use.
Default: `abcdefghijklmnopqrstuvqxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`


Example vim configuration
-------------------------

Here's an example of how to configure your `.vimrc` to use this plugin. Adapt
it to suit your needs.

~~~vim
if has('autocmd')
    filetype plugin indent on
endif

" Load plugins using vim-plug
call plug#begin('~/.vim/plugged')
Plug 'jpalardy/vim-slime' { 'for': 'python' }
Plug 'hanschen/vim-ipython-cell' { 'for': 'python' }
call plug#end()

"------------------------------------------------------------------------------
" slime configuration 
"------------------------------------------------------------------------------
" always use tmux
let g:slime_target = "tmux"

" fix paste issues in ipython
let g:slime_python_ipython = 1

" always send text to the top-right pane in the current tmux tab without asking
" for confirmation
let g:slime_default_config = {
            \ "socket_name": get(split($TMUX, ","), 0),
            \ "target_pane": "{top-right}" }
let g:slime_dont_ask_default = 1

"------------------------------------------------------------------------------
" ipython-cell configuration
"------------------------------------------------------------------------------
" map ,r to run script
autocmd FileType python nmap <buffer> ,r :IPythonCellRun<CR>

" map ,c to execute the current cell
autocmd FileType python nmap <buffer> ,c :IPythonCellExecuteCell<CR>

" map ,C to execute the current cell and jump to the next cell
autocmd FileType python nmap <buffer> ,C :IPythonCellExecuteCellJump<CR>

" map ,l to clear IPython screen
autocmd FileType python nmap <buffer> ,l :IPythonCellClear<CR>

" map ,x to close all Matplotlib figure windows
autocmd FileType python nmap <buffer> ,x :IPythonCellClose<CR>

~~~

Note that the mappings work only in normal mode. The extra
`autocmd FileType python` and `<buffer>` parts are there just to ensure that
the mapping are defined only for Python files. You can also move these
mappings to `~/.vim/ftplugin/python.vim` and then drop all
`autocmd FileType python`.

If you come from the MATLAB world, you may want e.g. F5 to save and run the
script regardless if you are in insert or normal mode:

~~~vim
" map <F5> to save and run script
autocmd FileType python map <buffer> <F5> :w<CR>:IPythonCellRun<CR>
autocmd FileType python imap <buffer> <F5> <C-o>:w<CR><C-o>:IPythonCellRun<CR>
~~~


FAQ
---

> How do I show the marks in the left-most column?

Use the vim-signature plugin: https://github.com/kshenoy/vim-signature

> How to send only the current line or selected lines to IPython?

Use the features provided by vim-slime. The default mapping `C-c C-c` (hold
down Ctrl and tap the C key twice) will send the current paragraph or the
selected lines to IPython. See `:help slime` for more information.

> Why do I get "name 'plt' is not defined" when I try to close figures?

ipython-cell assumes that you have imported `matplotlib.pyplot` as `plt` in
IPython. If you prefer to import `matplotlib.pyplot` differently, you can
achieve the same thing using vim-slime, for example by adding the following to
your .vimrc: >

    autocmd FileType python nmap <buffer> ,x :SlimeSend1 matplotlib.pyplot.close('all')<CR>

> How can I send other commands to IPython, e.g. '%who'?

You can easily send arbitary commands to IPython using the `:SlimeSend1`
provided by vim-slime, e.g. `:SlimeSend1 %who`, and map these commands to
key combinations.

> Why is this plugin written in Python instead of pure Vimscript?

Because I feel more comfortable with Python and don't have the motivation to
learn Vimscript for this plugin. If someone implements a pure Vimscript
version, I would be happy to merge it.


Related plugins
---------------

* [tslime\_ipython] - Similar to ipython-cell but with some slight differences.
  For example, tslime\_ipython sends the whole code cell to IPython's input
  line instead of using `%paste`.
* [vim-ipython] - Advanced two-way integration between Vim and IPython.
* [vim-tmux-navigator] - Seamless navigation between Vim splits and tmux panes.
* [vim-signature] - Display marks in the left-hand column.

[tslime\_ipython]: https://github.com/eldridgejm/tslime_ipython
[vim-tmux-navigator]: https://github.com/christoomey/vim-tmux-navigator
[vim-ipython]: https://github.com/ivanov/vim-ipython
[vim-signature]: https://github.com/kshenoy/vim-signature


Thanks
------

ipython-cell was heavily inspired by [tslime\_ipython].
The code logic to determine which Python version to use was taken from
[YouCompleteMe].

[tslime\_ipython]: https://github.com/eldridgejm/tslime_ipython
[YouCompleteMe]: https://github.com/Valloric/YouCompleteMe
