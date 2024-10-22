import objc
from AppKit import (NSView, NSColor, NSBezierPath, NSFont, NSFontAttributeName, 
                    NSForegroundColorAttributeName, NSString, NSMakePoint, NSMakeRect,
                    NSTextAlignmentCenter, NSParagraphStyleAttributeName, NSLineBreakByWordWrapping)

from Foundation import NSMutableParagraphStyle
from datetime import datetime

class AQIVisualizationView(NSView):
    @objc.python_method
    def initWithFrame_andData_(self, frame, data):
        self = objc.super(AQIVisualizationView, self).initWithFrame_(frame)
        if self:
            self.data = list(data[-24:])  # Last 24 hours, most recent last
            self.setup()
        return self

    @objc.python_method
    def setup(self):
        self.textColor = NSColor.blackColor()
        self.headerHeight = 150  # Space for header
        
        self.pollutant_levels = {
            'pm25': [
                (0, 50, NSColor.systemGreenColor()),
                (51, 100, NSColor.yellowColor()),
                (101, 150, NSColor.orangeColor()),
                (151, 200, NSColor.redColor()),
                (201, 300, NSColor.purpleColor()),
                (301, 500, NSColor.darkGrayColor())
            ],
            'pm10': [
                (0, 50, NSColor.systemGreenColor()),
                (51, 100, NSColor.yellowColor()),
                (101, 150, NSColor.orangeColor()),
                (251, 200, NSColor.redColor()),
                (302, 300, NSColor.purpleColor()),
                (301, 500, NSColor.darkGrayColor())
            ],
            # For gases that typically stay under 50, we'll use a gradient approach
            'o3': [(0, 50, None)],  # Will use interpolation
            'no2': [(0, 50, None)],  # Will use interpolation
            'so2': [(0, 50, None)],  # Will use interpolation
            'co': [(0, 50, None)],   # Will use interpolation
        }
        self.pressure_range = {
            'min': 965.1,  # Yellow
            'max': 1040.0  # Orange
        }
        # Static colors for non-pollutant metrics
        self.static_colors = {
            'temperature': NSColor.orangeColor(),
            'humidity': NSColor.magentaColor(),
            'wind': NSColor.lightGrayColor()
        }
        
        self.metric_labels = {
            'pm25': 'PM2.5', 'pm10': 'PM10', 'o3': 'O3', 'no2': 'NO2', 'so2': 'SO2',
            'co': 'CO', 'temperature': 'Temp.', 'pressure': 'Pressure',
            'humidity': 'Humidity', 'wind': 'Wind'
        }
        

        self.metrics = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'temperature', 'pressure', 'humidity', 'wind']
        self.chartPadding = 5
        self.labelWidth = 55
        self.currentValueWidth = 35
        self.minMaxWidth = 55
        self.aqi_levels = [
            (0, 50, "Good", NSColor.systemGreenColor()),
            (51, 100, "Moderate", NSColor.yellowColor()),
            (101, 150, "Unhealthy for Sensitive Groups", NSColor.orangeColor()),
            (151, 200, "Unhealthy", NSColor.redColor()),
            (201, 300, "Very Unhealthy", NSColor.purpleColor()),
            (301, 500, "Hazardous", NSColor.darkGrayColor())
        ]


    def drawRect_(self, dirtyRect):
        NSColor.windowBackgroundColor().setFill()
        NSBezierPath.fillRect_(dirtyRect)
        
        # Draw main sections
        self.drawHeader()
        self.drawCharts()

    @objc.python_method
    def get_aqi_info(self, aqi):
        for low, high, text, color in self.aqi_levels:
            if low <= aqi <= high:
                return color, text
        return NSColor.blackColor(), "Unknown"

    @objc.python_method
    def drawHeader(self):
        if not self.data:
            return

        headerRect = NSMakeRect(0, self.bounds().size.height - self.headerHeight, 
                            self.bounds().size.width, self.headerHeight)
        
        # Get latest data point
        latest_data = self.data[0]
        city_name = latest_data[1]  # City is index 1 in the tuple
        aqi_value = latest_data[2]  # AQI is index 2 in the tuple
        timestamp = latest_data[0]  # Timestamp is index 0
    
        # Parse and format the timestamp
        dt = datetime.fromisoformat(timestamp)
        formatted_time = dt.strftime("%A %I:%M%p").replace("AM", "am").replace("PM", "pm")
        # Remove leading zero from hour if present
        formatted_time = formatted_time.lstrip("0")
            
        # Draw city name - increased vertical space and moved up
        cityAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(16),
            NSForegroundColorAttributeName: NSColor.blackColor(),
        }
        # Increased height from 30 to 50 for two lines, and adjusted y position
        cityRect = NSMakeRect(10, headerRect.origin.y + 65, 
                            headerRect.size.width - 20, 50)
        
        # Create paragraph style for city name to handle wrapping
        cityParagraph = NSMutableParagraphStyle.alloc().init()
        cityParagraph.setLineBreakMode_(NSLineBreakByWordWrapping)
        cityAttrs[NSParagraphStyleAttributeName] = cityParagraph
        
        NSString.stringWithString_(city_name).drawInRect_withAttributes_(cityRect, cityAttrs)
        
        # Draw AQI box and text
        aqi_color, aqi_text = self.get_aqi_info(aqi_value)
        
        # Rounded corners for my friends
        aqiBoxRect = NSMakeRect(10, headerRect.origin.y + 15, 80, 60)
        roundedPath = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(aqiBoxRect, 10.0, 10.0)
        aqi_color.setFill()
        roundedPath.fill()
        
        # if you change this you HAVE to change aqiTextRect
        aqiAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(32),
            NSForegroundColorAttributeName: NSColor.whiteColor(),
        }
        paragraph = NSMutableParagraphStyle.alloc().init()
        paragraph.setAlignment_(NSTextAlignmentCenter)
        aqiAttrs[NSParagraphStyleAttributeName] = paragraph
        
        # origin.y + 10 and width,40 is as close as it gets to center do not FUCK this
        aqiTextRect = NSMakeRect(aqiBoxRect.origin.x, 
                                 aqiBoxRect.origin.y + 10, 
                                aqiBoxRect.size.width, 40)
        
        NSString.stringWithString_(str(aqi_value)).drawInRect_withAttributes_(
            aqiTextRect, aqiAttrs)
        
        # Higher makes text go higher "AQI QUALITIATIVE READING"
        qualTextRect = NSMakeRect(100, headerRect.origin.y + 45, 
                                headerRect.size.width - 110, 30)
        qualAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(20),
            NSForegroundColorAttributeName: aqi_color,
        }
        NSString.stringWithString_(aqi_text).drawInRect_withAttributes_(
            qualTextRect, qualAttrs)
        
        # Last updated time - adjusted position
        timestamp = latest_data[0]  # Timestamp is index 0
        updateAttrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(12),
            NSForegroundColorAttributeName: NSColor.grayColor(),
        }
        ## +15 is the rectangle height so YLOCish, +35 is the size of the rectangle
        updateRect = NSMakeRect(100, headerRect.origin.y + 15, 
                            headerRect.size.width - 110, 35)
        NSString.stringWithString_(f"Updated: {formatted_time}").drawInRect_withAttributes_(
        updateRect, updateAttrs)

    def interpolate_colors(self, color1, color2, progress):
        """Helper method to interpolate between two NSColors"""
        # Convert colors to RGB color space
        color1_rgb = color1.colorUsingColorSpaceName_("NSCalibratedRGBColorSpace")
        color2_rgb = color2.colorUsingColorSpaceName_("NSCalibratedRGBColorSpace")
        
        # Interpolate between colors
        r = color1_rgb.redComponent() + (color2_rgb.redComponent() - color1_rgb.redComponent()) * progress
        g = color1_rgb.greenComponent() + (color2_rgb.greenComponent() - color1_rgb.greenComponent()) * progress
        b = color1_rgb.blueComponent() + (color2_rgb.blueComponent() - color1_rgb.blueComponent()) * progress
        
        return NSColor.colorWithRed_green_blue_alpha_(r, g, b, 1.0)

    @objc.python_method
    def get_pressure_color(self, value):
        """Get color for pressure value based on the defined range"""
        min_pressure = self.pressure_range['min']
        max_pressure = self.pressure_range['max']
        
        # Clamp value to our range
        value = max(min_pressure, min(max_pressure, value))
        
        # Calculate progress through the range
        progress = (value - min_pressure) / (max_pressure - min_pressure)
        
        # Interpolate between yellow and orange
        return self.interpolate_colors(NSColor.systemBlueColor(), NSColor.blueColor(), progress)

    @objc.python_method
    def get_color_for_metric(self, metric, value):
        # Special handling for pressure
        if metric == 'pressure':
            return self.get_pressure_color(value)
            
        if metric in self.static_colors:
            return self.static_colors[metric]
        
        if metric in self.pollutant_levels:
            if metric in ['o3', 'no2', 'so2', 'co']:
                # For gases that typically stay under 50, interpolate between green and yellow
                if value > 50:
                    return NSColor.yellowColor()
                # Interpolate between green and yellow based on the value
                progress = value / 50.0
                return self.interpolate_colors(NSColor.systemGreenColor(), NSColor.yellowColor(), progress)
            else:
                # For PM2.5 and PM10, use their defined levels
                levels = self.pollutant_levels[metric]
                for low, high, color in levels:
                    if low <= value <= high:
                        return color
                return NSColor.darkGrayColor()  # Default color if out of all ranges
        
        return NSColor.grayColor()  # Default color for unknown metrics


    @objc.python_method
    def drawCharts(self):
        if not self.data:
            self.drawNoDataAvailable()
            return

        # Adjust available height to account for header
        availableHeight = self.bounds().size.height - self.headerHeight
        chart_height = (availableHeight / len(self.metrics)) - self.chartPadding
        
        for i, metric in enumerate(reversed(self.metrics)):
            y_position = i * (chart_height + self.chartPadding)
            self.drawChart(metric, NSMakeRect(0, y_position, self.bounds().size.width, chart_height))

    @objc.python_method
    def drawChart(self, metric, rect):
        def adjust_histogram_bounds(min_value, max_value):
            if metric == 'pressure':
                # Fixed bounds for pressure
                return min_value * .99, max_value * 1.01
            adjusted_min = min_value * 0.75
            adjusted_max = max_value * 1.25
            return adjusted_min, adjusted_max

        data_index_map = {
            'timestamp': 0, 'city': 1, 'aqi': 2, 'pm25': 3, 'pm10': 4, 
            'o3': 5, 'no2': 6, 'so2': 7, 'co': 8, 'temperature': 9, 
            'pressure': 10, 'humidity': 11, 'wind': 12
        }
        metric_index = data_index_map[metric]
        
        metric_data = [row[metric_index] if row[metric_index] is not None else None for row in self.data]
        valid_data = [float(value) for value in metric_data if value is not None]

        # Draw metric name and current reading as before...
        label_attrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(10),
            NSForegroundColorAttributeName: self.textColor
        }
        NSString.stringWithString_(self.metric_labels[metric]).drawAtPoint_withAttributes_(
            NSMakePoint(5, rect.origin.y + rect.size.height - 25), label_attrs)

        current_value = metric_data[0] if metric_data and metric_data[0] is not None else '-'
        NSString.stringWithString_(str(round(current_value) if current_value != '-' else '-')).drawAtPoint_withAttributes_(
            NSMakePoint(self.labelWidth, rect.origin.y + rect.size.height - 25), label_attrs)

        # Draw histogram with dynamic colors
        if valid_data:
            max_value = max(valid_data)
            min_value = min(valid_data)
            adjusted_min, adjusted_max = adjust_histogram_bounds(min_value, max_value)
            value_range = adjusted_max - adjusted_min

            histogram_rect = NSMakeRect(
                self.labelWidth + self.currentValueWidth, 
                rect.origin.y,
                self.bounds().size.width - self.labelWidth - self.currentValueWidth - self.minMaxWidth,
                rect.size.height
            )
            bar_width = histogram_rect.size.width / len(self.data)
            
            for i, value in enumerate(metric_data):
                if value is not None:
                    if value_range == 0:
                        height = histogram_rect.size.height * 0.5
                    else:
                        normalized_value = (float(value) - adjusted_min) / value_range
                        height = normalized_value * histogram_rect.size.height

                    x_position = histogram_rect.origin.x + i * bar_width
                    bar_rect = NSMakeRect(x_position, rect.origin.y, bar_width - 1, height)
                    
                    # Get color based on the value
                    color = self.get_color_for_metric(metric, float(value))
                    color.setFill()
                    NSBezierPath.fillRect_(bar_rect)

            # Draw min and max values...
            value_attrs = {
                NSFontAttributeName: NSFont.systemFontOfSize_(10),
                NSForegroundColorAttributeName: self.textColor
            }
            min_x = self.bounds().size.width - self.minMaxWidth + 5
            max_x = self.bounds().size.width - self.minMaxWidth / 2 + 5
            
            NSString.stringWithString_(f"{min_value:.0f}").drawAtPoint_withAttributes_(
                NSMakePoint(min_x, rect.origin.y + rect.size.height - 25), value_attrs)
            NSString.stringWithString_(f"{max_value:.0f}").drawAtPoint_withAttributes_(
                NSMakePoint(max_x, rect.origin.y + rect.size.height - 25), value_attrs)
        else:
            no_data_attrs = {
                NSFontAttributeName: NSFont.systemFontOfSize_(10),
                NSForegroundColorAttributeName: NSColor.grayColor()
            }
            NSString.stringWithString_("No Data").drawAtPoint_withAttributes_(
                NSMakePoint(self.labelWidth + self.currentValueWidth, rect.origin.y + rect.size.height / 2), no_data_attrs)



    @objc.python_method
    def drawNoDataAvailable(self):
        attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(14),
            NSForegroundColorAttributeName: self.textColor
        }
        message = "No data available"
        NSString.stringWithString_(message).drawAtPoint_withAttributes_(
            NSMakePoint(self.bounds().size.width / 2 - 50, self.bounds().size.height / 2), attrs)