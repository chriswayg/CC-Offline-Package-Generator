#!/bin/bash

CYAN="$(tput bold; tput setaf 6)"
RESET="$(tput sgr0)"

curl https://gist.githubusercontent.com/jorisguex/c62b7fcbedd7b3ace800c04c962c66fa/raw/ccdl.command -o "/Applications/Adobe Packager.command"
chmod +x "/Applications/Adobe Packager.command"

clear

echo "${CYAN}Done! You can now start /Applications/Adobe Packager.command to begin${RESET}"
exit