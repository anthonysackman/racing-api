# Baseball API Documentation

## Overview

The Baseball API provides real-time access to Major League Baseball (MLB) data through the official MLB Stats API. This API is designed to serve data to ESP32-powered 64x64 pixel matrix displays, providing formatted information optimized for small screens.

**NEW: Multi-Device Support** - The API now supports multiple independent devices, each with their own configuration. Each device must identify itself using the `X-Device-ID` header.

## Base URL

```
https://racing-api-fr6v.onrender.com/baseball
```

## Device Identification

All API requests must include a `X-Device-ID` header to identify which device is making the request. This allows each device to have its own independent configuration.

### Header Format
```
X-Device-ID: {device_id}
```

### Example
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/config
```

### Device IDs
- **Human-readable format**: Use descriptive names like `baseball_1`, `office_display`, `living_room_panel`
- **Fallback**: If no header is provided, the API defaults to `baseball_1`
- **Registration**: New devices are automatically registered when they first make a request

## Supported Teams

The API supports all 30 MLB teams. Team names can be provided in various formats (full name, nickname, or abbreviation):

| Team ID | Team Name | Alternative Names |
|---------|-----------|------------------|
| 108 | Angels | Los Angeles Angels, LAA |
| 109 | D-backs | Arizona Diamondbacks, ARI |
| 110 | Orioles | Baltimore Orioles, BAL |
| 111 | Red Sox | Boston Red Sox, BOS |
| 112 | Cubs | Chicago Cubs, CHC |
| 113 | Reds | Cincinnati Reds, CIN |
| 114 | Guardians | Cleveland Guardians, CLE |
| 115 | Rockies | Colorado Rockies, COL |
| 116 | Tigers | Detroit Tigers, DET |
| 117 | Astros | Houston Astros, HOU |
| 118 | Royals | Kansas City Royals, KC |
| 119 | Dodgers | Los Angeles Dodgers, LAD |
| 120 | Nationals | Washington Nationals, WAS |
| 121 | Mets | New York Mets, NYM |
| 133 | Athletics | Oakland Athletics, OAK |
| 134 | Pirates | Pittsburgh Pirates, PIT |
| 135 | Padres | San Diego Padres, SD |
| 136 | Mariners | Seattle Mariners, SEA |
| 137 | Giants | San Francisco Giants, SF |
| 138 | Cardinals | St. Louis Cardinals, STL |
| 139 | Rays | Tampa Bay Rays, TB |
| 140 | Rangers | Texas Rangers, TEX |
| 141 | Blue Jays | Toronto Blue Jays, TOR |
| 142 | Twins | Minnesota Twins, MIN |
| 143 | Phillies | Philadelphia Phillies, PHI |
| 144 | Braves | Atlanta Braves, ATL |
| 145 | White Sox | Chicago White Sox, CWS |
| 146 | Marlins | Miami Marlins, MIA |
| 147 | Yankees | New York Yankees, NYY |
| 158 | Brewers | Milwaukee Brewers, MIL |

## Endpoints

### 1. Get Last Completed Game

**Endpoint:** `GET /baseball/last/{team_name}`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Retrieves the most recent completed game for the specified team.

**Parameters:**
- `team_name` (path parameter, string): Name of the MLB team

**Response Format:**

#### Success Response (200 OK)
```json
{
  "gamePk": 775296,
  "gameGuid": "920f8c2c-a626-4716-9ffb-89b3059e2dfe",
  "link": "/api/v1.1/game/775296/feed/live",
  "gameType": "W",
  "season": "2024",
  "gameDate": "2024-10-31T00:08:00Z",
  "officialDate": "2024-10-30",
  "status": "auto",
  "teams": {
    "away": {
      "leagueRecord": {
        "wins": 4,
        "losses": 1,
        "pct": ".800"
      },
      "score": 7,
      "team": {
        "id": 119,
        "name": "Los Angeles Dodgers",
        "link": "/api/v1/teams/119"
      },
      "isWinner": true,
      "splitSquad": false,
      "seriesNumber": 1
    },
    "home": {
      "leagueRecord": {
        "wins": 1,
        "losses": 4,
        "pct": ".200"
      },
      "score": 6,
      "team": {
        "id": 147,
        "name": "New York Yankees",
        "link": "/api/v1/teams/147"
      },
      "isWinner": false,
      "splitSquad": false,
      "seriesNumber": 1
    }
  },
  "venue": {
    "id": 3313,
    "name": "Yankee Stadium",
    "link": "/api/v1/venues/3313"
  },
  "content": {
    "link": "/api/v1/game/775296/content"
  },
  "isTie": false,
  "gameNumber": 1,
  "publicFacing": true,
  "doubleHeader": "N",
  "gamedayType": "P",
  "tiebreaker": "N",
  "calendarEventID": "14-775296-2024-10-30",
  "seasonDisplay": "2024",
  "dayNight": "night",
  "description": "World Series Game 5",
  "scheduledInnings": 9,
  "reverseHomeAwayStatus": false,
  "inningBreakLength": 120,
  "gamesInSeries": 7,
  "seriesGameNumber": 5,
  "seriesDescription": "World Series",
  "recordSource": "S",
  "ifNecessary": "N",
  "ifNecessaryDescription": "Normal Game"
}
```

#### Error Responses

**404 Not Found - Team Not Found**
```json
{
  "error": "Team not found",
  "status": "auto"
}
```

**404 Not Found - No Completed Game**
```json
{
  "error": "No completed game found",
  "status": "auto"
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/last/Dodgers
```

---

### 2. Get Next Scheduled Game

**Endpoint:** `GET /baseball/next/{team_name}`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Retrieves the next scheduled game for the specified team.

**Parameters:**
- `team_name` (path parameter, string): Name of the MLB team

**Response Format:**

#### Success Response (200 OK)
```json
{
  "gamePk": 776941,
  "gameGuid": "afec0e76-f3dc-4d19-aec9-d881a3353317",
  "link": "/api/v1.1/game/776941/feed/live",
  "gameType": "R",
  "season": "2025",
  "gameDate": "2025-07-30T23:10:00Z",
  "officialDate": "2025-07-30",
  "status": "auto",
  "teams": {
    "away": {
      "leagueRecord": {
        "wins": 62,
        "losses": 45,
        "pct": ".579"
      },
      "team": {
        "id": 119,
        "name": "Los Angeles Dodgers",
        "link": "/api/v1/teams/119"
      },
      "splitSquad": false,
      "seriesNumber": 36
    },
    "home": {
      "leagueRecord": {
        "wins": 56,
        "losses": 51,
        "pct": ".523"
      },
      "team": {
        "id": 113,
        "name": "Cincinnati Reds",
        "link": "/api/v1/teams/113"
      },
      "splitSquad": false,
      "seriesNumber": 35
    }
  },
  "venue": {
    "id": 2602,
    "name": "Great American Ball Park",
    "link": "/api/v1/venues/2602"
  },
  "content": {
    "link": "/api/v1/game/776941/content"
  },
  "gameNumber": 1,
  "publicFacing": true,
  "doubleHeader": "N",
  "gamedayType": "P",
  "tiebreaker": "N",
  "calendarEventID": "14-776941-2025-07-30",
  "seasonDisplay": "2025",
  "dayNight": "night",
  "scheduledInnings": 9,
  "reverseHomeAwayStatus": false,
  "inningBreakLength": 120,
  "gamesInSeries": 3,
  "seriesGameNumber": 3,
  "seriesDescription": "Regular Season",
  "recordSource": "S",
  "ifNecessary": "N",
  "ifNecessaryDescription": "Normal Game"
}
```

#### Error Responses

**404 Not Found - Team Not Found**
```json
{
  "error": "Team not found",
  "status": "auto"
}
```

**404 Not Found - No Upcoming Game**
```json
{
  "error": "No upcoming game found",
  "status": "auto"
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/next/Dodgers
```

---

### 3. Get Live Game

**Endpoint:** `GET /baseball/live/{team_name}`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Retrieves the current live game for the specified team (if one is in progress).

**Parameters:**
- `team_name` (path parameter, string): Name of the MLB team

**Response Format:**

#### Success Response (200 OK)
Returns the same structure as the last/next game endpoints when a live game is found.

#### Error Responses

**404 Not Found - Team Not Found**
```json
{
  "error": "Team not found",
  "status": "auto"
}
```

**404 Not Found - No Live Game**
```json
{
  "error": "No live game found",
  "status": "auto"
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/live/Dodgers
```

---

### 4. Get Live Game Details

**Endpoint:** `GET /baseball/live/details/{team_name}`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Retrieves detailed live game information including current batter, pitcher, pitch data, and strike zone mapping optimized for matrix displays.

**Parameters:**
- `team_name` (path parameter, string): Name of the MLB team

**Response Format:**

#### Success Response (200 OK)
```json
{
  "batter": "Mookie Betts",
  "batting_avg": ".312",
  "colors": {
    "home": [0, 0, 15],
    "away": [0, 6, 15]
  },
  "count": {
    "balls": 2,
    "strikes": 1,
    "outs": 1
  },
  "inning": {
    "half": "Top",
    "number": 3
  },
  "matrix_location": {
    "x": 5,
    "y": 8
  },
  "outcome": "Called Strk",
  "pitch_speed": "94.2",
  "pitch_type": "4-Seam Fastb",
  "pitcher": "Max Scherzer",
  "score": {
    "Dodgers": 3,
    "Nationals": 2
  },
  "teams": {
    "home": "Nationals",
    "away": "Dodgers"
  },
  "todays_line": "2-for-3, single",
  "raw_pitch_type": "Four-Seam Fastball",
  "raw_outcome": "Called Strike",
  "zone_top": 3.5,
  "zone_bottom": 1.5,
  "px": 0.2,
  "pz": 2.8,
  "status": "auto"
}
```

#### Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `batter` | string | Current batter's full name |
| `batting_avg` | string | Batter's current season batting average |
| `colors` | object | Team colors for matrix display (RGB values) |
| `count` | object | Current count (balls, strikes, outs) |
| `inning` | object | Current inning information |
| `matrix_location` | object | Strike zone coordinates mapped to matrix display |
| `outcome` | string | Result of the last pitch (shortened for display) |
| `pitch_speed` | string | Speed of the last pitch in mph |
| `pitch_type` | string | Type of the last pitch (shortened for display) |
| `pitcher` | string | Current pitcher's full name |
| `score` | object | Current score for both teams |
| `teams` | object | Team names (home/away) |
| `todays_line` | string | Batter's performance today (e.g., "2-for-3, single") |
| `raw_pitch_type` | string | Full pitch type description |
| `raw_outcome` | string | Full pitch outcome description |
| `zone_top` | number | Top of strike zone in feet |
| `zone_bottom` | number | Bottom of strike zone in feet |
| `px` | number | Horizontal pitch location in feet |
| `pz` | number | Vertical pitch location in feet |

#### Pitch Type Mappings

| Full Description | Display Version |
|------------------|-----------------|
| Changeup | Changeup |
| Curveball | Curve |
| Cutter | Cutter |
| Eephus | Eephus |
| Fastball | Fastball |
| Forkball | Forkball |
| Four-Seam Fastball | 4-Seam Fastb |
| Knuckle Curve | Knuck Curve |
| Sinker | Sinker |
| Slider | Slider |
| Slow Curve | Slow Curve |
| Slurve | Slurve |
| Splitter | Splitter |
| Sweeper | Sweeper |

#### Pitch Outcome Mappings

| Full Description | Display Version |
|------------------|-----------------|
| Ball | Ball |
| Ball In Dirt | Ball (Dirt) |
| Called Strike | Called Strk |
| Foul | Foul |
| Foul Bunt | Foul Bunt |
| Foul Tip | Foul Tip |
| Hit By Pitch | HBP |
| In play, no out | In Play - No |
| In play, out(s) | In Play - Out |
| In play, run(s) | In Play - Run |
| Missed Bunt | Miss Bunt |
| Pitchout | Pitchout |
| Swinging Strike | Swing Strk |
| Swinging Strike (Blocked) | Sw Strk (Blk) |

#### Error Responses

**404 Not Found - Team Not Found**
```json
{
  "error": "Team not found",
  "status": "auto"
}
```

**404 Not Found - No Live Game**
```json
{
  "error": "No live game found",
  "status": "auto"
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/live/details/Dodgers
```

---

## Configuration Endpoints

### 5. Get Current Status

**Endpoint:** `GET /status`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Returns the current display mode for the specified device.

**Response Format:**
```json
{
  "mode": "auto",
  "status": "auto"
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/status
```

---

### 6. Get Device Configuration

**Endpoint:** `GET /config`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Returns the complete configuration for the specified device including display mode, timing settings, and panel configurations.

**Response Format:**
```json
{
  "mode": "auto",
  "live_content_timeout": 120000,
  "rotation_interval": 15000,
  "sub_panel_duration_offset": 5000,
  "panels": {
    "baseball": {
      "enabled": true,
      "duration": 30000,
      "priority": "live"
    },
    "nascar": {
      "enabled": true,
      "duration": 45000,
      "priority": "live"
    },
    "dashboard": {
      "enabled": true,
      "duration": 15000,
      "priority": "static"
    }
  }
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/config
```

---

### 7. Get Panel Status

**Endpoint:** `GET /status/panels`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Returns real-time status of all display panels for the specified device.

**Response Format:**
```json
{
  "baseball": {
    "has_live_content": true,
    "last_update": "2024-01-15T10:30:00Z",
    "status": "active",
    "current_sub_panel": "live_game"
  },
  "nascar": {
    "has_live_content": true,
    "last_update": "2024-01-15T10:30:00Z",
    "status": "active",
    "current_sub_panel": "cup_races"
  },
  "dashboard": {
    "has_live_content": false,
    "last_update": "2024-01-15T10:30:00Z",
    "status": "active",
    "current_sub_panel": "system_status"
  }
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/status/panels
```

---

### 8. Get System Status

**Endpoint:** `GET /status/system`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Returns system health and performance metrics.

**Response Format:**
```json
{
  "api_status": "healthy",
  "last_config_fetch": "2024-01-15T10:30:00Z",
  "active_mode": "auto",
  "current_panel": "baseball",
  "uptime_seconds": 86400,
  "memory_usage_percent": 45.2,
  "wifi_signal_strength": -65,
  "api_response_time_ms": 250
}
```

**Example Request:**
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/status/system
```

---

### 9. Save Device Configuration

**Endpoint:** `POST /save_config`

**Headers Required:**
- `X-Device-ID`: Device identifier

**Description:** Updates the configuration for the specified device. This endpoint is typically used by the web interface.

**Request Format:**
Form data with the following fields:
- `mode`: Display mode (auto, baseball, nascar, dashboard, demo, manual)
- `live_content_timeout`: Timeout for live content in seconds
- `rotation_interval`: Panel rotation interval in seconds
- `sub_panel_duration_offset`: Sub-panel duration offset in seconds
- `panels.{panel_name}.enabled`: Whether panel is enabled
- `panels.{panel_name}.duration`: Panel duration in seconds
- `panels.{panel_name}.priority`: Panel priority (live/static)

**Response:** Redirects to the web interface with success/error status.

**Example Request:**
```bash
curl -X POST -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/save_config \
  -d "mode=baseball" \
  -d "live_content_timeout=120" \
  -d "rotation_interval=15" \
  -d "sub_panel_duration_offset=5" \
  -d "panels.baseball.enabled=true" \
  -d "panels.baseball.duration=30" \
  -d "panels.baseball.priority=live"
```

## Device Management

### Device Registration
- **Automatic**: Devices are automatically registered when they first make a request
- **Device ID Format**: Use human-readable names like `baseball_1`, `office_display`, `living_room_panel`
- **Fallback**: If no `X-Device-ID` header is provided, the API defaults to `baseball_1`

### Multiple Device Support
- Each device has its own independent configuration
- No shared state between devices
- Each device can have different display modes, timing settings, and panel configurations

## Status Injection

All JSON responses automatically include a `status` field indicating the current display mode for the specified device. This is injected by middleware and helps the matrix display know which sport mode is active.

## Error Handling

The API implements comprehensive error handling:

1. **Team Not Found**: Returns 404 when the team name cannot be resolved
2. **No Data Available**: Returns 404 with appropriate error message when no relevant data is found
3. **External API Failures**: Gracefully handles MLB API failures
4. **Invalid Parameters**: Validates input parameters and returns appropriate errors
5. **Device Not Found**: Falls back to default device if unknown device ID is provided

## Rate Limiting

Currently, the API does not implement rate limiting. Consider implementing rate limiting for production use.

## Data Sources

- **MLB Stats API**: Official MLB statistics API (https://statsapi.mlb.com/api/v1)
- **Live Game Feed**: Real-time game data for live games
- **Player Statistics**: Individual player performance data

## Matrix Display Integration

The API is specifically designed for ESP32-powered 64x64 pixel matrix displays:

- **Formatted Data**: All text is shortened for small screens
- **Color Information**: Team colors provided as RGB values
- **Strike Zone Mapping**: Pitch locations mapped to matrix coordinates
- **Real-time Updates**: Live data optimized for frequent polling
- **Multi-Device Support**: Each device can have independent configurations

## Usage Examples

### Get Last Game for Dodgers
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/last/Dodgers
```

### Get Next Game for Yankees
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/next/Yankees
```

### Get Live Game for Red Sox
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/live/Red%20Sox
```

### Get Live Game Details for Astros
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/baseball/live/details/Astros
```

### Get Current Status
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/status
```

### Get Device Configuration
```bash
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/config
```

### Multiple Devices Example
```bash
# Device 1
curl -H "X-Device-ID: baseball_1" https://racing-api-fr6v.onrender.com/config

# Device 2  
curl -H "X-Device-ID: office_display" https://racing-api-fr6v.onrender.com/config

# Device 3
curl -H "X-Device-ID: living_room_panel" https://racing-api-fr6v.onrender.com/config
```

## Notes

- Team names are case-insensitive and support various formats
- Live game data is only available during active games
- Strike zone mapping is optimized for 64x64 matrix displays
- All timestamps are in UTC format
- Team colors are provided as RGB tuples for matrix display compatibility
- Configuration can be managed through the web interface at the root URL
- **NEW**: Each device must include the `X-Device-ID` header in all requests
- **NEW**: Devices are automatically registered on first request
- **NEW**: Each device has independent configuration and status 