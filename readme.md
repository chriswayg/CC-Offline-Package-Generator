# Adobe CC 2018 to 2022 Direct Download

**UPDATE, March 11, 2022: I have released a new version of the *CC Offline Package Generator* app which packages the updated script [adobe-packager](https://github.com/Drovosek01/adobe-packager) (version 0.1.4) by Drovosek. This app will allow you to download most available versions of Adobe CC Applications on all recent versions of macOS.** The advantage of *CC Offline Package Generator* is that it already has all dependencies in a small 8 MB app, whereas the *adobe-packager* script by itself may need to download and install about 500 MB of dependencies in order to work.

**Download: [CC Offline Package Generator](https://github.com/chriswayg/CC-Offline-Package-Generator/releases/latest)**

## Background

Adobe used to make Adobe CC trial full offline installer packages available via direct downloads as seen in the links for Adobe CC 2018 and 2019:

- [Adobe CC 2018 Direct Download Links](https://prodesigntools.com/adobe-cc-2018-direct-download-links.html) and [Adobe CC 2019 Direct Download Links](https://prodesigntools.com/adobe-cc-2019-direct-download-links.html)
- [How to Get New Adobe Creative Cloud 2022 Direct Download Links | ProDesignTools](https://prodesigntools.com/creative-cloud-2022-direct-download-links.html)
- [Why Direct Download Links Are Needed | ProDesignTools](https://prodesigntools.com/adobe-cc-no-more-direct-download-links.html#the-need)

There is no equivalent list of Adobe CC 2020 to 2022 direct download links available at this time, but the *CC_Offline_Package_Generator* can download the files directly from Adobe and create an installer package. *(This GitHub repository is not associated with or endorsed by Adobe or ProDesign Tools. Links to ProDesign and Adobe are provided to give additional background information on the issue of Direct Downloads of the Adobe CC offline installers and to give easy access to the various ways of downloading Adobe software.)*

## Description

This is a script that allows you to download portable installers of programs from Adobe for macOS with different versions and different or all languages. This can help system administrators who need to install the same program from Adobe on several computers, as well as those people who do not want to use the latest version of programs from Creative Cloud or install the application on an officially unsupported version of macOS (see *Instructions by Drovosek0*1 section below).

## Usage

1. First download and install from Adobe the [Creative Cloud - Full Installer (250+ MB)](https://helpx.adobe.com/download-install/kb/creative-cloud-desktop-app-download.html) *(scroll down to macOS | Alternative downloads)* or if you prefer, use the [Creative Cloud - Installer Downloader (3+ MB)](https://creativecloud.adobe.com/apps/download/creative-cloud). The CC Offline Package Generator will not run unless the Adobe Creative Cloud app has been installed first. You need an Adobe account when installing this app.

2. Then download the [CC_Offline_Package_Generator.dmg](https://github.com/chriswayg/CC-Offline-Package-Generator/releases/), mount it and copy `CC_Offline_Package_Generator` to Applications. Run the app and it will open a Terminal window. Then follow the on-screen instructions. Tested from High Sierra up to Monterey.

Download location: https://github.com/chriswayg/CC-Offline-Package-Generator/releases/

![](screenshots/Usage00.png)

Allow access to launch the Terminal window
![](screenshots/Usage00b.png)

The CC_Offline_Package_Generator script will download a list of all products from Adobe and prompt you to choose the product, version, language, and destination folder for the installer.

![](screenshots/Usage01.png)
![](screenshots/Usage02.png)

After that you just have to sit back and wait for it to finish. The script will download all required files, and then generate a convenient installer and place it in the destination directory. When prompted, select a destination folder where you want to save the installer.

![](screenshots/Usage03.png)

Now you can run the "Install [product]" app created in the destination folder, or save it for later offline installation.

![](screenshots/Usage04.png)

Make sure you install the [Adobe Creative Cloud App](https://creativecloud.adobe.com/apps/download/creative-cloud) first on the computers where you intend to run the installer. Most installers should work, but some will not. See *Known Issues* below for details.

![](screenshots/Usage05.png)
![](screenshots/Usage06.png)
![](screenshots/Usage07.png)

## Known issues

Currently most installers work, some might not work, and some are known not to work.

- *Acrobat* does not show up in the list, as is not made available from the Adobe servers in the same way.
- Look for reports about installers that do not work in [Issues · CC-Offline-Package-Generator · GitHub](https://github.com/chriswayg/CC-Offline-Package-Generator/issues) and in [Issues · adobe-packager · GitHub](https://github.com/Drovosek01/adobe-packager/issues).

## Technical notes

The *CC_Offline_Package_Generator* binary file was built with via `pyinstaller pyinstall.spec`on macOS High Sierra 10.13.6. This means it should be compatible with High Sierra, Mojave, Catalina, Big Sur, Monterey and beyond. The python virtual environment was created with `pipenv`. The original *adobe-packager* script is in the `src/` directory. The binary already includes Python inside, so there is no need to install Python to run CC_Offline_Package_Generator. 

## Build instructions

To build the app, *Homebrew* and *Python 3* need to be installed. This has been tested with Python 3.9 from Homebrew. The `build_prerequisites.sh` script will setup everything that is required. Some familiarity with configuring Python would be helpful. Check for potentially conflicting python installations with the Terminal command:

```shell
/bin/bash -c "$(curl -fsSL https://gist.githubusercontent.com/chriswayg/ee97606a4dc93a4cdacff90915d5d1e5/raw/pythonlister.sh)"
```

Then issue the following commands:

```shell
cd ~
git clone https://github.com/chriswayg/CC-Offline-Package-Generator.git
cd ~/CC-Offline-Package-Generator
sudo true && ./build_prerequisites.sh
```

Once the build prerequisites were susccessfully installed, open a new Terminal tab and continue with:

```shell
cd ~/CC-Offline-Package-Generator
pipenv install
pipenv shell
pip list
./build_app.sh
```

With `pip list` you can check, that your build environment has been correctly initialized with `pyinstaller`, `requests` and `tqdm`.  The build script will create the `CC_Offline_Package_Generator.dmg` installer in the `dmg/` directory.

---

### Alternative: run the python script

- Run a shell script which installs Homebrew and Python first (500 MB), then runs the python script.
1. Open the Apple Terminal.app
2. Copy & paste this command and hit enter:

```
/bin/bash -c "$(curl -fsSL src/install.sh)"
```

* Then run the `CC Offline Package Generator.command` in your /Applications folder and follow the on-screen instructions as explained above.

The script should be able to automatically configure itself by installing the required prerequisites in most setups: It will install Homebrew, if not already installed, then install Python 3 via Homebrew, and then add the python `requests` and the `tqdm` package to your python3 install via `pip`. These are the prerequisites for actually running the `ccdl.py` python script which does the actual download.

If you already have *Python 3*, the `requests` and the `tqdm` packages installed, you could also run  `ccdl.py` directly:

```
python3 ccdl.py
```

---

### How this works

The developer of the script, [ayyybe](https://gist.github.com/ayyybe), explains it:

>  I used a proxy to look at how the Creative Cloud app downloads apps, and was able to emulate it. I wish it were as simple as just downloading a dmg/pkg/app but Adobe has their own proprietary installer format. All the downloads are zip files with some files, and a .pimx file, which contains instructions for the installer system (usually something like "copy these files, set these permissions on these files, register these files with the CC app"). I was originally gonna implement my own parser/installer for .pimx files and handle everything myself, but I found that you can use Adobe's own installer included in the CC app by creating and providing it with a "driver.xml" file that contains the location of all the downloads, the install location, and install language, among other things. **The installers made by this script aren't the actual offline installers that Adobe provides to its enterprise customers. They're generated by the script and contain all the downloads for the product and its dependencies, and the aforementioned driver.xml.** When you run it and click the install button, it simply runs the HyperDrive installer included with the Adobe Creative Cloud App, and points it to the driver.xml inside the Install.app

## Instructions by Drovosek

#### How to install an application with all languages or choose a specific application language if all language packs are downloaded

Firstly, you should take into account that Adobe applications are quite specific and although they are made in approximately the same style, they often differ greatly in the implementation of the interface. For example, whichever language you choose when downloading Lightroom Classic or Media Encoder (tested on versions 10.4 and CC 2021, respectively), after installation they will have the same interface language as the system language and in the application settings you can change the interface language and it will change after restarting the application. Alas, this does not work with Photoshop, Illustrator (it was tested on CC 2021) and many other Adobe applications, and in order to change their interface language, you will have to reinstall the application after downloading it with the necessary language using our Adobe Packager or change the system interface language in the system settings and in the Creative Cloud settings in the "Apps" item to change the language to the same, restart the computer and only then install the application from Creative Cloud with the desired language.

Our Adobe Packager from a certain commit allows you to download the installer of your chosen application with all the languages available for the selected application (for this, at the language selection stage, you need to enter the word "ALL"), but this does not guarantee that in the installed application it will be possible to change the interface language to any available one. It all depends on the specific application.

For example, as already mentioned here, Lightroom Classic and Media Encoder, regardless of the language selected when downloading, will be installed with all languages and they can be easily switched in the application settings. Adobe XD application (tested on version 44.0.12) if you download (by selecting "ALL") and install with all languages, then after installation, you can select any interface language in the application settings and it will be applied after restarting the application. If you select one language during the Adobe XD download, then after installing the application, only this selected language will be present in its settings. With Illustrator (tested on CC 2021 v25.4.1) the situation is slightly different. If you download (by selecting "ALL") and install Illustrator with all languages, then after installation it will have the interface language "en_US" and all interface languages will be available for selection in the application settings, but after selecting the desired language and restarting the application, the interface language will not change.

I repeat, the interface language settings are specific to each Adobe program and therefore it is more convenient to have 1 installer with all languages and, if necessary, choose which interface language to install the application with.

If you downloaded the application with all the language packs (by selecting "ALL"), then you can set which interface language to install this application by changing in the file `driver.xml` the text between the "InstallLanguage" tags to one of the available language interface codes available for this application. You can view them in the `application.json` file (I recommend using some JSON beautifier to make it easier to read this JSON file). If you leave the word "ALL" between these tags, then the application will be installed either with the language "en_US" and in its settings it will not be possible to change the interface language, or it will be installed with the interface language of your system and in its settings it will be possible to change the interface language.

File `driver.xml` located on the path `<create_package>.app/Contents/Resouces/products`

The `application.json` file is located at `<create_package>.app/Contents/Resouces/products/<application_sapcode>`

P.S.: To be sure that the application will install exactly with the selected language after changing the text between the "InstallLanguage" tags, you can also delete all language packs except the one selected from the `application.json` folder

#### How to install an application on an unsupported version of macOS

If you don't have the most up-to-date version of macOS (for example, macOS Mojave 10.14.6) if you try to download the latest version of the application from Creative Cloud (for example Adobe InDesign CC 2022 v17.0), then Creative Cloud will give an error that the requested version of the application is incompatible with your version of macOS and you need to upgrade (in this situation to macOS 10.15 or newer macOS).

If you want to try your luck and find out if the version of the application you requested really can't work on the current version of macOS, you can download the installer with the version of the application you need using our Adobe Packager script. If you then run the installer, you will most likely immediately see error 192 and to install the downloaded version of the application on your macOS, you will need to open the `application.json` file and there, in the file search, enter "macOS 10." and see what minimum version of macOS Adobe wants for this application to work (for InDesign 2022 v17.0 it was macOS 10.15) and then in the entire `application.json` file replace this version (in my case it is "10.15") with the macOS version that you have now (in my case it is "10.14") and start the installation again.

After the installation is complete, open the Application folder and there is a folder with the installed application and if there is no crossed-out circle on the application icons, then it will start without problems and most likely will also work without problems. So on macOS Mojave I managed to work in InDesign CC 2022 v17.0, but Photoshop CC 2022 installed on macOS Mojave was displayed with a crossed circle and even changing the requirements of the minimum version of macOS in the Info.plist file inside Adobe Photoshop 2022 did not help to launch it, because, as I understand, it is compiled specifically for macOS 10.15 and newer.

## Technical documentation

- [PyInstaller Manual](https://pyinstaller.readthedocs.io/en/stable/): *"PyInstaller builds apps are compatible with the macOS release in which you run it, and following releases."*

- [Platypus](https://sveinbjorn.org/platypus): Create Mac apps from command line scripts

- [create-dmg](https://github.com/create-dmg/create-dmg): A shell script to build fancy DMGs

## Credits and notes

- The python script was initially forked from [ayyybe/ccdl.command](https://gist.github.com/ayyybe/a5f01c6f40020f9a7bc4939beeb2df1d) with a progressbar added from jorisguex's GitHub Gist fork. After ayyybe stopped updating the script it was further developed by [SaadBazaz](https://gist.github.com/SaadBazaz/37f41fffc66efea798f19582174e654c), as well as [thpryrchn](https://gist.github.com/thpryrchn/c0ea1b6793117b00494af5f05959d526) and possibly others.
- Based on these Drovosek01 created an updated version called [adobe-packager](https://github.com/Drovosek01/adobe-packager) which forms the basis of this app. The Instructions by Drovosek have also been included on this page. *(Note: The currently working script version [adobe-packager](https://github.com/Drovosek01/adobe-packager) might get updated more frequently than my app.)*
- I merely created the *CC_Offline_Package_Generator* app which is the `ccdl.py` script packaged together with Python 3 using *pyinstaller* as well as adding the *.app* and *.dmg* packaging.
- *CC Folder Icon* by [Baklay](https://www.deviantart.com/baklay/gallery) and Arrow Vectors by [Vecteezy](https://www.vecteezy.com/free-vector/arrow)
- Lincense: GPL 3.0 for my portions of the code
