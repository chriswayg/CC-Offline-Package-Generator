#!/usr/bin/env python3
import os
import json
import argparse
import urllib3
import shutil
from xml.etree import ElementTree as ET
from collections import OrderedDict
from subprocess import Popen, PIPE

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
	const driverPath = appPath.substring(0, appPath.lastIndexOf('/')) + '/products/driver.xml'
	const hyperDrivePath = '/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Setup'

	if (!installFlag) {
		app.displayAlert('Adobe Package Installer', {
			message: 'Start installation now?',
			buttons: ['Cancel', 'Install'],
			defaultButton: 'Install',
			cancelButton: 'Cancel'
		})

		const output = app.doShellScript(`${appPath}/Contents/MacOS/applet -y`, { administratorPrivileges: true })
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

#ADOBE_PRODUCTS_XML_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v4/products/all?_type=xml&channel=ccm,sti&platform=osx10,osx10-64&productType=Desktop'
ADOBE_PRODUCTS_XML_URL = 'https://prod-rel-ffc-ccm.oobesaas.adobe.com/adobe-ffc-external/core/v4/products/all?_type=xml&channel=ccm&platform=osx10,osx10-64&productType=Desktop'
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
	</RequestInfo>
</DriverInfo>
'''

DRIVER_XML_DEPENDENCY = '''			<Dependency>
				<SAPCode>{sapCode}</SAPCode>
				<BaseVersion>{version}</BaseVersion>
				<EsdDirectory>./{sapCode}</EsdDirectory>
			</Dependency>'''

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()

def dl(filename, url):
	r = http.request('GET', url, preload_content=False, headers={
		'X-Adobe-App-Id': 'accc-hdcore-desktop',
		'User-Agent': 'Adobe Application Manager 2.0',
		'X-Api-Key': 'CC_HD_ESD_1_0'
	})

	with open(filename, 'wb') as out_file:
		shutil.copyfileobj(r, out_file)

def r(url):
	return http.request('GET', url, headers={
		'X-Adobe-App-Id': 'accc-hdcore-desktop',
		'User-Agent': 'Adobe Application Manager 2.0',
		'X-Api-Key': 'CC_HD_ESD_1_0'
	}).data.decode('utf-8')

def get_products_xml():
	return ET.fromstring(r(ADOBE_PRODUCTS_XML_URL))

def parse_products_xml(products_xml):
	cdn = products_xml.find('channel/cdn/secure').text
	products = {}
	for p in products_xml.findall('channel/products/product'):
		displayName = p.find('displayName').text
		sap = p.get('id')
		version  = p.get('version')
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
	parser.add_argument('-l', '--installLanguage', help='Language code (defaults to \'en_US\'', action='store', default='en_US')
	parser.add_argument('-s', '--sapCode', help='SAP code for desired product (eg. PHSP)', action='store')
	parser.add_argument('-v', '--version', help='Version of desired product (eg. 21.0.3)', action='store')
	parser.add_argument('-d', '--destination', help='Directory to download installation files to', action='store')
	args = parser.parse_args()

	print('=================================')
	print('= Adobe macOS Package Generator =')
	print('============= 0.1.0 =============\n')

	print('Downloading products.xml\n')
	products_xml = get_products_xml()

	print('Parsing products.xml')
	products, cdn = parse_products_xml(products_xml)

	print('CDN: ' + cdn)
	print(str(len(products)) + ' products found:')
	
	sapCode = None
	if (args.sapCode):
		if products.get(args.sapCode):
			print('\nUsing provided SAP Code: '  +  args.sapCode)
			sapCode = args.sapCode
		else:
			print('\nProvided SAP Code not found in products: ' + args.sapCode)

	print('')

	if not sapCode:
		for p in products.values():
			print('[{}] {}'.format(p['sapCode'], p['displayName']))

		while sapCode is None:
			val = input('\nPlease enter the SAP Code of the desired product (eg. PHSP for Photoshop): ')
			if products.get(val):
				sapCode = val
			else:
				print('{} is not a valid SAP Code. Please use a value from the list above.'.format(val))

	product = products.get(sapCode)
	versions = product['versions']
	version = None
	if (args.version):
		if versions.get(args.version):
			print('\nUsing provided version: '  +  args.version)
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

	prodInfo = versions[version]
	installLanguage = args.installLanguage
	dest = args.destination or '{}_{}-{}'.format(sapCode, version, installLanguage)

	print('installLanguage: ' + installLanguage)
	print('sapCode: ' + sapCode)
	print('version: ' + version)
	print('dest: ' + dest)

	
	#print(get_application_json('CORE', '1.0'))

	prods_to_download = [{ 'sapCode': d['sapCode'], 'version': d['version'] } for d in prodInfo['dependencies']]
	prods_to_download.insert(0, { 'sapCode': prodInfo['sapCode'], 'version': prodInfo['version'] })
	#print(prods_to_download)

	print ('\nPreparing...\n')

	for p in prods_to_download:
		s, v = p['sapCode'], p['version']
		product_dir = os.path.join(dest, 'products', s)
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

	print ('Downloading...\n')

	for p in prods_to_download:
		s, v = p['sapCode'], p['version']
		app_json = p['application_json']
		product_dir = os.path.join(dest, 'products', s)

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
				if ((not pkg.get('Condition')) or installLanguage in pkg['Condition']): # TODO: actually parse `Condition` and check it properly (and maybe look for & add support for conditions other than installLanguage)
					noncore_pkg_count += 1
					download_urls.append(cdn + pkg['Path'])

		print('[{}_{}] Selected {} core packages and {} non-core packages'.format(s, v, core_pkg_count, noncore_pkg_count))


		for url in download_urls:
			name = url.split('/')[-1].split('?')[0]
			print('[{}_{}] Downloading {}'.format(s, v, name))
			dl(os.path.join(product_dir, name), url)

	print('\nGenerating driver.xml')

	driver = DRIVER_XML.format(
		name = product['displayName'],
		sapCode = prodInfo['sapCode'],
		version = prodInfo['version'],
		dependencies = '\n'.join([DRIVER_XML_DEPENDENCY.format(
			sapCode = d['sapCode'],
			version = d['version']
		) for d in prodInfo['dependencies']])
	)

	with open(os.path.join(dest, 'products', 'driver.xml'), 'w') as f:
		f.write(driver)
		f.close()

	print('\nCreating Install.app')

	with Popen(['/usr/bin/osacompile', '-l', 'JavaScript', '-o', os.path.join(dest, 'Install.app')], stdin=PIPE) as p:
		p.communicate(INSTALL_APP_APPLE_SCRIPT.encode('utf-8'))

	iconPath = '/Library/Application Support/Adobe/Adobe Desktop Common/HDBox/Install.app/Contents/Resources/app.icns'
	shutil.copyfile(iconPath, os.path.join(dest, 'Install.app', 'Contents', 'Resources', 'applet.icns'))

	print('\nPackage successfully created. Run Install.app inside the destination folder to install.')
