import objc
from AppKit import (NSView, NSColor, NSBezierPath, NSFont, NSFontAttributeName, 
                    NSForegroundColorAttributeName, NSString, NSMakePoint, NSMakeRect, 
                    NSTextAlignmentCenter, NSParagraphStyleAttributeName, NSBackgroundColorAttributeName)
from Foundation import NSMutableParagraphStyle
from datetime import datetime


class AQIVisualizationView(NSView):
    @objc.python_method
    def initWithFrame_andData_(self, frame, data):
        self = objc.super(AQIVisualizationView, self).initWithFrame_(frame)
        if self:
            self.data = data
            self.setup()
        return self

    @objc.python_method
    def setup(self):
        self.textColor = NSColor.blackColor()
        self.barColors = {
            'pm25': NSColor.greenColor(),
            'pm10': NSColor.blueColor(),
            'o3': NSColor.orangeColor(),
            'uvi': NSColor.purpleColor()
        }
        self.metrics = ['uvi', 'o3', 'pm10', 'pm25']
        self.headerHeight = 140
        self.chartPadding = 40
        self.aqi_levels = [
            (0, 50, "Good", NSColor.greenColor()),
            (51, 100, "Moderate", NSColor.yellowColor()),
            (101, 150, "Unhealthy for Sensitive Groups", NSColor.orangeColor()),
            (151, 200, "Unhealthy", NSColor.redColor()),
            (201, 300, "Very Unhealthy", NSColor.purpleColor()),
            (301, 500, "Hazardous", NSColor.darkGrayColor())
        ]

    def drawRect_(self, dirtyRect):
        NSColor.windowBackgroundColor().setFill()
        NSBezierPath.fillRect_(dirtyRect)
        
        chartsRect = NSMakeRect(0, 0, self.bounds().size.width, self.bounds().size.height - self.headerHeight)
        NSBezierPath.fillRect_(chartsRect)
        
        self.drawHeader()
        self.drawCharts()

    @objc.python_method
    def drawHeader(self):
        headerRect = NSMakeRect(0, self.bounds().size.height - self.headerHeight, self.bounds().size.width, self.headerHeight)
        
        # Draw city name (moved down)
        cityName = self.data['city']['name']
        cityAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(18),
            NSForegroundColorAttributeName: NSColor.blackColor(),
        }
        cityRect = NSMakeRect(10, headerRect.origin.y + 80, headerRect.size.width - 20, 30)
        NSString.stringWithString_(cityName).drawInRect_withAttributes_(cityRect, cityAttrs)
        
        # Draw AQI box
        aqi = self.data['aqi']
        aqi_color, aqi_text = self.get_aqi_info(aqi)
        
        aqiBoxRect = NSMakeRect(10, headerRect.origin.y + 10, 80, 60)
        aqi_color.setFill()
        NSBezierPath.fillRect_(aqiBoxRect)
        
        aqiAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(32),
            NSForegroundColorAttributeName: NSColor.whiteColor(),
        }
        aqiTextRect = NSMakeRect(aqiBoxRect.origin.x, aqiBoxRect.origin.y + 15, aqiBoxRect.size.width, 30)
        paragraph = NSMutableParagraphStyle.alloc().init()
        paragraph.setAlignment_(NSTextAlignmentCenter)
        aqiAttrs[NSParagraphStyleAttributeName] = paragraph
        NSString.stringWithString_(str(aqi)).drawInRect_withAttributes_(aqiTextRect, aqiAttrs)
        
        # Draw qualitative text
        qualTextRect = NSMakeRect(100, headerRect.origin.y + 30, headerRect.size.width - 110, 30)
        qualAttrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(20),
            NSForegroundColorAttributeName: aqi_color,
        }
        NSString.stringWithString_(aqi_text).drawInRect_withAttributes_(qualTextRect, qualAttrs)
        
        # Draw last updated time
        lastUpdate = self.data['time']['s']
        updateAttrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(12),
            NSForegroundColorAttributeName: NSColor.grayColor(),
        }
        updateRect = NSMakeRect(100, headerRect.origin.y + 10, headerRect.size.width - 110, 20)
        NSString.stringWithString_(f"Updated: {lastUpdate}").drawInRect_withAttributes_(updateRect, updateAttrs)

    @objc.python_method
    def get_aqi_info(self, aqi):
        for low, high, text, color in self.aqi_levels:
            if low <= aqi <= high:
                return color, text
        return NSColor.blackColor(), "Unknown"

    @objc.python_method
    def drawCharts(self):
        availableHeight = self.bounds().size.height - self.headerHeight
        chart_height = (availableHeight / len(self.metrics)) - self.chartPadding
        chart_width = self.bounds().size.width - 2 * self.chartPadding
        
        for i, metric in enumerate(self.metrics):
            y_position = i * (chart_height + self.chartPadding)
            self.drawChart(metric, NSMakeRect(self.chartPadding, y_position, chart_width, chart_height))




    @objc.python_method
    def drawChart(self, metric, rect):
        forecast_data = self.data['forecast']['daily'].get(metric, [])
        if not forecast_data:
            self.drawNoDataAvailable(metric, rect)
            return

        # Draw bars
        bar_width = (rect.size.width - 100) / len(forecast_data)  # Leave space for labels
        max_height = rect.size.height - 40
        max_value = max(point['max'] for point in forecast_data)
        min_value = min(point['min'] for point in forecast_data)
        value_range = max_value - min_value

        for i, point in enumerate(forecast_data):
            x = 80 + i * bar_width
            height_max = max_height * ((point['max'] - min_value) / value_range) if value_range else 0
            height_min = max_height * ((point['min'] - min_value) / value_range) if value_range else 0
            height_avg = max_height * ((point['avg'] - min_value) / value_range) if value_range else 0
            
            # Draw min-max range
            range_rect = NSMakeRect(x, rect.origin.y + 20 + height_min, bar_width - 1, height_max - height_min)
            NSColor.lightGrayColor().setFill()
            NSBezierPath.fillRect_(range_rect)
            
            # Draw average
            avg_rect = NSMakeRect(x, rect.origin.y + 20 + height_avg, bar_width - 1, 2)
            self.barColors[metric].setFill()
            NSBezierPath.fillRect_(avg_rect)

        # Draw labels
        attrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(12),
            NSForegroundColorAttributeName: self.textColor
        }
        
        # Metric name and current value
        current_value = self.data.get('iaqi', {}).get(metric, {}).get('v', 'N/A')
        metric_label = f"{metric.upper()}: Current {current_value}"
        NSString.stringWithString_(metric_label).drawAtPoint_withAttributes_(
            NSMakePoint(5, rect.origin.y + rect.size.height - 20), attrs)
        
        # Y-axis labels
        y_attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(10),
            NSForegroundColorAttributeName: self.textColor
        }
        max_label = NSString.stringWithString_(f"{max_value:.1f}")
        max_label.drawAtPoint_withAttributes_(NSMakePoint(5, rect.origin.y + rect.size.height - 35), y_attrs)

        min_label = NSString.stringWithString_(f"{min_value:.1f}")
        min_label.drawAtPoint_withAttributes_(NSMakePoint(5, rect.origin.y + 15), y_attrs)

        # X-axis labels (dates)
        date_attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(10),
            NSForegroundColorAttributeName: self.textColor
        }
        for i, point in enumerate(forecast_data):
            if i % 2 == 0:  # Draw every other date to avoid crowding
                x = 80 + i * bar_width
                date = datetime.strptime(point['day'], "%Y-%m-%d").strftime("%m-%d")
                label = NSString.stringWithString_(date)
                label.drawAtPoint_withAttributes_(NSMakePoint(x, rect.origin.y + 5), date_attrs)

    @objc.python_method
    def drawNoDataAvailable(self, metric, rect):
        attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(12),
            NSForegroundColorAttributeName: self.textColor
        }
        message = f"{metric.upper()}: No forecast data available"
        NSString.stringWithString_(message).drawAtPoint_withAttributes_(
            NSMakePoint(rect.size.width / 2 - 100, rect.origin.y + rect.size.height / 2), attrs)