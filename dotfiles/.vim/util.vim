" Utility commands and other settings

command! Config :e $MYVIMRC
command! TrimWhitespace execute ':%s/\s\+$//e' | let @/=''
command! JsonIndent execute ':%!python3 -m json.tool --indent 2'
command! JsonLinesIndent execute ':%!python3 -m json.tool --indent 2 --json-lines'
command! CopyFileName :let @+ = expand('%:t') | echo 'Copied: ' . @+
command! CopyFilePath :let @+ = expand('%:p') | echo 'Copied: ' . @+
command! Reformat :%!clang-format
command! Timestamp :execute "normal! a" . strftime('%Y-%m-%d %H:%M:%S')

" autocmd OptionSet diff setlocal syntax=off
if &diff
syntax off
set nocursorline
endif

" settings for fzf-vim plugin
let g:fzf_vim = {}
let g:fzf_vim.preview_window = []

command! -bang -nargs=* Rg call fzf#vim#grep("rg --hidden --no-ignore --glob '!.git/*' --column --line-number --no-heading --color=always --smart-case " .
      \ <q-args>, 1, { 'options': '--delimiter : --nth 4..' }, <bang>0)


function! RunCmdOnPara(cmd)
  " Save current unnamed register
  let save_reg = getreg('"')
  let save_regtype = getregtype('"')

  normal! dip

  " Get deleted text from unnamed register
  let lines = getreg('"', 1, 1)

  " Run shell command with deleted paragraph as input
  let result = systemlist(a:cmd, lines)

  " Insert result below current line
  call append(line('.') - 1, result)

  " Restore unnamed register
  call setreg('"', save_reg, save_regtype)
endfunction

" Function to find the range (start, end) between surrounding ```
function! FindSurroundingCodeBlock() abort
  let total_lines = line('$')
  let cur_line = line('.')
  let start = -1
  let end = -1

  " Search upwards for the previous ```
  for lnum in range(cur_line - 1, 1, -1)
    let line_content = getline(lnum)
    if line_content =~ '^```'
      let start = lnum + 1
      break
    endif
  endfor

  " Search downwards for the next ```
  for lnum in range(cur_line + 1, total_lines)
    let line_content = getline(lnum)
    if line_content =~ '^```'
      let end = lnum - 1
      break
    endif
  endfor

  if start > 0 && end > 0 && start <= end
    return [start, end]
  endif
  throw "Could not find a valid ``` query block below the table."
endfunction

" Find the first consecutive range of lines above the cursor that form a Markdown-style table
function! FindTableAbove() abort
  let cur_line = line('.') - 1
  let start = -1
  let end = -1

  " Skip any non-table lines at the very beginning
  while cur_line >= 1 && getline(cur_line) !~ '^|'
    let cur_line -= 1
  endwhile

  " If we didn't find a line starting with '|', throw
  if cur_line < 1
    throw 'No Markdown table found above.'
  endif

  " End of table is the first line starting with '|'
  let end = cur_line

  " Now keep going up as long as lines start with '|'
  while cur_line >= 1 && getline(cur_line) =~ '^|'
    let start = cur_line
    let cur_line -= 1
  endwhile

  return [start, end]
endfunction

function! RunTextQuery(...) abort

  let [start, end] = FindSurroundingCodeBlock()
  let query_lines = getline(start, end)
  let query = join(query_lines, " ")

  let [t_start, t_end] = FindTableAbove()
  let lines = getline(t_start, t_end)
  let normalized = systemlist('dfx --from md --to csv', lines)

  " Construct the shell command with the input
  let cmd = 'textquery ' . shellescape(query)

  " Run shell command with deleted paragraph as input
  let result = systemlist(cmd, normalized)
  call setreg('+', join(result, "\n"))

  redraw!
  " Show output line-by-line
  " for line in result
  for line in result
    echom line
  endfor

endfunction

function! RunTextQueryInline(...) abort

  " Find the surrounding code block for the query
  let [start, end] = FindSurroundingCodeBlock()
  let query_lines = getline(start, end)
  let query = join(query_lines, " ")

  " Find the table above
  let [t_start, t_end] = FindTableAbove()
  let lines = getline(t_start, t_end)
  let normalized = systemlist('dfx --from md --to csv', lines)

  " Construct the shell command with the query
  let cmd = 'textquery ' . shellescape(query)

  " Run shell command with table as input
  let result = systemlist(cmd, normalized)

  " Replace original table with result
  call setline(t_start, result)
  if len(result) < t_end - t_start + 1
    " Delete extra lines if the result is shorter than original
    call deletebufline('%', t_start + len(result), t_end)
  endif

endfunction

function! ExecBacktickToggle()
  let cols = input("Enter column numbers (comma-separated): ")
  if empty(cols)
    echo "No columns provided."
    return
  endif
  call RunCmdOnPara('dfx --from md --to md --tf-backtick=' . cols . '')
endfunction

function! RunCurrentBuf()
    let current_file = expand('%:p')
    if !filereadable(current_file)
        echohl ErrorMsg | echom "Error: The current buffer is not a readable file." | echohl None
        return
    endif
    let result_str = system(current_file)
    let result = split(result_str, '\n')
    call setreg('+', join(result, "\n"))
    redraw!
    for line in result
        echom line
    endfor
endfunction


command! Csv2Md call RunCmdOnPara('dfx --from csv --to md')
command! Md2Csv call RunCmdOnPara('dfx --from md --to csv')
command! MdTableFixup call RunCmdOnPara('dfx --from md --to md')
command! BacktickToggle call ExecBacktickToggle()
command! TextQuery call RunTextQuery()
command! TextQueryInline call RunTextQueryInline()
command! RunCurrentBuf call RunCurrentBuf()

nnoremap <leader><leader>x :RunCurrentBuf<CR>
