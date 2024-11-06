from setuptools import setup

APP = ['app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
        'CFBundleName': 'AQI Display',
        'CFBundleDisplayName': 'AQI Display',
        'CFBundleIdentifier': 'com.github.jimmmmmmmmmmmy',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13',
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
        'NSLocationUsageDescription': 'AQI Display needs your location to show air quality data for your area.',
        'NSLocationWhenInUseUsageDescription': 'AQI Display needs your location to show air quality data for your area.',
        'NSPrincipalClass': 'NSApplication'
    },
    'packages': [
        'rumps',
        'requests',
        'objc',
        'Foundation',
        'AppKit',
        'sqlite3',
        'certifi',
        'charset_normalizer',
        'idna',
        'urllib3',
        'PIL',  # Added PIL package
        'PIL._imagingtk',
        'PIL._tkinter_finder',
    ],
    'includes': [
        'os',
        'json',
        're',
        'time',
        'logging',
        'datetime',
        'plistlib',
        'subprocess',
        'pathlib',
    ],
    'resources': [
        'aqi_visualization_view.py',
        'detail_window.py',
        'search_city_window.py',
        'login_item_manager.py'
    ],
    'iconfile': 'air_icon.icns',
    'arch': 'universal2',  # For Apple Silicon support
}

setup(
    name='AQI Display',
    version='1.0.0',
    author='Jimmy',
    description='A macOS menu bar app for monitoring air quality',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=[
        'py2app==0.28.8',
    ],
    install_requires=[
        'rumps @ git+https://github.com/jaredks/rumps.git@8730e7cff5768dfabecff478c0d5e3688862c1c6',
        'requests==2.32.3',
        'pyobjc-core==9.2',
        'pyobjc-framework-Cocoa==9.2',
        'pyobjc-framework-ApplicationServices==9.2',
        'certifi==2024.8.30',
        'charset-normalizer==3.4.0',
        'idna==3.10',
        'urllib3==2.2.3',
        'altgraph==0.17.4',
        'macholib==1.16.3',
        'pillow>=10.0.0'
    ]
)