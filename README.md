# Sports Matrix Display Backend API

A comprehensive backend API service designed to provide real-time sports data for 64x64 pixel matrix displays. This service aggregates data from multiple sports sources and provides a unified interface for displaying live sports information.

## 🏗️ Project Overview

This backend serves as the data layer for ESP32-powered matrix displays, providing real-time sports data for NASCAR and MLB (Major League Baseball). The system supports multiple display modes and can switch between different sports or show all data simultaneously.

### Key Features

- **Multi-Sport Support**: NASCAR and MLB data integration
- **Real-Time Data**: Live race/game information with current standings
- **Display Mode Management**: Switch between sports or show all data
- **RESTful API**: Clean, JSON-based API endpoints
- **Status Injection**: Automatic status information in all responses
- **Web Interface**: Simple HTML interface for mode management

## 🚀 Technology Stack

- **Framework**: Sanic (Async Python web framework)
- **Python Version**: 3.10+
- **Dependencies**: 
  - `sanic>=25.3.0` - Web framework
  - `requests>=2.32.3` - HTTP client
  - `pytz>=2025.2` - Timezone handling
  - `aiofiles==24.1.0` - Async file operations

## 📁 Project Structure

```
nascarapi/
├── app/
│   ├── server.py              # Main Sanic application
│   ├── constants.py           # Application constants and enums
│   ├── routes.py              # Main routes and web interface
│   ├── requirements.txt       # App-specific dependencies
│   ├── data/                  # Data storage
│   │   ├── display_status.json
│   │   └── schedule.json
│   ├── html_dumps/           # HTML templates for data
│   │   ├── cup.html
│   │   ├── truck.html
│   │   └── xfinity.html
│   ├── nascar/               # NASCAR-specific modules
│   │   ├── routes.py         # NASCAR API endpoints
│   │   ├── live_data.py      # Live race data fetching
│   │   ├── schedule.py       # Race schedule management
│   │   ├── standings.py      # Driver standings
│   │   └── storage.py        # Data storage utilities
│   └── baseball/             # MLB-specific modules
│       ├── routes.py         # Baseball API endpoints
│       └── baseball_api.py   # MLB data integration
├── data/                     # Global data storage
├── requirements.txt          # Project dependencies
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

## 🏁 NASCAR Integration

### Data Sources
- **Live Race Data**: NASCAR.com live feed API
- **Schedule Data**: Race schedules for all series
- **Standings**: Driver standings and race results

### NASCAR Series IDs
- **1**: Cup Series
- **2**: Xfinity Series  
- **3**: Truck Series

### Key Features
- Real-time race position tracking
- Top 3 drivers with detailed stats
- Race schedule management
- Historical race results
- Driver standings

### NASCAR API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/nascar/race/<series_id>` | GET | Get upcoming race for series |
| `/nascar/race/live` | GET | Get current live race data |
| `/nascar/race/last/<series_id>` | GET | Get last completed race |
| `/nascar/standings/<series_id>` | GET | Get driver standings |

### Live Race Data Format
```json
{
  "time_of_day_os_formatted": "March 15, 2:30 PM",
  "vehicles": [
    {
      "driver_name": "Kyle Larson",
      "short_display_name": "K, Larson",
      "position": 1,
      "laps_completed": 45,
      "last_lap_time": "32.456",
      "last_lap_speed": "185.234",
      "vehicle_number": "5"
    }
  ]
}
```

## ⚾ MLB Integration

### Data Sources
- **MLB Stats API**: Official MLB statistics API
- **Live Game Data**: Real-time game feeds
- **Team Information**: Comprehensive team data

### Supported Teams
All 30 MLB teams with team colors and identifiers:
- Angels, D-backs, Orioles, Red Sox, Cubs, Reds, Guardians, Rockies, Tigers, Astros, Royals, Dodgers, Nationals, Mets, Athletics, Pirates, Padres, Mariners, Giants, Cardinals, Rays, Rangers, Blue Jays, Twins, Phillies, Braves, White Sox, Marlins, Yankees, Brewers

### MLB API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/baseball/last/<team_name>` | GET | Get last completed game |
| `/baseball/next/<team_name>` | GET | Get next scheduled game |
| `/baseball/live/<team_name>` | GET | Get current live game |
| `/baseball/live/details/<team_name>` | GET | Get detailed live game data |

### Live Game Data Features
- Current game state (inning, score, count)
- Batter and pitcher information
- Pitch-by-pitch data
- Player statistics
- Strike zone mapping

## 🎛️ Display Mode Management

### Available Modes
- **ALL**: Display data from all sports
- **BASEBALL**: Show only MLB data
- **NASCAR**: Show only NASCAR data

### Mode Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface for mode selection |
| `/set_mode` | POST | Set display mode |
| `/status` | GET | Get current display status |

### Status Injection
All JSON responses automatically include a `status` field with the current display mode:
```json
{
  "data": "...",
  "status": "baseball"
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- `uv` package manager (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nascarapi
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Run the server**
   ```bash
   python -m app.server
   ```

### Configuration

The application uses several configuration files:

- **`app/data/display_status.json`**: Current display mode
- **`app/data/schedule.json`**: Cached schedule data
- **`app/constants.py`**: Application constants

## 🔧 Development

### Project Structure Overview

#### Core Application (`app/`)
- **`server.py`**: Main Sanic application with middleware
- **`constants.py`**: Enums and configuration constants
- **`routes.py`**: Main routes and web interface

#### NASCAR Module (`app/nascar/`)
- **`live_data.py`**: Real-time race data fetching and formatting
- **`schedule.py`**: Race schedule management and caching
- **`standings.py`**: Driver standings and race results
- **`routes.py`**: NASCAR-specific API endpoints

#### Baseball Module (`app/baseball/`)
- **`baseball_api.py`**: MLB API integration and data processing
- **`routes.py`**: Baseball-specific API endpoints

### Key Components

#### Middleware
The application includes response middleware that automatically injects the current display status into all JSON responses.

#### Data Caching
- Schedule data is cached locally to reduce API calls
- HTML templates are stored for quick access
- Status information is persisted between restarts

#### Error Handling
- Comprehensive error handling for API failures
- Graceful degradation when external services are unavailable
- Detailed logging for debugging

## 🔌 API Usage Examples

### Get Live NASCAR Race
```bash
curl http://localhost:8000/nascar/race/live
```

### Get Next Baseball Game
```bash
curl http://localhost:8000/baseball/next/Dodgers
```

### Set Display Mode
```bash
curl -X POST http://localhost:8000/set_mode \
  -d "mode=baseball"
```

### Get Current Status
```bash
curl http://localhost:8000/status
```

## 🎯 Matrix Display Integration

This backend is designed to work with ESP32-powered 64x64 pixel matrix displays. The API provides:

- **Formatted Data**: Optimized for small display screens
- **Real-time Updates**: Live data for current events
- **Mode Switching**: Easy switching between sports
- **Status Information**: Display mode included in all responses

### Data Format Considerations
- Driver names are shortened for display (e.g., "K, Larson")
- Time formats are optimized for matrix displays
- Scores and statistics are formatted for readability
- Team colors are provided for visual enhancement

## 🔮 Future Enhancements

### Planned Features
- **Additional Sports**: NBA, NFL, NHL integration
- **Weather Data**: Local weather conditions
- **Custom Displays**: User-defined display layouts
- **WebSocket Support**: Real-time data streaming
- **Authentication**: API key management
- **Rate Limiting**: API usage controls

### Technical Improvements
- **Database Integration**: Persistent data storage
- **Caching Layer**: Redis for improved performance
- **Monitoring**: Health checks and metrics
- **Documentation**: OpenAPI/Swagger documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the existing documentation
2. Review the API endpoints
3. Check the logs for error messages
4. Create an issue with detailed information

---

**Note**: This backend is designed to work with the ESP32 matrix display project located at `C:\Users\Mvp-T\Documents\PlatformIO\Projects\Matrix\src`.
