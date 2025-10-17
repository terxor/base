# Setup

Linux general environment setup, primarily:

- Terminal (alacritty)
- tmux
- vim/neovim
- sway (a wayland WM)

> Note: Tested only on Ubuntu

## Get started

Download script, inspect and execute:

```
curl -o /tmp/setup.sh https://raw.githubusercontent.com/terxor/setup/main/setup.sh
# Inspect setup.sh
bash -c /tmp/setup.sh
```

Or, directly execute:

```
BRANCH=main curl -fsSL https://raw.githubusercontent.com/terxor/setup/$BRANCH/setup.sh | bash -s -- --remote --branch $BRANCH
```

```
bash -c "$(wget -qO- https://raw.githubusercontent.com/terxor/setup/main/setup.sh)"
```

## Conventions

- Configurations go into `$HOME/.config`
- Binaries or scripts go into `$HOME/.local/bin`

## Miscellaneous stuff

### Tex

For tex, look at install instructions on [tex live official website](https://tug.org/texlive/quickinstall.html#running)
  
Or simply run this script:

```
#!/bin/bash
set -e 

cd ~/workspace/scratch
curl -L -o install-tl-unx.tar.gz https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
zcat < install-tl-unx.tar.gz | tar xf -

cd "$(ls -d install-tl-* | head -n 1)"

perl ./install-tl --no-interaction --scheme=small --no-doc-install --no-src-install --texdir=$HOME/.local/bin/texlive

# Now, add the following line to your shell init
PATH=$PATH:$HOME/.local/bin/texlive/bin/x86_64-linux

# Install additional packages
tlmgr install titlesec
tlmgr install enumitem
```

### C++ code formatting

`apt install clang-format`

Normally this tool will work using stdin/stdout

To reformat a file in-place: `clang-format -i src.cc`

### Alacritty/WSL setup

```
curl -o "%USERPROFILE%\AppData\Roaming\alacritty\alacritty.toml" https://raw.githubusercontent.com/terxor/setup/refs/heads/staging/config/.alacritty.toml
```

### Touchpad issues

In  `/etc/X11/xorg.conf.d/touchpad-tap.conf` add the following

tapping and natural scroll

> Note: requires sudo

```
Section "InputClass"
        Identifier "libinput touchpad catchall"
        MatchIsTouchpad "on"
        MatchDevicePath "/dev/input/event*"
        Driver "libinput"
        Option "Tapping" "on"
        Option "Natural Scrolling" "on"
EndSection
```

The method below does it temporarily

```
# Note: 9 below is the id obtained by first command
xinput list
xinput list-props 9
xinput set-prop 9 "libinput Natural Scrolling Enabled" 1
```


### NPM and language servers

```
sudo apt install nodejs npm
sudo npm i -g pyright
```

```
sudo apt-get install clangd-19
sudo update-alternatives --install /usr/bin/clangd clangd /usr/bin/clangd-19 100
```

### Iosevka font

https://github.com/be5invis/Iosevka/releases/download/v33.2.0/PkgTTF-IosevkaTerm-33.2.0.zip

```
curl -fsSL -o /tmp/iosevka.zip https://github.com/be5invis/Iosevka/releases/download/v33.2.0/PkgTTF-IosevkaTerm-33.2.0.zip
mkdir -p /tmp/iosevka ~/.local/share/fonts
unzip -d /tmp/iosevka /tmp/iosevka.zip
mv /tmp/iosevka/*.ttf ~/.local/share/fonts
fc-cache -f -v
```

***

TODO: Nvim reproduce error:

it will get stuck right after `no`

```
:.,$norm
```

***

Set mouse speed and flat accel

```
xinput set-prop "Logitech Gaming Mouse G402" "Coordinate Transformation Matrix"  0.5 0 0 0 0.5 0 0 0 1
xinput set-prop "Logitech Gaming Mouse G402" "libinput Accel Profile Enabled"  0 1 0
```

Update: It is better to just copy `./other/mouse.conf` to
`/etc/X11/xorg.conf.d/` for persistent changes (requires sudo)


***

Auto switching of displays:

```
# autoswitch, add to i3
autorandr --change

# save profile
autorandr --save myprofile1
```

***

Brightness controls

```
sudo apt install brightnessctl
sudo chmod +s $(which brightnessctl)
```

***

Audio auto-mute on headphone plugged in

```
amixer scontrols
amixer -c 0 sget "Auto-Mute Mode"
amixer -c 0 sset "Auto-Mute Mode" Enabled
```

***

Hide `EN` in i3 status bar:

Open `ibus-setup` and uncheck box related to 'show in tray'.

***

Creating custom mappings through `keymapper`

Enable service on start:

```
systemctl enable keymapperd
```


## Browser mappings (intended)

| Action           | Key          | Default? |
| --------         | -----        | ---      |
| Next tab         | ctrl+n       | NO       |
| Prev tab         | ctrl+p       | NO       |
| Move to Next tab | ctrl+shift+n | NO       |
| Move to Prev tab | ctrl+shift+p | NO       |
| Delete word      | ctrl+w       | NO       |
| Close tab        | ctrl+q       | NO       |
| Bookmark         | ctrl+b       | NO       |
| Duplicate        | ctrl+d       | NO       |
| Back             | ctrl+[       | YES      |
| Fwd              | ctrl+]       | YES      |
| Edit address     | ctrl+l       | YES      |
| New tab          | ctrl+t       | YES      |

### Firefox config

In `about:config`:

```
ui.prefersReducedMotion -> set to number 1
ui.key.menuAccessKeyFocuses -> false
browser.urlbar.suggest.weather -> false
```

Optionally:

- Zoom: `Settings -> Zoom -> Default zoom 120%`

## Misc stuff

Media tools

```
sudo apt install vlc
sudo apt install ffmpeg
```

Screenshot tooling

```
sudo apt install maim
```

***

### TODO

- VIM: Fix multiple spaces in `gq` formatting

- Try tmux plugins (especially tmux-open)

## Wayland based setups

Packages:

```
sway
wl-clipboard
waybar
wofi
lm-sensors
swaylock

# Image related tools
grim
slurp
imv # Use imv-wayland
```

Enable auto-mute speakers on plugging in headphones 

- `alsamixer`
- If not visible by `F5`, then select sound card using `F6`
- Use arrow keys to go the the auto-mute vertical section.
- Enable it.
- `sudo alsactl store`

Screensharing

```
sudo apt install pipewire xdg-desktop-portal
systemctl --user restart xdg-desktop-portal
```

***

## Compile VIM on wayland


Prerequisite for wayland clipboard

```
sudo apt install libwayland-dev libxkbcommon-dev libgtk-3-dev
```

Steps

```
git clone https://github.com/vim/vim.git
cd vim/src
./configure --with-wayland
make
sudo make install
```

## Bluetooth connection (example: headphone)

```
sudo apt install pipewire pipewire-audio pipewire-pulse wireplumber
sudo apt install blueman

# Run blueman-manager to connect
```

