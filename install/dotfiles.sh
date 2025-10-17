#!/bin/bash
set -euo pipefail
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $INSTALL_DIR/env
# ------------------------------------------------------------------------------

if [ ! -d $BASE ]; then
    mkdir -p $BASE
    git clone $UPSTREAM_URL/$BASE_REPO $BASE
fi


# Create dirs which will get populated with other stuff
# so that stow doesn't link the dir
mkdir -p $HOME/.config/zsh
mkdir -p $HOME/.config/nvim
mkdir -p $HOME/.local/bin

$BASE/utils/install.sh
stow -v -d $BASE -t $HOME --adopt --no-folding dotfiles

