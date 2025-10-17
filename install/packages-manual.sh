#!/bin/bash
set -euo pipefail
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source $INSTALL_DIR/env
# ------------------------------------------------------------------------------

# Constants
LOCAL_INSTALL_DIR="$HOME/.local/bin"
TMP_DIR="/tmp/setup/$(date +"%Y%m%d%H%M%S")"
FONTS_DIR="$HOME/.local/share/fonts"
ZSH_CUSTOM="$HOME/.oh-my-zsh/custom"

# For packages with arch names
ARCH="x86_64"

NVIM_VERSION='v0.11.0'
FZF_VERSION='v0.62.0'
OMZ_COMMIT_HASH="f8022980a3423f25e3d5e1b6a60d2372a2ba006b"
FZF_TAB_VERSION='v1.2.0'

# Ensure dirs
mkdir -p "$LOCAL_INSTALL_DIR" "$TMP_DIR" "$FONTS_DIR"

install_fzf() {
  if command -v fzf >/dev/null; then
    return
  fi

  local fzf_dir="$TMP_DIR/fzf"
  git clone --depth 1 --branch $FZF_VERSION https://github.com/junegunn/fzf.git "$fzf_dir"
  "$fzf_dir/install" --bin

  mv "$fzf_dir/bin/fzf" "$LOCAL_INSTALL_DIR/"
  mv "$fzf_dir/shell/"*.zsh "$LOCAL_INSTALL_DIR/"
}

install_nvim() {
  if command -v nvim >/dev/null; then
    return
  fi

  local nvim_pkg="https://github.com/neovim/neovim/releases/download/${NVIM_VERSION}/nvim-linux-${ARCH}.tar.gz"
  curl -fsSL -o "$TMP_DIR/nvim.tar.gz" "$nvim_pkg"
  tar -xzf "$TMP_DIR/nvim.tar.gz" -C "$HOME/.local/" --strip-components=1
}

install_omz() {
  if [ -d "$HOME/.oh-my-zsh" ]; then
    return
  fi
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/$OMZ_COMMIT_HASH/tools/install.sh)" "" --unattended
  rm -f "$HOME/.zshrc"
}

install_fzf_tab() {
  local plugin_dir="$ZSH_CUSTOM/plugins/fzf-tab"
  if [ -d "$plugin_dir" ]; then
    return
  fi
  git clone --branch $FZF_TAB_VERSION https://github.com/Aloxaf/fzf-tab "$plugin_dir"
}

install_font_iosevka() {
  if fc-list -q "Iosevka"; then
    return
  fi

  local font_url="https://github.com/be5invis/Iosevka/releases/download/v33.2.5/PkgTTF-Iosevka-33.2.5.zip"
  local font_dir="$TMP_DIR/iosevka"

  curl -fsSL -o "$TMP_DIR/iosevka.zip" "$font_url"
  unzip -d "$font_dir" "$TMP_DIR/iosevka.zip"

  mv "$font_dir"/*.ttf "$FONTS_DIR/"
  fc-cache -f >/dev/null
}

install_font_jbmono() {
  if fc-list -q "JetBrainsMono"; then
    return
  fi

  local font_url="https://download.jetbrains.com/fonts/JetBrainsMono-2.304.zip"
  local font_dir="$TMP_DIR/jbmono"

  curl -fsSL -o "$TMP_DIR/jbmono.zip" "$font_url"
  unzip -d "$font_dir" "$TMP_DIR/jbmono.zip"

  mv $font_dir/fonts/ttf/*.ttf "$FONTS_DIR/"
  fc-cache -f >/dev/null
}

# Run tasks
install_fzf
install_nvim
install_omz
install_fzf_tab
install_font_iosevka
install_font_jbmono

rm -rf $TMP_DIR
