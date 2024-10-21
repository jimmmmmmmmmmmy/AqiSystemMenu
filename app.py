import rumps
import requests
import time
from AppKit import NSApplication, NSBundle
from custom_window import CustomWindow
from search_city_window import SearchCityWindow

info = NSBundle.mainBundle().infoDictionary()
info['LSUIElement'] = '1'

class OpenAir(rumps.App):
    def __init__(self):
        super(OpenAir, self).__init__("AQI")
        self.quit_button = "Quit OpenAir"
        self.token = "09975e52f3b1bf07469353eabdeb513092b85f9d"
        self.base_url = "https://api.waqi.info"
        self.user_ip = self.get_user_ip()
        self.current_city = self.get_location_from_ip() or "Sarasota"
        self.format_options = {
            'City': True,
            'AQI': True,
            'PM2.5': False,
            'PM10': False,
            'O\u2083': False,
            'NO\u2082': False,
            'SO\u2082': False,
            'CO': False,
            'Temperature': False,
            'Humidity': False,
            'Wind': False
        }
        self.setup_menu()
        self.cached_data = None
        self.last_update_time = 0
        self.update_interval = 900  # 15 minutes
        self.timer = rumps.Timer(self.update, 900)
        self.timer.start()
        self.update(None)  # Initial update
        self.search_window = None
        self.custom_window = CustomWindow.alloc().init()



    def setup_menu(self):
        format_menu = rumps.MenuItem("Format Options")
        for option in self.format_options:
            item = rumps.MenuItem(option, callback=self.toggle_format_option)
            item.state = self.format_options[option]
            format_menu.add(item)

        format_menu.add(None)
        
        format_menu.add(rumps.MenuItem("Reset", callback=self.reset_format_options))
        
        self.menu = ["Search City", format_menu, "Details...", None]

    def toggle_format_option(self, sender):
        self.format_options[sender.title] = not sender.state
        sender.state = self.format_options[sender.title]
        self.update(None)

    def reset_format_options(self, _):
        for option in self.format_options:
            self.format_options[option] = option in ['City', 'AQI']
        self.update_format_menu()
        self.update(None)

    def update_format_menu(self):
        format_menu = self.menu["Format Options"]
        for item in format_menu.values():
            if isinstance(item, rumps.MenuItem) and item.title in self.format_options:
                item.state = self.format_options[item.title]

    def get_user_ip(self):
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except:
            return None

    def get_location_from_ip(self):
        if self.user_ip:
            url = f"{self.base_url}/feed/here/?token={self.token}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    return data['data']['city']['name']
        return None

    def applicationSupportsSecureRestorableState_(self, app):
        return True

    def get_aqi_data(self, city):
        url = f"{self.base_url}/feed/{city}/?token={self.token}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'ok':
                return data['data']
        return None

    def update(self, _):
        current_time = time.time()
        if current_time - self.last_update_time > self.update_interval or self.cached_data is None:
            self.cached_data = self.get_aqi_data(self.current_city)
            self.last_update_time = current_time

        if self.cached_data:
            self.update_title()
        else:
            self.title = "Failed to update"

    def update_title(self):
        title_parts = []
        data = self.cached_data
        iaqi = data.get('iaqi', {})

        if self.format_options['City']:
            title_parts.append(self.current_city)
        if self.format_options['AQI']:
            title_parts.append(f"AQI: {data['aqi']}")
        if self.format_options['PM2.5']:
            title_parts.append(f"PM2.5: {iaqi.get('pm25', {}).get('v', 'N/A')}")
        if self.format_options['PM10']:
            title_parts.append(f"PM10: {iaqi.get('pm10', {}).get('v', 'N/A')}")
        if self.format_options['O\u2083']:
            title_parts.append(f"O\u2083: {iaqi.get('o3', {}).get('v', 'N/A')}")
        if self.format_options['NO\u2082']:
            title_parts.append(f"NO\u2082 {iaqi.get('no2', {}).get('v', 'N/A')}")
        if self.format_options['SO\u2082']:
            title_parts.append(f"SO\u2082 {iaqi.get('so2', {}).get('v', 'N/A')}")
        if self.format_options['CO']:
            title_parts.append(f"CO {iaqi.get('co', {}).get('v', 'N/A')}")
        if self.format_options['Temperature']:
            title_parts.append(f"{iaqi.get('t', {}).get('v', 'N/A')}°C")
        if self.format_options['Humidity']:
            title_parts.append(f"RH: {iaqi.get('h', {}).get('v', 'N/A')}%")
        if self.format_options['Wind']:
            title_parts.append(f"{iaqi.get('w', {}).get('v', 'N/A')}m/s")

        self.title = " | ".join(title_parts)

    @rumps.clicked("About")
    def search_city(self, _):
        response = rumps.Window('Enter city name:', 'Search City', default_text=self.current_city).run()
        if response.clicked:
            new_city = response.text
            data = self.get_aqi_data(new_city)
            if data:
                self.current_city = new_city
                self.cached_data = data
                self.update(None)
            else:
                rumps.notification("Error", f"Could not find data for {new_city}", "")

    @rumps.clicked("Search City")
    def search_city(self, _):
        if self.search_window is None:
            self.search_window = SearchCityWindow.alloc().initWithApp_(self)
        self.search_window.showWindow()

    @rumps.clicked("Details...")
    def show_details(self, _):
        if self.cached_data:
            aqi = self.cached_data['aqi']
            iaqi = self.cached_data['iaqi']
            details = f"City: {self.current_city}\n"
            details += f"AQI: {aqi}\n"
            details += f"PM2.5: {iaqi.get('pm25', {}).get('v', 'N/A')}\n"
            details += f"PM10: {iaqi.get('pm10', {}).get('v', 'N/A')}\n"
            details += f"O\u2083: {iaqi.get('o3', {}).get('v', 'N/A')}\n"
            details += f"NO\u2082: {iaqi.get('no2', {}).get('v', 'N/A')}\n"
            details += f"SO\u2082: {iaqi.get('so2', {}).get('v', 'N/A')}\n"
            details += f"CO: {iaqi.get('co', {}).get('v', 'N/A')}\n"
            details += f"Temperature: {iaqi.get('t', {}).get('v', 'N/A')}°C\n"
            details += f"Humidity: {iaqi.get('h', {}).get('v', 'N/A')}%\n"
            details += f"Wind: {iaqi.get('w', {}).get('v', 'N/A')} m/s"

            self.custom_window.showWindow_withText_("AQI Details", details)
        else:
            rumps.notification("Error", "Failed to fetch AQI data", "")

    def terminate(self):
        if self.custom_window:
            self.custom_window.dealloc()
            self.custom_window = None
        super(OpenAir, self).terminate()

if __name__ == "__main__":
    app = OpenAir()
    app.run()