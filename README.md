# AQIDisplay

A native macOS menu bar application for real-time air quality monitoring, developed as part of my coursework.

[Download Pre-built App (MacOS arm64](https://website-ripl.onrender.com/downloads/AQIDisplay.zip)

![Screenshot 2024-10-24 at 7 57 52 PM](https://github.com/user-attachments/assets/1480b648-f9c1-4c6b-8dbf-dcbb362f96cf)



## Project Overview

AQIDisplay is a macOS application that lives in your menu bar and provides real-time air quality information. The project demonstrates practical application of:

- Native macOS development using PyObjC
- Real-time data visualization
- API integration (WAQI - World Air Quality Index)
- Local data persistence with SQLite
- System integration features

## Core Components

### Menu Bar Application (`app.py`)
- Main application entry point
- Manages menu bar interface and updates
- Handles API communication with WAQI
- Implements SQLite database operations for historical data

### Data Visualization (`aqi_visualization_view.py`)
- Custom visualization system for air quality metrics
- 24-hour historical data charts
- Dynamic color coding based on AQI levels
- Temperature unit conversion support

### Detail Window (`detail_window.py`)
- Comprehensive view of air quality metrics
- Historical data visualization
- System preferences management

### Search Window (`search_city_window.py`)
- Location search functionality
- Table view for search results
- City selection and data updates

### System Integration (`login_item_manager.py`)
- macOS login item management
- System preferences integration
- Launch-at-login functionality

## Technical Implementation

### Data Storage
- SQLite database for historical data
- 24-hour data retention
- Hourly data point storage
- Automatic database cleanup

### UI Components
- Native macOS window management
- Custom NSView implementations
- Dynamic chart rendering
- Real-time updates

### System Integration
- Menu bar presence
- Native notifications
- System preferences integration
- Launch-at-login capability

## Project Structure
```
AQIDisplay/
├── app.py                     # Main application
├── aqi_visualization_view.py  # Data visualization
├── detail_window.py          # Detailed view window
├── login_item_manager.py     # System integration
├── search_city_window.py     # Location search
└── setup.py                  # Build configuration
```

## Key Features

### Air Quality Metrics
- Real-time AQI monitoring
- PM2.5 and PM10 levels
- O₃, NO₂, SO₂, CO concentrations
- Temperature and humidity
- Wind speed and pressure

### Data Display
- Menu bar quick view
- Detailed historical charts
- Color-coded indicators
- Customizable metrics

### System Features

- Local data persistence
- Automatic updates
- Location search

## Dependencies

The project uses several key libraries and frameworks:
- PyObjC for macOS integration
- rumps for menu bar functionality
- requests for API communication
- SQLite3 for data storage

## TODO

### Core Features
- [ ] Fix 'Search City'
- [ ] Implement 'About'
- [ ] Implement Start at Login
