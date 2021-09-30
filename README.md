ipython-cell
============

Seamlessly run Python code from Vim in IPython, including executing individual
code cells similar to Jupyter notebooks and MATLAB.
This plugin also supports [other languages and REPLs](#other-repls) such as
Julia.

ipython-cell is especially suited for data exploration and visualization using
Python. You can for example define a code cell that loads your input data, and
another code cell to visualize the data. This plugin allows you to change and
re-run the visualization part of your code without having to reload the data
each time.

The major difference between ipython-cell and other plugins (such as vim-slime
and nvim-ipy) is that this plugin has 'non-verbose' commands that do not show
the code that is run. This makes it easier to read the output in IPython.
Additionally, ipython-cell provides some convenience commands to jump between
cells and to work with IPython, see [Commands](#commands) below.


Demo
----

![Demo animation](../assets/ipython-cell-demo.gif?raw=true)


Requirements
------------

ipython-cell requires Vim or Neovim to be compiled with Python 2 or Python 3
support (`+python` or `+python3` when running `vim --version`). If both Python
versions are found, the plugin will prefer Python 3.

ipython-cell depends on [vim-slime] to send the code to IPython, see
[Installation](#installation) instructions below.

Additionally, the 'non-verbose' cell execution feature requires Tkinter to be
installed and either `+clipboard` support in Vim (see `vim --version`), or an
external [clipboard program](#supported-clipboard-programs) to be installed.
There is also a verbose version of the cell execution feature that does not
require Tkinter or clipboard support, see [Usage](#usage).

[vim-slime]: https://github.com/jpalardy/vim-slime


Installation
------------

It is easiest to install ipython-cell using a plugin manager (I personally
recommend [vim-plug]). See respective plugin manager's documentation for more
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

ipython-cell sends code from Vim to IPython using [vim-slime]. For this to
work, IPython has to be running in a terminal multiplexer like GNU Screen or
tmux, or in a Vim or Neovim terminal. I personally use tmux, but you will find
`screen` installed on most *nix systems.

It is recommended that you familiarize yourself with [vim-slime] first before
using ipython-cell. Once you understand vim-slime, using ipython-cell will be a
breeze.

ipython-cell does not define any key mappings by default, but comes with the
commands listed below, which I recommend that you bind to key combinations of
your likings. The [Example Vim Configuration](#example-vim-configuration) shows
some examples of how this can be done.

Note that the 'non-verbose' cell execution feature copies your code to the
system clipboard. You may want to avoid using this feature if your code
contains sensitive data.


### Commands

| Command                               | Description                                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------------------------- |
| `:IPythonCellExecuteCell`             | Execute the current code cell in IPython<sup>1,2</sup>                                      |
| `:IPythonCellExecuteCellJump`         | Execute the current code cell in IPython, and jump to the next cell<sup>1,2</sup>           |
| `:IPythonCellExecuteCellVerbose`      | Print and execute the current code cell in IPython<sup>3</sup>                              |
| `:IPythonCellExecuteCellVerboseJump`  | Print and execute the current code cell in IPython, and jump to the next cell<sup>3</sup>   |
| `:IPythonCellRun`                     | Run the whole script in IPython<sup>1</sup>                                                 |
| `:IPythonCellRunTime`                 | Run the whole script in IPython and time the execution                                      |
| `:IPythonCellClear`                   | Clear IPython screen                                                                        |
| `:IPythonCellClose`                   | Close all figure windows                                                                    |
| `:IPythonCellPrevCell`                | Jump to the previous cell header                                                            |
| `:IPythonCellNextCell`                | Jump to the next cell header                                                                |
| `:IPythonCellPrevCommand`             | Run previous command                                                                        |
| `:IPythonCellRestart`                 | Restart IPython                                                                             |
| `:IPythonCellInsertAbove`             | Insert a cell header tag above the current cell                                             |
| `:IPythonCellInsertBelow`             | Insert a cell header tag below the current cell                                             |
| `:IPythonCellToMarkdown`              | Convert current code cell into a markdown cell                                              |

<sup>1</sup> Can be [configured for other REPLs](#other-repls).  
<sup>2</sup> Non-verbose version (using `%paste`), requires Tkinter and `+clipboard` support or a [clipboard program](#supported-clipboard-programs).  
<sup>3</sup> Verbose version (using `%cpaste`), works without Tkinter and clipboard support.

[vim-slime]: https://github.com/jpalardy/vim-slime


### Custom commands

You may want to send other commands to IPython, such as `%debug` and `exit`.
vim-slime makes it easy to send arbitrary text to IPython from Vim using the
`SlimeSend1` command, for example

    :SlimeSend1 %debug

You can then bind these commands to key mappings, see
[Example Vim Configuration](#example-vim-configuration) below.


Defining code cells
-------------------

Code cells are defined by either special text in the code or Vim marks,
depending on if `g:ipython_cell_delimit_cells_by` is set to `'tags'` or
`'marks'`, respectively. The default is to use tags.

The examples below show how code cell boundaries work.


### Code cells defined using tags

Use `# %%`, `#%%`, `# <codecell>`, or `##` to define cell boundaries.

~~~
                                   _
import numpy as np                  | cell 1
                                   _|
# %% Setup                          | cell 2
                                    |
numbers = np.arange(10)             |
                                   _|
# %% Print numbers                  | cell 3
                                    |
for n in numbers:                   |
    print(n)                        |
                                   _|
    # %% Odd or even                | cell 4
                                    |
    if n % 2 == 0:                  |
        print("Even")               |
    else:                           |
        print("Odd")                |
                                   _|
# %% Print sum                      | cell 5
                                    |
total = numbers.sum()               |
print("Sum: {}".format(total))      |
print("Done.")                     _|

~~~

Note that code cells can be defined inside statements such as `for` loops.
IPython's `%paste` will automatically dedent the code before execution.
However, if the code cell is defined inside e.g. a `for` loop, the code cell
*will not* iterate over the loop.

In the example above, executing cell 4 after cell 3 will only print `Odd` once
because IPython will execute the following code:

~~~python
for n in numbers:
    print(n)

~~~

for cell 3, followed by

~~~python
if n % 2 == 0:
    print("Even")
else:
    print("Odd")

~~~

for cell 4. The `for` statement is no longer included for cell 4.

You must therefore be careful when defining code cells inside statements.


### Code cells defined using marks

Use Vim marks (see `:help mark`) to define cell boundaries.
Here marks are depicted as letters in the left-most column.

~~~
                                   _
  | import numpy as np              | cell 1
  |                                _| 
a | numbers = np.arange(10)         | cell 2
  |                                 |
  |                                _|
b | for n in numbers:               | cell 3
  |     print(n)                   _|
c |     if n % 2 == 0:              | cell 4
  |         print("Even")           |
  |     else:                       |
  |         print("Odd")            |
  |                                _|
d | total = numbers.sum()           | cell 5
  | print("Sum: {}".format(total)) _|

~~~

See note in the previous section about defining code cells inside statements
(such as cell 4 inside the `for` loop in the example above).


Configuration
-------------

| Option                                | Description                                                                                                                                                                         |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `g:ipython_cell_delimit_cells_by`     | Specify if cells should be delimited by `'tags'` or `'marks'`. Default: `'tags'`                                                                                                    |
| `g:ipython_cell_tag`                  | If cells are delimited by tags, specify the format of the tags. Can be a string or a list of strings to specify multiple formats. Default: `['# %%', '#%%', '# <codecell>', '##']`  |
| `g:ipython_cell_regex`                | If `1`, tags specified by `g:ipython_cell_tag` are interpreted as [Python regex patterns], otherwise they are interpreted as literal strings. Default: `0`                          |
| `g:ipython_cell_valid_marks`          | If cells are delimited by marks, specify which marks to use. Default: `'abcdefghijklmnopqrstuvqxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'`                                                      |
| `g:ipython_cell_cell_command`         | Command to run for executing cells. Default: `'%paste -q'`                                                                                                                          |
| `g:ipython_cell_run_command`          | Command to run for executing scripts. Default: `'%run {options} "{filepath}"`<sup>1</sup>                                                                                           |
| `g:ipython_cell_prefer_external_copy` | Set to `1` to prefer using an external program to copy to system clipboard rather than relying on Vim/Neovim yank. Default: `0`                                                     |
| `g:ipython_cell_highlight_cells`      | Set to `0` to disable highlighting of cell headers defined using tags. Default: `1`                                                                                                 |
| `g:ipython_cell_highlight_cells_ft`   | A list of filetypes for which cell headers will be highlighted if `g:ipython_cell_highlight_cells` is enabled. Default: `['python']`                                                |
| `g:ipython_cell_send_cell_headers`    | If cells are delimited by tags, separately send the cell header before the cell contents. Default: `0`                                                                              |
| `g:ipython_cell_insert_tag`           | The cell tag inserted by `IPythonCellInsertAbove` and `IPythonCellInsertBelow`. Default: `# %% `                                                                                    |
| `g:ipython_cell_send_ctrl_u`          | Send Ctrl-U to clear the line before sending commands to IPython. Set to `0` if this is not supported by your shell. Default: `1`                                                   |

<sup>1</sup> `{options}` will be replaced by the command options, such as `-t` for `IPythonRunTime`. `{filepath}` will be replaced by the path of the current buffer.

[Python regex patterns]: https://docs.python.org/3/library/re.html#regular-expression-syntax


Example Vim configuration
-------------------------

Here's an example of how to configure your `.vimrc` to use this plugin. Adapt
it to suit your needs.

~~~vim
" Load plugins using vim-plug
call plug#begin('~/.vim/plugged')
Plug 'jpalardy/vim-slime', { 'for': 'python' }
Plug 'hanschen/vim-ipython-cell', { 'for': 'python' }
call plug#end()

"------------------------------------------------------------------------------
" slime configuration 
"------------------------------------------------------------------------------
" always use tmux
let g:slime_target = 'tmux'

" fix paste issues in ipython
let g:slime_python_ipython = 1

" always send text to the top-right pane in the current tmux tab without asking
let g:slime_default_config = {
            \ 'socket_name': get(split($TMUX, ','), 0),
            \ 'target_pane': '{top-right}' }
let g:slime_dont_ask_default = 1

"------------------------------------------------------------------------------
" ipython-cell configuration
"------------------------------------------------------------------------------
" Keyboard mappings. <Leader> is \ (backslash) by default

" map <Leader>s to start IPython
nnoremap <Leader>s :SlimeSend1 ipython --matplotlib<CR>

" map <Leader>r to run script
nnoremap <Leader>r :IPythonCellRun<CR>

" map <Leader>R to run script and time the execution
nnoremap <Leader>R :IPythonCellRunTime<CR>

" map <Leader>c to execute the current cell
nnoremap <Leader>c :IPythonCellExecuteCell<CR>

" map <Leader>C to execute the current cell and jump to the next cell
nnoremap <Leader>C :IPythonCellExecuteCellJump<CR>

" map <Leader>l to clear IPython screen
nnoremap <Leader>l :IPythonCellClear<CR>

" map <Leader>x to close all Matplotlib figure windows
nnoremap <Leader>x :IPythonCellClose<CR>

" map [c and ]c to jump to the previous and next cell header
nnoremap [c :IPythonCellPrevCell<CR>
nnoremap ]c :IPythonCellNextCell<CR>

" map <Leader>h to send the current line or current selection to IPython
nmap <Leader>h <Plug>SlimeLineSend
xmap <Leader>h <Plug>SlimeRegionSend

" map <Leader>p to run the previous command
nnoremap <Leader>p :IPythonCellPrevCommand<CR>

" map <Leader>Q to restart ipython
nnoremap <Leader>Q :IPythonCellRestart<CR>

" map <Leader>d to start debug mode
nnoremap <Leader>d :SlimeSend1 %debug<CR>

" map <Leader>q to exit debug mode or IPython
nnoremap <Leader>q :SlimeSend1 exit<CR>

" map <F9> and <F10> to insert a cell header tag above/below and enter insert mode
nmap <F9> :IPythonCellInsertAbove<CR>a
nmap <F10> :IPythonCellInsertBelow<CR>a

" also make <F9> and <F10> work in insert mode
imap <F9> <C-o>:IPythonCellInsertAbove<CR>
imap <F10> <C-o>:IPythonCellInsertBelow<CR>

~~~

Note that the mappings as defined here work only in normal mode unless
otherwise noted (see `:help mapping` in Vim for more information).

Moreover, these mappings will be defined for all file types, not just Python
files. If you want to define these mappings for only Python files, you can put
the mappings in `~/.vim/after/ftplugin/python.vim` for Vim
(or `~/.config/nvim/after/ftplugin/python.vim` for Neovim).


### MATLAB-like key bindings

If you come from the MATLAB world, you may want e.g. F5 to save and run the
script regardless if you are in insert or normal mode, F6 to execute the
current cell, and F7 to execute the current cell and jump to the next cell:

~~~vim
" map <F5> to save and run script
nnoremap <F5> :w<CR>:IPythonCellRun<CR>
inoremap <F5> <C-o>:w<CR><C-o>:IPythonCellRun<CR>

" map <F6> to evaluate current cell without saving
nnoremap <F6> :IPythonCellExecuteCell<CR>
inoremap <F6> <C-o>:IPythonCellExecuteCell<CR>

" map <F7> to evaluate current cell and jump to next cell without saving
nnoremap <F7> :IPythonCellExecuteCellJump<CR>
inoremap <F7> <C-o>:IPythonCellExecuteCellJump<CR>

~~~


### Use the `percent` format

If you use the [percent format] for cells and don't want e.g. `# %% [markdown]`
to be interpreted as a cell header, you can use regex:

~~~vim
let g:ipython_cell_regex = 1
let g:ipython_cell_tag = '# %%( [^[].*)?'

~~~

[percent format]: https://jupytext.readthedocs.io/en/latest/formats.html#the-percent-format


### Other REPLs

ipython-cell can also be configured to support other languages and REPLs.
For example, to make `IPythonCellRun` and `IPythonCellExecuteCell` work with
Julia, add the following to your `.vimrc`:

~~~vim
let g:ipython_cell_run_command = 'include("{filepath}")'
let g:ipython_cell_cell_command = 'include_string(Main, clipboard())'

~~~


### Change highlight for code cell headers

To change the colors of cell headers, add something like the following to your
.vimrc:

    augroup ipython_cell_highlight
        autocmd!
        autocmd ColorScheme * highlight IPythonCell ctermbg=238 guifg=darkgrey guibg=#444d56
    augroup END


### More tips

For more configuration and usage tips, see [the wiki].

[the wiki]: https://github.com/hanschen/vim-ipython-cell/wiki


Supported clipboard programs
----------------------------

If your Vim installation does not have `+clipboard` support, some features of
ipython-cell will attempt to use one of the following clipboard programs:

* Linux: [xclip] (preferred) or [xsel].
* macOS: pbcopy (installed by default).
* Windows: not supported.

[xclip]: https://github.com/astrand/xclip
[xsel]: https://github.com/kfish/xsel


FAQ
---

> I have installed the plugin but get 'Not an editor command'. Why?

If the error persists after restarting Vim/Neovim, make sure that your editor
has support for Python by running the following commands in the editor:

    :echo has('python')
    :echo has('python3')

At least one of the commands should return `1`. If they both return `0`,
you need to set up your editor with Python support. In the case of Neovim, that
means installing the `pynvim` Python module, see [documentation].

[documentation]: https://neovim.io/doc/user/provider.html#provider-python

> The `IPythonCellExecuteCell` and `IPythonCellExecuteCellJump` commands do
> not work, but other commands such as IPythonCellRun work. Why?

First, make sure you have Tkinter installed (otherwise you will get an error
message) and a supported [clipboard program](#supported-clipboard-programs).
Also make sure your `DISPLAY` variable is correct, see next question.
If you cannot install the requirements but still want to use the cell execution
feature, you can try the verbose versions `IPythonCellExecuteCellVerbose` and
`IPythonCellExecuteCellVerboseJump`.

> `IPythonCellExecuteCell` and `IPythonCellExecuteCellJump` do not execute the
> correct code cell, or I get an error about
> 'can't open display',
> 'could not open display',
> 'could not connect to display',
> or something similar, what do I do?

Make sure your `DISPLAY` environment variable is correct, especially after
re-attaching a screen or tmux session. In tmux you can update the `DISPLAY`
variable with the following command:

    eval $(tmux showenv -s DISPLAY)

> Should I use tags or marks to define cells?

This depends on personal preference. Tags are similar to `%%` in MATLAB and
`# %%` in e.g. Jupyter Notebooks and Spyder. They become a part of your code
and can also be shared with others, making them ideal if you want more
persistent cells. Marks, on the other hand, are more transient and can be
changed without triggering changes in your code, which can be nice if you
change your cells often and your code is under version control.

> How do I show the marks in the left-most column?

Use the vim-signature plugin: https://github.com/kshenoy/vim-signature

> How to send only the current line or selected lines to IPython?

Use the features provided by vim-slime, see the
[Example Vim Configuration](#example-vim-configuration) for an example.
The default mapping `C-c C-c` (hold down Ctrl and tap the C key twice) will
send the current paragraph or the selected lines to IPython. See `:help slime`
for more information, in particular the documentation about
`<Plug>SlimeRegionSend` and `<Plug>SlimeLineSend`.

> Why do I get "name 'plt' is not defined" when I try to close figures?

ipython-cell assumes that you have imported `matplotlib.pyplot` as `plt` in
IPython. If you prefer to import `matplotlib.pyplot` differently, you can
achieve the same thing using vim-slime, for example by adding the following to
your .vimrc:

    nnoremap <Leader>x :SlimeSend1 matplotlib.pyplot.close('all')<CR>

> How can I send other commands to IPython, e.g. '%who'?

You can easily send arbitrary commands to IPython using the `:SlimeSend1`
command provided by vim-slime, e.g. `:SlimeSend1 %who`, and map these commands
to key combinations.

> Why does this plugin not work inside a virtual environment?

If you use Neovim, make sure you have the [neovim] Python package installed.

[neovim]: https://pypi.org/project/neovim/

> The `IPythonCellExecuteCell` command does not work, it seems to run the wrong
> cell.

Try to add the following to your configuration file:

    let g:ipython_cell_prefer_external_copy = 1

Make sure you have a [supported clipboard program](#supported-clipboard-programs)
installed.

> Why isn't this plugin specific to Python by default? In other words, why do
> I have to add all this extra stuff to make this plugin Python-specific?

This plugin was created with Python and IPython in mind, but I don't want to
restrict the plugin to Python by design. Instead, I have included examples of
how to use plugin managers to specify that the plugin should be loaded only
for Python files and how to create Python-specific mappings. If someone wants
to use this plugin for other filetypes, they can easily do so.

> Why is this plugin written in Python instead of pure Vimscript?

Because I feel more comfortable with Python and don't have the motivation to
learn Vimscript for this plugin. If someone implements a pure Vimscript
version, I would be happy to consider to merge it.

> I get an error (e.g. SyntaxError) because the plugin inserts `^U` before the
> command, what should I do?

Try to add the following to your configuration file:

    let g:ipython_cell_send_ctrl_u = 0


Related plugins
---------------

* [tslime\_ipython] - Similar to ipython-cell but with some small differences.
  For example, tslime\_ipython pastes the whole code that's sent to IPython
  to the input line, while ipython-cell uses IPython's `%paste -q` command to
  make the execution less verbose.
* [vim-ipython] - Advanced two-way integration between Vim and IPython. I never
  got it to work as I want, i.e., don't show the code that's executed but show
  the output from the code, which is why I created this simpler plugin.
* [nvim-ipy] - Similar to [vim-ipython], but refactored for Neovim and has some
  basic support for cells.
* [vim-tmux-navigator] - Seamless navigation between Vim splits and tmux panes.
* [vim-signature] - Display marks in the left-hand column.

[tslime\_ipython]: https://github.com/eldridgejm/tslime_ipython
[vim-ipython]: https://github.com/ivanov/vim-ipython
[nvim-ipy]: https://github.com/bfredl/nvim-ipy
[vim-tmux-navigator]: https://github.com/christoomey/vim-tmux-navigator
[vim-signature]: https://github.com/kshenoy/vim-signature


Thanks
------

ipython-cell was heavily inspired by [tslime\_ipython].
The code logic to determine which Python version to use was taken from
[YouCompleteMe].

[tslime\_ipython]: https://github.com/eldridgejm/tslime_ipython
[YouCompleteMe]: https://github.com/Valloric/YouCompleteMe
