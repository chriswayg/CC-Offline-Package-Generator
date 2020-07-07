# Adobe CC 2018, 2019 and 2020 Direct Download

#### Background

Adobe used to make Adobe CC trial full offline installer packages available via direct downloads as seen in the links for Adobe CC 2018 and 2019:
- [Adobe CC 2018 Direct Download Links: Creative Cloud 2018 Release](https://prodesigntools.com/adobe-cc-2018-direct-download-links.html)
- [All the New Adobe CC 2019 Direct Download Links, Now Available!](https://prodesigntools.com/adobe-cc-2019-direct-download-links.html)
- [How to Get New Adobe Creative Cloud 2020 Direct Download Links](https://prodesigntools.com/creative-cloud-2020-direct-download-links.html)
- [Why Direct Download Links Are Needed | ProDesignTools](https://prodesigntools.com/adobe-cc-no-more-direct-download-links.html#the-need)

There is no equivalent list of Adobe CC 2020 direct download links available at this time (June 2020), but the *CC_Offline_Package_Generator* script can download the files directly from Adobe and create an installer package. *(This GitHub repository is not associated with or endorsed by Adobe or ProDesign Tools. Links to ProDesign and Adobe are provided to give additional background information on the issue of Direct Downloads of the Adobe CC offline installers and to give easy access to the various ways of downloading Adobe software.)*

### Usage

1. First download and install from Adobe the [Creative Cloud - Offline Installer (180MB)](https://ccmdl.adobe.com/AdobeProducts/KCCC/CCD/5_1/osx10/ACCCx5_1_0_407.dmg ) or the [Creative Cloud - Online Installer (2.5MB)](https://creativecloud.adobe.com/apps/download/creative-cloud). The CC Offline Package Generator will not run unless the Adobe Creative Cloud app has been installed first. You need an Adobe account when installing this app.

2. Then download the [CC_Offline_Package_Generator.dmg](https://github.com/chriswayg/CC-Offline-Package-Generator/releases/), mount it and copy `CC_Offline_Package_Generator` to Applications. Run the app and it will open a Terminal window. Then follow the on-screen instructions. Tested on High Sierra, Mojave and Catalina.

Download location: https://github.com/chriswayg/CC-Offline-Package-Generator/releases/

![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage00.png)

Allow access to launch the Terminal window
![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage00b.png)

The CC_Offline_Package_Generator script will download a list of all products from Adobe and prompt you to choose the product, version, language, and destination folder for the installer.

![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage01.png)
![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage02.png)

After that you just have to sit back and wait for it to finish. The script will download all required files, and then generate a convenient installer and place it in the destination directory. When prompted, select a destination folder where you want to save the installer.

![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage03.png)

Now you can run the "Install [product]" app created in the destination folder, or save it for later offline installation.

![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage04.png)

Make sure you install the [Adobe Creative Cloud App](https://creativecloud.adobe.com/apps/download/creative-cloud) first on the computers where you intend to run the installer. Most installers should work, but some will not. See *Known Issues* below for details.

![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage05.png)
![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage06.png)
![](https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/screenshots/Usage07.png)

### Known issues

Currently most installers work, but the following are known not to work:
- Acrobat does not show up in the list, as is not made available form the Adobe servers in the same way.
- Muse (Install MUSE_2018.1.1-en_US) will stop with an error, but inside the installer app folder the app in AdobeMuse2018.1.1-core.zip will work in English. Alternatively ProDesign Tools has a download link for Muse_2018_0_CC_LS24.dmg
- Lightroom CC (Install LRCC_3.3-en_US) will stop with an error, but Lightroom Classic (Install LTRM_9.3-en_US) works fine.

### Technical notes:
The *CC_Offline_Package_Generator* binary file was built with via `pyinstaller pyinstall.spec`on macOS High Sierra 10.13.6. This means it should theoretically be compatible with High Sierra, Mojave, Catalina, and Big Sur. The python virtual environment was created with `pipenv`. The binary already includes Python inside, so there is no need to install Python to run CC_Offline_Package_Generator.

To build the binary, Homebrew and Python 3 needs to be installed. This has been tested with Python 3.7 from Homebrew. The build_prerequisites.sh` script will setup everything that is required. Some familiarity with configuring Python would be helpful. - Issue the following commands in a Terminal:

```
git clone https://github.com/chriswayg/CC-Offline-Package-Generator.git
cd CC-Offline-Package-Generator
./build_prerequisites.sh
pipenv shell
./build_app.sh
```

This will produce the `CC_Offline_Package_Generator.dmg` installer in the `/dmg` directory.

---

### Alternative - run the python script

- Run a shell script which installs Homebrew and Python first (500 MB), then runs the python script.

1. Open the Apple Terminal.app
2. Copy & paste this command and hit enter:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/chriswayg/CC-Offline-Package-Generator/master/src/install.sh)"
```
* Then run the `CC Offline Package Generator.command` in your /Applications folder and follow the on-screen instructions as explained above..

The script should be able to automatically configure itself by installing the required prerequisites in most setups: It will install Homebrew, if not already installed, then install Python 3 via Homebrew, and then add the python `requests` and the `tqdm` package to your python3 install via pip. These are the prerequisites for actually running the `ccdl.py` python script which does the actual download.

If you already have Python 3 and the `requests` and the `tqdm` packages installed, you could also run  `ccdl.py` directly:

```
python3 ccdl.py
```

---

#### How this works
The developer of the script, [ayyybe](https://gist.github.com/ayyybe), explains it:
>  I used a man-in-the-middle proxy to look at how the Creative Cloud app downloads apps, and was able to emulate it by just spoofing a few http headers for authorization. I wish it were as simple as just downloading a dmg/pkg/app but Adobe has their own proprietary installer format. All the downloads are zip files with some files, and a .pimx file, which contains instructions for the installer system (usually something like "copy these files, set these permissions on these files, register these files with the CC app") I was originally gonna implement my own parser/installer for .pimx files and handle everything myself, but I found that you can use Adobe's own installer included in the CC app by creating and providing it with a "driver.xml" file that contains the location of all the downloads, the install location, and install language, among other things. The installers made by this script aren't the actual offline installers that Adobe provides to its enterprise customers. They're generated by the script and contain all the downloads for the product and its dependencies, and the aforementioned driver.xml. When you run it and click the install button, it simply runs the HyperDrive installer included with the Adobe Creative Cloud App, and points it to the driver.xml inside the Install.app

### Credits and notes:
- the python script has been forked from [ayyybe/ccdl.command](https://gist.github.com/ayyybe/a5f01c6f40020f9a7bc4939beeb2df1d) with a progressbar added from @jorisguex's GitHub Gist fork
- the original script by @ayyybe might get updated more frequently
- I merely added the binary *CC_Offline_Package_Generator* which is `ccdl.py` packaged together with Python 3 using pyinstaller as well as added the .app and .dmg packaging.
- *CC Folder Icon* by [Baklay](https://www.deviantart.com/baklay/gallery) and Arrow Vectors by [Vecteezy](https://www.vecteezy.com/free-vector/arrow)
- Lincense: GPL 3.0 for my portions of the code
