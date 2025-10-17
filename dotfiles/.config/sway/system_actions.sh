#!/bin/bash

choices="lock\nsuspend\nlogout\nreboot\nshutdown"
action=$(echo -e "$choices" | wofi --dmenu --prompt "action")

case "$action" in
  lock)
    swaylock \
      -i $HOME/workspace/base/other/bg.png \
      --indicator-radius 110 \
      --font-size 20;;
  suspend)
    systemctl suspend ;;
  reboot)
    systemctl reboot ;;
  shutdown)
    systemctl poweroff ;;
  logout)
    swaymsg exit ;;
  *)
    exit 1 ;;
esac

