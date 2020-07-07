#!/usr/bin/env bash
set -o errexit

cyan="$(tput bold; tput setaf 5)"
reset="$(tput sgr0)"

 printf "\n*** Checking for build requirements and installing them, if missing...\n"

if [[ -d "$(xcode-select -p)" ]]; then
    echo "${cyan}Xcode tools found!${reset}"
else
    xcode-select --install
    echo "${cyan}If you received a popup asking to install Xcode tools, please accept.${reset}"
    read -rsn1 -p"===========  Press any key when installation is complete  ===========";echo
fi

if command -v brew > /dev/null 2>&1; then
    echo "${cyan}Homebrew found!${reset}"
else
    echo "${cyan}This script may have to be restarted after Homebrew is installed${reset}"
    echo | /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
fi

if command -v python3.7 > /dev/null 2>&1; then
	  echo "${cyan}Python 3.7 found!${reset}"
else
    # currently this will install Python version 3.7.x
    echo "${cyan}Installing Python 3 via Homebrew...${reset}"
    brew install python
fi

# check for presence of commands and install, if needed
command -v platypus >/dev/null 2>&1  || brew install platypus
command -v create-dmg >/dev/null 2>&1 || brew install create-dmg
command -v pipenv >/dev/null 2>&1 || pip3 install pipenv==2020.5.28

# set language environment to prevent pip locale errors
echo -e 'export LC_ALL=en_US.UTF-8\nexport LANG=en_US.UTF-8' >> ~/.bash_profile

echo "${cyan}Looks good! Open a new shell and run 'pipenv shell' first, as the build script"
echo "should be run in a virtual environment. Then run build_app.sh ${reset}"
