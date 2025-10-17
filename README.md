# base

## Environment setup

A simple way is to copy this script and run it.

```sh
#!/bin/bash
set -euo pipefail
BRANCH=main
URL=https://github.com/terxor/base/archive/refs/heads/$BRANCH.zip
curl -fsSL $URL -o /tmp/base.zip
BASE_TMP=/tmp/base
rm -rf $BASE_TMP
unzip /tmp/base.zip -d $BASE_TMP
$BASE_TMP/base-$BRANCH/setup.sh
```

Other ways are simply downloading or cloning this repo manually.
Note that the convention that this repo is placed in `~/workspace/base`.

### Individual installations

| name                         | purpose                                                 |
| ---------------------------- | ------------------------------------------------------- |
| `install/packages.sh`        | Basic packages such as git,vim,tree,etc.                |
| `install/packages-extn.sh`   | Window managers and other utilities                     |
| `install/packages-manual.sh` | Fonts, packages requiring special installation          |
| `install/dotfiles.sh`        | Create symlinks in home to binaries/config in this repo |

## Utils

Utils are set up as part of dotfiles setup.

--------------------------------------------------------------------------------
