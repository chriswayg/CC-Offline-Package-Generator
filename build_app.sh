#!/usr/bin/env bash
set -o errexit

color="$(tput bold; tput setaf 5)"
reset="$(tput sgr0)"

printf "${color}*** Checking for build prerequisites${reset}\n"

[[ -d "$(xcode-select -p)" ]]  || { echo "${color}Xcode tools are missing! Run build_prerequisites.sh first.${reset}\n" && exit 1; }

checkPrereqs=("python3.7" \
              "brew" \
              "platypus" \
              "create-dmg" \
              "pipenv")

for prereq in ${checkPrereqs[@]}; do
    command -v $prereq > /dev/null 2>&1  || { printf "${color}$prereq is missing! Run build_prerequisites.sh first.${reset}\n" && exit 1; }
done

[[ -z $VIRTUAL_ENV ]] && printf "${color}Run 'pipenv shell' first, as this build script needs to run in a virtual environment.${reset}\n" && exit 1

if [[ -d /Volumes/CC_Offline_Package_Generator/CC_Offline_Package_Generator.app ]]; then
    hdiutil detach /Volumes/CC_Offline_Package_Generator  || { printf  "${color}*** Ensure that Adobe_Offline_Package_Generator.dmg is unmounted!${reset}\n" && exit 1; }
fi

printf  "${color}*** cleaning up before build...${reset}\n"
rm -rf build/ dist/
[[ -f app/ppackage ]] && rm app/ppackage

printf  "${color}*** creating the binary python 'ppackage' with pyinstaller...${reset}\n"
pipenv install
pyinstaller ccdl.spec

printf  "${color}***creating the .app bundle with Platypus...${reset}\n"
mkdir -p dmg/createdmg
mv dist/ppackage app/
cd app
rm -rf "../dmg/createdmg/CC_Offline_Package_Generator.app"
platypus -P app_bundle_config.platypus "../dmg/createdmg/CC_Offline_Package_Generator.app"

printf  "${color}*** creating the DMG installer with create-dmg...${reset}\n"
cd ../dmg
[[ -f "CC_Offline_Package_Generator.dmg" ]] && rm "CC_Offline_Package_Generator.dmg"
[[ -f "rw.CC_Offline_Package_Generator.dmg" ]] && rm "rw.CC_Offline_Package_Generator.dmg"

# Create a DMG installer
create-dmg \
  --volname "CC_Offline_Package_Generator" \
  --background "installer_background.png" \
  --window-pos 200 120 \
  --window-size 500 360 \
  --icon-size 80 \
  --icon "CC_Offline_Package_Generator.app" 120 155 \
  --hide-extension "CC_Offline_Package_Generator.app" \
  --app-drop-link 350 155 \
  "CC_Offline_Package_Generator.dmg" \
  "createdmg"
printf  "${color}*** The installer has been created in dmg/CC_Offline_Package_Generator.dmg${reset}\n"
