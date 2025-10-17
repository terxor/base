#!/usr/bin/env python3
import os
import stat
import sys
import subprocess
import re
import argparse
import string
from pathlib import Path
from bench.data import DataTable, MdFormat, TermColor

# Check environment variable
tb = os.environ.get("tb")
if not tb:
    print(TermColor.colorize(f'Env var "tb" is not set', 'red'))
    sys.exit(1)

tb_path = Path(tb)
tb_path.mkdir(parents=True, exist_ok=True)

STANDARD_FILES = list(string.ascii_lowercase + string.digits)

def get_file_size(fpath):
    path = Path(fpath)
    if not path.is_file():
        return 0
    return path.stat().st_size

def get_stats(fname, preview_len=50):
    """
    Returns (num_chars, preview) for the given file.
    - num_chars is file size in bytes.
    - preview is a collapsed snippet of up to preview_len chars.
    """
    fpath = os.path.join(tb_path, fname)
    size = get_file_size(fpath)
    if size == 0:
        return (0, "")

    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            chunk = f.read(preview_len * 2)  # small buffer
        collapsed = re.sub(r"\s+", " ", chunk).strip()

        if len(collapsed) > preview_len:
            preview = collapsed[:preview_len-2] + ".."
        else:
            preview = collapsed

        return (size, preview)

    except Exception:
        return (0, "")

def tb_stats():
    table = DataTable(['Buffer', 'Bytes', 'Preview'])
    ctable = []
    for fname in STANDARD_FILES:
        size, preview = get_stats(fname)
        if size == 0:
            continue
        table.append([fname, size, preview])
        ctable.append(['cyan', 'yellow', 'white'])
    print(MdFormat.render(table, color_table=ctable))

def tb_regen():
    regenerated = [f for f in STANDARD_FILES if not (tb_path / f).exists()]
    for f in regenerated:
        (tb_path / f).touch()
    
    for d in string.digits:
        p = tb_path / d
        st = os.stat(p)
        os.chmod(p, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    msg = "Regenerated files: " + ' '.join(regenerated) if regenerated else "All standard buffer files already exist."
    print(msg)

def tb_non_empty():
    used = [fname for fname in STANDARD_FILES if get_file_size(os.path.join(tb_path, fname)) > 0]
    if used:
        open_editor(used)
    else:
        print("No non-empty buffers to open.")
        sys.exit(1)

def tb_free(lim = len(string.ascii_lowercase)):
    res = []
    for fname in string.ascii_lowercase:
        p = os.path.join(tb_path, fname)
        if len(res) == lim:
            break
        if get_file_size(p) == 0:
            res.append(fname)
    return res

def open_editor(files, cd_to_base=True):
    """
    Open the given list of file paths in the user's preferred editor.

    Args:
        files (list of str or Path): List of file paths to open.
        cd_to_base (bool): If True, issue a '+cd {tb_path}' command to the editor.
    """
    if not files:
        print("No files to open.")
        sys.exit(1)

    editor = os.environ.get("EDITOR")
    cmd = [editor]
    if cd_to_base:
        cmd.append(f"+cd {str(tb_path)}")
    cmd += [os.path.join(tb_path, f) for f in files]
    os.execvp(editor, cmd)

def main():
    parser = argparse.ArgumentParser(
        description="Buffer manager utility.",
        usage="tb [-l|--list] [-i|--init] [-e|--empty] [-u|--used] [a-z0-9]"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--list", action="store_true", help="Show buffer list with stats")
    group.add_argument("-i", "--init", action="store_true", help="Initialize missing buffers")
    group.add_argument("-f", "--free", action="store_true", help="Return list of free buffers")
    group.add_argument("-u", "--used", action="store_true", help="Open all used buffers")
    group.add_argument("file", nargs="?", help="Open or create buffer file a-z or 0-9")

    args = parser.parse_args()

    if args.list:
        tb_stats()
    elif args.init:
        tb_regen()
    elif args.used:
        tb_non_empty()
    elif args.free:
        print(*tb_free())
    elif args.file is None:
        e = tb_free(1)
        if len(e) > 0:
            open_editor([e[0]])
        else:
            sys.exit(1)
    elif args.file in STANDARD_FILES:
        open_editor(args.file)
    else:
        print(f"Unknown option or file: {args.file}")
        parser.print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
