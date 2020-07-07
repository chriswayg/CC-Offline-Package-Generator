#!/usr/bin/env bash

CYAN="$(tput bold; tput setaf 6)"
RESET="$(tput sgr0)"

curl https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/src/ccdl.command -o "/Applications/CC Offline Package Generator.command"
chmod +x "/Applications/CC Offline Package Generator.command"

clear

echo "${CYAN}Done! You can now start /Applications/CC Offline Package Generator.command to begin${RESET}"
exit
