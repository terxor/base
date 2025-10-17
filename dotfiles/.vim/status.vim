function! ShortenPath(path)
  let maxplen = 75
  if strlen(a:path) > maxplen
    let parts = split(a:path, '/')
    let l:sp = a:path
    if len(parts) > 2
      let sparts = []
      for i in range(len(parts) - 1)
        call add(sparts, strpart(parts[i], 0, 2))
      endfor
      let l:sp = '/' . join(sparts, '/') . '/' . parts[-1]
    endif
    if len(l:sp) > maxplen
      let pref = "..."
      return pref . strpart(l:sp, len(l:sp) - maxplen + len(pref))
    else
      return l:sp
    endif
  else
    return a:path
  endif
endfunction

if has("statusline") && !&cp
  set laststatus=2                                " always show the status bar
  set statusline=\ L%l:%L\ C%c:%{col('$')-1}                " line and column
  set statusline+=\ %{&modified?'MODIFIED':''}    " show modified indicator
  set statusline+=%=                              " left-right separation point
  set statusline+=\ %{ShortenPath(expand('%:p'))} " full file path
  set statusline+=\ %r                            " readonly indicator
endif
