import rumps
import requests
import time
from AppKit import NSApplication, NSBundle
from custom_window import CustomWindow

info = NSBundle.mainBundle().infoDictionary()
info['LSUIElement'] = '1'

class AQIApp(rumps.App):
    def __init__(self):
        super(AQIApp, self).__init__("AQI")
        self.custom_window = None
        self.quit_button = "Quit AQI App"
        self.token = "09975e52f3b1bf07469353eabdeb513092b85f9d"
        self.base_url = "https://api.waqi.info"
        self.user_ip = self.get_user_ip()
        self.current_city = self.get_location_from_ip() or "Sarasota"
        self.menu = ["Search City", "Details", None]
        self.cached_data = None
        self.last_update_time = 0
        self.update_interval = 900  # 15 minutes
        self.timer = rumps.Timer(self.update, 900)
        self.timer.start()
        self.update(None) 

    def get_user_ip(self):
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except:
            return None

    def get_location_from_ip(self):
        ip = self.get_user_ip()
        if ip:
            url = f"{self.base_url}/feed/here/?token={self.token}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'ok':
                    return data['data']['city']['name']
        return None

    def applicationSupportsSecureRestorableState_(self, app):
        return True

    def __del__(self):
        if self.custom_window:
            self.custom_window.window.close()

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
            aqi = self.cached_data['aqi']
            self.title = f"{self.current_city}: AQI {aqi}"
        else:
            self.title = "Failed to update"

    @rumps.clicked("Search City")
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


    @rumps.clicked("Details")
    def show_details(self, _):
        if self.cached_data:
            aqi = self.cached_data['aqi']
            iaqi = self.cached_data['iaqi']
            details = f"City: {self.current_city}\n"
            details += f"AQI: {aqi}\n"
            details += f"PM2.5: {iaqi.get('pm25', {}).get('v', 'N/A')}\n"
            details += f"PM10: {iaqi.get('pm10', {}).get('v', 'N/A')}\n"
            details += f"O3: {iaqi.get('o3', {}).get('v', 'N/A')}\n"
            details += f"NO2: {iaqi.get('no2', {}).get('v', 'N/A')}\n"
            details += f"SO2: {iaqi.get('so2', {}).get('v', 'N/A')}\n"
            details += f"CO: {iaqi.get('co', {}).get('v', 'N/A')}\n"
            details += f"Temperature: {iaqi.get('t', {}).get('v', 'N/A')}°C\n"
            details += f"Humidity: {iaqi.get('h', {}).get('v', 'N/A')}%\n"
            details += f"Wind: {iaqi.get('w', {}).get('v', 'N/A')} m/s"

            if self.custom_window is None:
                self.custom_window = CustomWindow.alloc().init()
            self.custom_window.showWindow_withText_andApp_("AQI Details", details, self)
        else:
            rumps.notification("Error", "Failed to fetch AQI data", "")

    def terminate(self):
        if self.custom_window:
            self.custom_window.closeWindow()
        super(AQIApp, self).terminate()

if __name__ == "__main__":
    app = AQIApp()
    app.run()