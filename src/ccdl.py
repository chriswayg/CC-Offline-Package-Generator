#!/usr/bin/env python3
import os
import json
import argparse
import requests

session = requests.Session()
import shutil
from xml.etree import ElementTree as ET
from collections import OrderedDict
from subprocess import Popen, PIPE

from tqdm import tqdm

VERSION = 3
VERSION_STR = '0.1.2.2'

INSTALL_APP_APPLE_SCRIPT = '''
const app = Application.currentApplication()
app.includeStandardAdditions = true

ObjC.import('Cocoa')
ObjC.import('stdio')
ObjC.import('stdlib')

ObjC.registerSubclass({
    name: 'HandleDataAction',
    methods: {
        'outData:': {
            types: ['void', ['id']],
            implementation: function(sender) {
                const data = sender.object.availableData
                if (data.length !== '0') {
                    const output = $.NSString.alloc.initWithDataEncoding(data, $.NSUTF8StringEncoding).js
                    const res = parseOutput(output)
                    if (res) {
                        switch (res.type) {
                            case 'progress':
                                Progress.additionalDescription = `Progress: ${res.data}%`
                                Progress.completedUnitCount = res.data
                                break
                            case 'exit':
                                if (res.data === 0) {
                                    $.puts(JSON.stringify({ title: 'Installation succeeded' }))
                                } else {
                                    $.puts(JSON.stringify({ title: `Failed with error code ${res.data}` }))
                                }
                                $.exit(0)
                                break
                        }
                    }
                    sender.object.waitForDataInBackgroundAndNotify
                } else {
                    $.NSNotificationCenter.defaultCenter.removeObserver(this)
                }
            }
        }
    }
})

function parseOutput(output) {
    let matches

    matches = output.match(/Progress: ([0-9]{1,3})%/)
    if (matches) {
        return {
            type: 'progress',
            data: parseInt(matches[1], 10)
        }
    }

    matches = output.match(/Exit Code: ([0-9]{1,3})/)
    if (matches) {
        return {
            type: 'exit',
            data: parseInt(matches[1], 10)
        }
    }

    return false
}


function run() {
    const args = $.NSProcessInfo.processInfo.arguments
    const argv = []
    const argc = args.count
    for (var i = 0; i < argc; i++) {
        argv.push(ObjC.unwrap(args.objectAtIndex(i)))
    }
    delete args

    const installFlag = argv.indexOf('-y') > -1

    const appPath = app.pathTo(this).toString()
    //const driverPath = appPath.substring(0, appPath.lastIndexOf('/')) + '/products/driver.xml'
    const driverPath = appPath + '/Contents/Resources/products/driver.xml'
    const hyperDrivePath = '/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Setup'

    if (!installFlag) {
        app.displayAlert('Adobe Package Installer', {
            message: 'Start installation now?',
            buttons: ['Cancel', 'Install'],
            defaultButton: 'Install',
            cancelButton: 'Cancel'
        })

        const output = app.doShellScript(`"${appPath}/Contents/MacOS/applet" -y`, { administratorPrivileges: true })
        const alert = JSON.parse(output)
        alert.params ? app.displayAlert(alert.title, alert.params) : app.displayAlert(alert.title)
        return
    }

    const stdout = $.NSPipe.pipe
    const task = $.NSTask.alloc.init

    task.executableURL = $.NSURL.alloc.initFileURLWithPath(hyperDrivePath)
    task.arguments = $(['--install=1', '--driverXML=' + driverPath])
    task.standardOutput = stdout

    const dataAction = $.HandleDataAction.alloc.init
    $.NSNotificationCenter.defaultCenter.addObserverSelectorNameObject(dataAction, 'outData:', $.NSFileHandleDataAvailableNotification, $.initialOutputFile)

    stdout.fileHandleForReading.waitForDataInBackgroundAndNotify

    let err = $.NSError.alloc.initWithDomainCodeUserInfo('', 0, '')
    const ret = task.launchAndReturnError(err)
    if (!ret) {
        $.puts(JSON.stringify({
            title: 'Error',
            params: {
                message: 'Failed to launch task: ' + err.localizedDescription.UTF8String
            }
        }))
        $.exit(0)
    }

    Progress.description =  "Installing packages..."
    Progress.additionalDescription = "Preparing…"
    Progress.totalUnitCount = 100

    task.waitUntilExit
}
'''

# ADOBE_PRODUCTS_XML_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v4/products/all?_type=xml&channel=ccm,sti&platform=osx10,osx10-64&productType=Desktop'
POPULATE_ADOBE_COOKIES_URL = 'https://adobeid-na1.services.adobe.com/ims/check/v4/token?client_id=CreativeCloud_v5_1'
ADOBE_PRODUCTS_XML_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v4/products/all?_type=xml&channel=ccm&platform=osx10-64&productType=Desktop'
ADOBE_APPLICATION_JSON_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v2/applications?name={name}&version={version}&platform={platform}'

DRIVER_XML = '''<DriverInfo>
    <ProductInfo>
        <Name>Adobe {name}</Name>
        <SAPCode>{sapCode}</SAPCode>
        <CodexVersion>{version}</CodexVersion>
        <Platform>osx10-64</Platform>
        <EsdDirectory>./{sapCode}</EsdDirectory>
        <Dependencies>
{dependencies}
        </Dependencies>
    </ProductInfo>
    <RequestInfo>
        <InstallDir>/Applications</InstallDir>
        <InstallLanguage>{language}</InstallLanguage>
    </RequestInfo>
</DriverInfo>
'''

DRIVER_XML_DEPENDENCY = '''			<Dependency>
                <SAPCode>{sapCode}</SAPCode>
                <BaseVersion>{version}</BaseVersion>
                <EsdDirectory>./{sapCode}</EsdDirectory>
            </Dependency>'''

ADOBE_REQ_HEADERS = {
    'X-Adobe-App-Id': 'accc-hdcore-desktop',
    'User-Agent': 'Adobe Application Manager 2.0',
    'X-Api-Key': 'CC_HD_ESD_1_0'
}


def dl(filename, url, name):
    with session.get(url, stream=True, headers=ADOBE_REQ_HEADERS) as r:
        total_size = int(r.headers["Content-Length"])
        chunkSize = 1024
        bars = int(total_size / chunkSize)
        with open(filename, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size=chunkSize), total=bars, unit='B', unit_scale=True,
                              unit_divisor=chunkSize, desc=name,
                              bar_format="{l_bar}{bar} {n_fmt}/{total_fmt}(k in MB) [{remaining} remaining]",
                              leave=False, dynamic_ncols=True, smoothing=0):
                f.write(chunk)


def r(url):
    req = session.get(url, headers=ADOBE_REQ_HEADERS)
    req.encoding = 'utf-8'
    return req.text


def get_products_xml():
    return ET.fromstring(r(ADOBE_PRODUCTS_XML_URL))


def parse_products_xml(products_xml):
    cdn = products_xml.find('channel/cdn/secure').text
    products = {}
    for p in products_xml.findall('channel/products/product'):
        displayName = p.find('displayName').text
        sap = p.get('id')
        version = p.get('version')
        dependencies = list(p.find('platforms/platform/languageSet/dependencies'))

        if not products.get(sap):
            products[sap] = {
                'displayName': displayName,
                'sapCode': sap,
                'versions': OrderedDict()
            }

        products[sap]['versions'][version] = {
            'sapCode': sap,
            'version': version,
            'dependencies': [{
                'sapCode': d.find('sapCode').text, 'version': d.find('baseVersion').text
            } for d in dependencies]
        }

    return products, cdn


def get_application_json(sapCode, version):
    try:
        return json.loads(r(ADOBE_APPLICATION_JSON_URL.format(name=sapCode, version=version, platform='osx10-64')))
    except json.decoder.JSONDecodeError:
        return json.loads(r(ADOBE_APPLICATION_JSON_URL.format(name=sapCode, version=version, platform='osx10')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--installLanguage', help='Language code (eg. en_US)', action='store')
    parser.add_argument('-s', '--sapCode', help='SAP code for desired product (eg. PHSP)', action='store')
    parser.add_argument('-v', '--version', help='Version of desired product (eg. 21.0.3)', action='store')
    parser.add_argument('-d', '--destination', help='Directory to download installation files to', action='store')
    args = parser.parse_args()

    print('====================================')
    print('=== CC Offline Package Generator ===')
    print('============== {} =============\n'.format(VERSION_STR))
    print('More info: https://github.com/chriswayg/CC-Offline-Package-Generator')
    print('           https://gist.github.com/ayyybe/a5f01c6f40020f9a7bc4939beeb2df1d\n')

    if (not os.path.isfile('/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Setup')):
        print(
            'Creative Cloud app not found.\nPlease download and install from: https://creativecloud.adobe.com/apps/download/creative-cloud\n')
        exit(1)

    #print('Populating .adobe.com cookies')
    session.post(POPULATE_ADOBE_COOKIES_URL, headers=ADOBE_REQ_HEADERS)

    print('Downloading products.xml\n')
    products_xml = get_products_xml()

    print('Parsing products.xml')
    products, cdn = parse_products_xml(products_xml)

    print('CDN: ' + cdn)
    print(str(len(products)) + ' products found:')

    sapCode = None
    if (args.sapCode):
        if products.get(args.sapCode):
            print('\nUsing provided SAP Code: ' + args.sapCode)
            sapCode = args.sapCode
        else:
            print('\nProvided SAP Code not found in products: ' + args.sapCode)

    print('')

    if not sapCode:
        for p in products.values():
            print('[{}] {}'.format(p['sapCode'], p['displayName']))

        while sapCode is None:
            val = input('\nPlease enter the SAP Code of the desired product (eg. PHSP for Photoshop): ')
            if val == 'APRO':
                print(
                    '\033[1;31mAcrobat is currently broken, please sit tight while I try to find a solution.\nAll other products are functional.\033[0m')
            elif products.get(val):
                sapCode = val
            else:
                print('{} is not a valid SAP Code. Please use a value from the list above.'.format(val))

    product = products.get(sapCode)
    versions = product['versions']
    version = None
    if (args.version):
        if versions.get(args.version):
            print('\nUsing provided version: ' + args.version)
            version = args.version
        else:
            print('\nProvided version not found: ' + args.version)

    print('')

    if not version:
        for v in reversed(versions.values()):
            print('{} {}'.format(product['displayName'], v['version']))

        while version is None:
            val = input('\nPlease enter the desired version (eg. 21.0.3): ')
            if versions.get(val):
                version = val
            else:
                print('{} is not a valid version. Please use a value from the list above.'.format(val))

    print('')

    langs = ['en_US', 'en_GB', 'en_IL', 'en_AE', 'es_ES', 'es_MX', 'pt_BR', 'fr_FR', 'fr_CA', 'fr_MA', 'it_IT', 'de_DE',
             'nl_NL', 'ru_RU', 'uk_UA', 'zh_TW', 'zh_CN', 'ja_JP', 'ko_KR', 'pl_PL', 'hu_HU', 'cs_CZ', 'tr_TR', 'sv_SE',
             'nb_NO', 'fi_FI', 'da_DK']
    installLanguage = None
    if (args.installLanguage):
        if (args.installLanguage in langs):
            print('\nUsing provided language: ' + args.installLanguage)
            installLanguage = args.installLanguage
        else:
            print('\nProvided language not available: ' + args.installLanguage)

    if not installLanguage:
        print('Available languages: {}'.format(', '.join(langs)))
        while installLanguage is None:
            val = input('\nPlease enter the desired install language, or nothing for [en_US]: ') or 'en_US'
            if (val in langs):
                installLanguage = val
            else:
                print('{} is not available. Please use a value from the list above.'.format(val))

    dest = None
    if (args.destination):
        print('\nUsing provided destination: ' + args.destination)
        dest = args.destination
    else:
        print('\nPlease navigate to the desired downloads folder, or cancel to abort.')
        p = Popen(['/usr/bin/osascript', '-e',
                   'tell application (path to frontmost application as text)\nset _path to choose folder\nPOSIX path of _path\nend'],
                  stdout=PIPE)
        dest = p.communicate()[0].decode('utf-8').strip()
        if (p.returncode != 0):
            print('Exiting...')
            exit()

    print('')

    install_app_name = 'Install {}_{}-{}.app'.format(sapCode, version, installLanguage)
    install_app_path = os.path.join(dest, install_app_name)

    print('sapCode: ' + sapCode)
    print('version: ' + version)
    print('installLanguage: ' + installLanguage)
    print('dest: ' + install_app_path)

    prodInfo = versions[version]
    prods_to_download = [{'sapCode': d['sapCode'], 'version': d['version']} for d in prodInfo['dependencies']]
    prods_to_download.insert(0, {'sapCode': prodInfo['sapCode'], 'version': prodInfo['version']})

    print('\nCreating {}'.format(install_app_name))

    install_app_path = os.path.join(dest, 'Install {}_{}-{}.app'.format(sapCode, version, installLanguage))
    with Popen(['/usr/bin/osacompile', '-l', 'JavaScript', '-o', os.path.join(dest, install_app_path)],
               stdin=PIPE) as p:
        p.communicate(INSTALL_APP_APPLE_SCRIPT.encode('utf-8'))

    icon_path = '/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Install.app/Contents/Resources/app.icns'
    shutil.copyfile(icon_path, os.path.join(install_app_path, 'Contents', 'Resources', 'applet.icns'))

    products_dir = os.path.join(install_app_path, 'Contents', 'Resources', 'products')

    print('\nPreparing...\n')

    for p in prods_to_download:
        s, v = p['sapCode'], p['version']
        product_dir = os.path.join(products_dir, s)
        app_json_path = os.path.join(product_dir, 'application.json')

        print('[{}_{}] Downloading application.json'.format(s, v))
        app_json = get_application_json(s, v)
        p['application_json'] = app_json

        print('[{}_{}] Creating folder for product'.format(s, v))
        os.makedirs(product_dir, exist_ok=True)

        print('[{}_{}] Saving application.json'.format(s, v))
        with open(app_json_path, 'w') as file:
            json.dump(app_json, file, separators=(',', ':'))

        print('')

    print('Downloading...\n')

    for p in prods_to_download:
        s, v = p['sapCode'], p['version']
        app_json = p['application_json']
        product_dir = os.path.join(products_dir, s)

        print('[{}_{}] Parsing available packages'.format(s, v))
        core_pkg_count = 0
        noncore_pkg_count = 0
        packages = app_json['Packages']['Package']
        download_urls = []
        for pkg in packages:
            if pkg.get('Type') and pkg['Type'] == 'core':
                core_pkg_count += 1
                download_urls.append(cdn + pkg['Path'])
            else:
                if ((not pkg.get('Condition')) or installLanguage in pkg[
                    'Condition']):  # TODO: actually parse `Condition` and check it properly (and maybe look for & add support for conditions other than installLanguage)
                    noncore_pkg_count += 1
                    download_urls.append(cdn + pkg['Path'])

        print('[{}_{}] Selected {} core packages and {} non-core packages'.format(s, v, core_pkg_count,
                                                                                  noncore_pkg_count))

        for url in download_urls:
            name = url.split('/')[-1].split('?')[0]
            print('[{}_{}] Downloading {}'.format(s, v, name))
            dl(os.path.join(product_dir, name), url, name)

    print('\nGenerating driver.xml')

    driver = DRIVER_XML.format(
        name=product['displayName'],
        sapCode=prodInfo['sapCode'],
        version=prodInfo['version'],
        dependencies='\n'.join([DRIVER_XML_DEPENDENCY.format(
            sapCode=d['sapCode'],
            version=d['version']
        ) for d in prodInfo['dependencies']]),
        language=installLanguage
    )

    with open(os.path.join(products_dir, 'driver.xml'), 'w') as f:
        f.write(driver)
        f.close()

    print('\nPackage successfully created. Run {} to install.'.format(install_app_path))
