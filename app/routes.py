from sanic import Blueprint, response, Request
import json
import time
import psutil
from datetime import datetime
from .config_manager import config_manager
from .constants import DisplayMode, PanelPriority, PanelStatus, ApiStatus

index_bp = Blueprint("index", url_prefix="/")


@index_bp.get("/")
async def index(request: Request):
    """Main configuration interface"""
    # Get device ID from query param or default to baseball_1
    device_id = request.args.get("device", "baseball_1")

    # Get all devices for the selector
    all_devices = config_manager.get_all_devices()

    # Get config for selected device
    config = config_manager.get_device_config(device_id)

    # Generate device selector options
    device_options = "\n".join(
        f'<option value="{dev_id}"{" selected" if dev_id == device_id else ""}>{dev_id}</option>'
        for dev_id in all_devices.keys()
    )

    # Generate mode options based on device
    if device_id == "baseball_1":
        # baseball_1 only gets auto and manual modes
        mode_options = "\n".join(
            [
                f'<option value="auto"{" selected" if config.get("mode", "auto") == "auto" else ""}>Auto</option>',
                f'<option value="manual"{" selected" if config.get("mode", "auto") == "manual" else ""}>Manual</option>',
            ]
        )
    else:
        # Other devices get all modes including demo
        mode_options = "\n".join(
            f'<option value="{mode.value}"{" selected" if mode.value == config.get("mode", "auto") else ""}>{mode.name.title()}</option>'
            for mode in DisplayMode
        )

    # Generate panel configurations
    panel_configs = ""
    for panel_name, panel_config in config.get("panels", {}).items():
        enabled_checked = "checked" if panel_config.get("enabled", True) else ""
        duration_value = (
            panel_config.get("duration", 30000) // 1000
        )  # Convert to seconds
        priority_options = "\n".join(
            f'<option value="{priority.value}"{" selected" if priority.value == panel_config.get("priority", "live") else ""}>{priority.name.title()}</option>'
            for priority in PanelPriority
        )

        panel_configs += f"""
        <div class="panel-config">
            <div class="panel-header">
            <h3>{panel_name.title()} Panel</h3>
                <div class="panel-status">
                    <span class="status-dot {panel_config.get("enabled", True) and "active" or "inactive"}"></span>
                    <span class="status-text">{panel_config.get("enabled", True) and "Enabled" or "Disabled"}</span>
                </div>
            </div>
            <div class="panel-controls">
                <div class="control-group">
                    <label class="checkbox-label">
                    <input type="checkbox" name="panels.{panel_name}.enabled" {enabled_checked}>
                        <span class="checkmark"></span>
                    Enabled
                </label>
            </div>
                <div class="control-group">
                <label>Duration (seconds):</label>
                <input type="number" name="panels.{panel_name}.duration" value="{duration_value}" min="5" max="300">
            </div>
                <div class="control-group">
                <label>Priority:</label>
                <select name="panels.{panel_name}.priority">
                    {priority_options}
                </select>
                </div>
            </div>
        </div>
        """

        # Timing configuration
    timing_config = {
        "live_content_timeout": config.get("live_content_timeout", 120000),
        "rotation_interval": config.get("rotation_interval", 15000),
        "sub_panel_duration_offset": config.get("sub_panel_duration_offset", 5000),
    }

    return response.html(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sports Matrix Display Configuration</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .device-selector {{
                background: #ecf0f1;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;
            }}
            
            .device-selector h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            
            .device-selector select {{
                padding: 10px 15px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                font-size: 16px;
                background: white;
                min-width: 200px;
            }}
            
            .main-grid {{
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 30px;
                margin-bottom: 30px;
            }}
            
            .status-panel {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                border-left: 4px solid #3498db;
            }}
            
            .status-panel h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.3em;
            }}
            
            .status-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 1px solid #e1e8ed;
            }}
            
            .status-item:last-child {{
                border-bottom: none;
            }}
            
            .status-label {{
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            
            .status-value {{
                font-size: 1em;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .config-panel {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                border-left: 4px solid #27ae60;
            }}
            
            .config-panel h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.3em;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .form-group input,
            .form-group select {{
                width: 100%;
                padding: 12px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }}
            
            .form-group input:focus,
            .form-group select:focus {{
                outline: none;
                border-color: #3498db;
            }}
            
            .timing-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            
            .panel-config {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #e1e8ed;
            }}
            
            .panel-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }}
            
            .panel-header h3 {{
                color: #2c3e50;
                font-size: 1.2em;
            }}
            
            .panel-status {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            .status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #27ae60;
            }}
            
            .status-dot.inactive {{
                background: #95a5a6;
            }}
            
            .status-text {{
                font-size: 0.9em;
                color: #27ae60;
                font-weight: 600;
            }}
            
            .status-dot.inactive + .status-text {{
                color: #95a5a6;
            }}
            
            .panel-controls {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .control-group {{
                display: flex;
                flex-direction: column;
            }}
            
            .control-group label {{
                margin-bottom: 5px;
                font-size: 0.9em;
                color: #2c3e50;
            }}
            
            .checkbox-label {{
                display: flex;
                align-items: center;
                cursor: pointer;
                font-size: 0.9em;
                color: #2c3e50;
            }}
            
            .checkbox-label input[type="checkbox"] {{
                display: none;
            }}
            
            .checkmark {{
                width: 18px;
                height: 18px;
                border: 2px solid #e1e8ed;
                border-radius: 3px;
                margin-right: 8px;
                position: relative;
                transition: all 0.3s;
            }}
            
            .checkbox-label input[type="checkbox"]:checked + .checkmark {{
                background: #3498db;
                border-color: #3498db;
            }}
            
            .checkbox-label input[type="checkbox"]:checked + .checkmark::after {{
                content: '✓';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
            
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                margin: 5px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                text-decoration: none;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .btn-success {{
                background: #27ae60;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #229954;
                transform: translateY(-2px);
            }}
            
            .btn-secondary {{
                background: #95a5a6;
                color: white;
            }}
            
            .btn-secondary:hover {{
                background: #7f8c8d;
                transform: translateY(-2px);
            }}
            
            .api-links {{
                margin-top: 30px;
                padding: 20px;
                background: #ecf0f1;
                border-radius: 10px;
                text-align: center;
            }}
            
            .api-links h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            
            .api-links a {{
                display: inline-block;
                margin: 5px;
                padding: 8px 16px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 14px;
            }}
            
            .api-links a:hover {{
                background: #2980b9;
            }}
            
            .nav-links {{
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .nav-links a {{
                display: inline-block;
                padding: 10px 20px;
                margin: 0 10px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
            }}
            
            .nav-links a:hover {{
                background: #2980b9;
                transform: translateY(-2px);
            }}
            
            .nav-links a.active {{
                background: #27ae60;
            }}
            
            @media (max-width: 768px) {{
                .main-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .timing-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .panel-controls {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏟️ Sports Matrix Display</h1>
                <p>Multi-Device Configuration Panel</p>
            </div>
            
            <div class="content">
                <div class="nav-links">
                    <a href="/?device={device_id}" class="active">⚙️ Configuration</a>
                    <a href="/preview?device={device_id}">📊 Data Preview</a>
                </div>
                
                <div class="device-selector">
                    <h3>📱 Select Device</h3>
                    <form method="GET" action="/">
                        <select name="device" id="device" onchange="this.form.submit()">
                            {device_options}
                        </select>
                    </form>
                </div>
                
                <div class="main-grid">
                    <div class="status-panel">
                        <h2>📊 Device Status</h2>
                    <div class="status-item">
                            <span class="status-label">Device ID</span>
                            <span class="status-value">{device_id}</span>
                    </div>
                    <div class="status-item">
                            <span class="status-label">Display Mode</span>
                            <span class="status-value">{config.get("mode", "auto").title()}</span>
                    </div>
                    <div class="status-item">
                            <span class="status-label">Rotation Interval</span>
                            <span class="status-value">{int(timing_config.get("rotation_interval", 15000)) // 1000}s</span>
                    </div>
                    <div class="status-item">
                            <span class="status-label">Live Timeout</span>
                            <span class="status-value">{int(timing_config.get("live_content_timeout", 120000)) // 1000}s</span>
                        </div>
                        <div class="status-item">
                            <span class="status-label">Sub-panel Offset</span>
                            <span class="status-value">{int(timing_config.get("sub_panel_duration_offset", 5000)) // 1000}s</span>
                    </div>
                </div>
                
                    <div class="config-panel">
                        <h2>🎛️ Configuration</h2>
                <form action="/save_config" method="POST">
                            <input type="hidden" name="device_id" value="{device_id}">
                            
                        <div class="form-group">
                            <label for="mode">Display Mode:</label>
                            <select name="mode" id="mode">
                                {mode_options}
                            </select>
                            <small style="color: #7f8c8d; margin-top: 5px; display: block;">
                                <strong>Auto:</strong> Automatically rotate between panels based on live content<br>
                                <strong>Manual:</strong> Manual control of panel selection<br>
                                <strong>Demo:</strong> Demo mode for testing
                            </small>
                    </div>
                    
                            <div class="form-group">
                                <label>Timing Configuration:</label>
                                <div class="timing-grid">
                                    <div>
                                <label>Live Content Timeout (seconds):</label>
                                <input type="number" name="live_content_timeout" 
                                               value="{timing_config.get("live_content_timeout", 120000) // 1000}" 
                                       min="30" max="600" step="30">
                            </div>
                                    <div>
                                <label>Rotation Interval (seconds):</label>
                                <input type="number" name="rotation_interval" 
                                               value="{timing_config.get("rotation_interval", 15000) // 1000}" 
                                       min="5" max="120" step="5">
                            </div>
                                    <div>
                                <label>Sub-panel Duration Offset (seconds):</label>
                                <input type="number" name="sub_panel_duration_offset" 
                                               value="{timing_config.get("sub_panel_duration_offset", 5000) // 1000}" 
                                       min="1" max="30" step="1">
                            </div>
                        </div>
                    </div>
                    
                            <div class="form-group">
                                <label>Panel Configuration:</label>
                        {panel_configs}
                    </div>
                    
                            <div style="text-align: center; margin-top: 20px;">
                        <button type="submit" class="btn btn-success">💾 Save Configuration</button>
                    </div>
                </form>
                    </div>
                </div>
                
                <div class="api-links">
                    <h3>🔗 API Endpoints</h3>
                    <a href="/config?device={device_id}" target="_blank">GET /config</a>
                    <a href="/status/panels?device={device_id}" target="_blank">GET /status/panels</a>
                    <a href="/status/system?device={device_id}" target="_blank">GET /status/system</a>
                    <a href="/status?device={device_id}" target="_blank">GET /status</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


def get_device_id(request: Request) -> str:
    return request.headers.get("x-device-id", "baseball_1")


@index_bp.post("/save_config")
async def save_config(request: Request):
    # Get device_id from form or fallback to baseball_1
    device_id = request.form.get("device_id", "baseball_1")
    try:
        form_data = request.form or {}
        updates = {}
        # Extract mode
        mode = form_data.get("mode")
        if mode:
            updates["mode"] = mode
        # Timing config
        for key in [
            "live_content_timeout",
            "rotation_interval",
            "sub_panel_duration_offset",
        ]:
            val = form_data.get(key)
            if val is not None:
                try:
                    updates[key] = int(val) * 1000
                except Exception:
                    pass
        # Panels
        panels = {}
        for k, v in form_data.items():
            if k.startswith("panels."):
                parts = k.split(".")
                if len(parts) >= 3:
                    panel_name = parts[1]
                    field = parts[2]
                    if panel_name not in panels:
                        panels[panel_name] = {}
                    if field == "enabled":
                        panels[panel_name][field] = True
                    elif field == "duration":
                        try:
                            panels[panel_name][field] = int(v) * 1000
                        except Exception:
                            pass
                    else:
                        panels[panel_name][field] = v
        if panels:
            updates["panels"] = panels
        config_manager.update_device_config(device_id, updates)
        return response.redirect(f"/?success=1&device={device_id}")
    except Exception as e:
        print(f"Error saving config: {e}")
        return response.redirect(f"/?error=invalid_data&device={device_id}")


@index_bp.get("/config")
async def get_config(request: Request):
    """Get full configuration"""
    device_id = request.args.get("device", "baseball_1")
    return response.json(config_manager.get_device_config(device_id))


@index_bp.get("/status/panels")
async def get_panel_status(request: Request):
    """Get real-time panel status"""
    device_id = request.args.get("device", "baseball_1")
    config = config_manager.get_device_config(device_id)
    # This would normally check actual panel states
    # For now, return mock data
    panels = config.get("panels", {})

    panel_status = {}
    for panel_name, panel_config in panels.items():
        panel_status[panel_name] = {
            "has_live_content": panel_name
            in ["baseball", "nascar"],  # Mock live content detection
            "last_update": datetime.utcnow().isoformat() + "Z",
            "status": PanelStatus.ACTIVE.value
            if panel_config.get("enabled", True)
            else PanelStatus.DISABLED.value,
            "current_sub_panel": "live_game"
            if panel_name == "baseball"
            else "cup_races"
            if panel_name == "nascar"
            else "system_status",
        }

    return response.json(panel_status)


@index_bp.get("/status/system")
async def get_system_status(request: Request):
    """Get system health and performance metrics"""
    device_id = request.args.get("device", "baseball_1")
    config = config_manager.get_device_config(device_id)
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        # config = config_manager.get_config() # This line is no longer needed

        system_status = {
            "api_status": ApiStatus.HEALTHY.value,
            "last_config_fetch": datetime.utcnow().isoformat() + "Z",
            "active_mode": config.get("mode", "auto"),
            "current_panel": "baseball",  # Mock current panel
            "uptime_seconds": int(time.time()),  # Mock uptime
            "memory_usage_percent": round(memory.percent, 1),
            "wifi_signal_strength": -65,  # Mock WiFi signal
            "api_response_time_ms": 250,  # Mock response time
        }

        return response.json(system_status)

    except Exception as e:
        print(f"Error getting system status: {e}")
        return response.json(
            {"api_status": ApiStatus.ERROR.value, "error": str(e)}, status=500
        )


@index_bp.get("/status")
async def get_status(request: Request):
    """Legacy status endpoint for backward compatibility"""
    device_id = request.args.get("device", "baseball_1")
    config = config_manager.get_device_config(device_id)
    return response.json(
        {"mode": config.get("mode", "auto"), "status": config.get("mode", "auto")}
    )


@index_bp.get("/preview")
async def data_preview(request: Request):
    """Data preview interface for testing and viewing live data"""
    
    # MLB Teams for dropdown (sorted alphabetically) - using the names that match the API
    mlb_teams = [
        {"name": "Angels"},
        {"name": "D-backs"}, 
        {"name": "Orioles"},
        {"name": "Red Sox"},
        {"name": "Cubs"},
        {"name": "Reds"},
        {"name": "Guardians"},
        {"name": "Rockies"},
        {"name": "Tigers"},
        {"name": "Astros"},
        {"name": "Royals"},
        {"name": "Dodgers"},
        {"name": "Nationals"},
        {"name": "Mets"},
        {"name": "Athletics"},
        {"name": "Pirates"},
        {"name": "Padres"},
        {"name": "Mariners"},
        {"name": "Giants"},
        {"name": "Cardinals"},
        {"name": "Rays"},
        {"name": "Rangers"},
        {"name": "Blue Jays"},
        {"name": "Twins"},
        {"name": "Phillies"},
        {"name": "Braves"},
        {"name": "White Sox"},
        {"name": "Marlins"},
        {"name": "Yankees"},
        {"name": "Brewers"},
    ]

    # NASCAR Series for dropdown
    nascar_series = [
        {"id": "cup", "name": "NASCAR Cup Series"},
        {"id": "xfinity", "name": "NASCAR Xfinity Series"},
        {"id": "truck", "name": "NASCAR Truck Series"},
    ]

    # Generate MLB team options
    mlb_team_options = "\n".join(
        f'<option value="{team["name"]}">{team["name"]}</option>'
        for team in mlb_teams
    )

    # Generate NASCAR series options
    nascar_series_options = "\n".join(
        f'<option value="{series["id"]}">{series["name"]}</option>'
        for series in nascar_series
    )

    return response.html(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sports Data Preview</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .nav-tabs {{
                display: flex;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 30px;
                overflow: hidden;
            }}
            
            .nav-tab {{
                flex: 1;
                padding: 15px 20px;
                background: #ecf0f1;
                border: none;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                color: #7f8c8d;
                transition: all 0.3s;
            }}
            
            .nav-tab.active {{
                background: #3498db;
                color: white;
            }}
            
            .nav-tab:hover {{
                background: #2980b9;
                color: white;
            }}
            
            .tab-content {{
                display: none;
                background: #f8f9fa;
                padding: 30px;
                border-radius: 10px;
                border-left: 4px solid #3498db;
            }}
            
            .tab-content.active {{
                display: block;
            }}
            
            .data-controls {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .control-group {{
                display: flex;
                flex-direction: column;
            }}
            
            .control-group label {{
                margin-bottom: 8px;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .control-group select, .control-group button {{
                padding: 12px;
                border: 2px solid #e1e8ed;
                border-radius: 8px;
                font-size: 16px;
                background: white;
            }}
            
            .control-group select:focus {{
                outline: none;
                border-color: #3498db;
            }}
            
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
                margin: 5px;
            }}
            
            .btn-primary {{
                background: #3498db;
                color: white;
                border: 2px solid #3498db;
                box-shadow: 0 2px 4px rgba(52, 152, 219, 0.3);
            }}
            
            .btn-primary:hover {{
                background: #2980b9;
                border-color: #2980b9;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(52, 152, 219, 0.4);
            }}
            
            .btn-success {{
                background: #27ae60;
                color: white;
            }}
            
            .btn-success:hover {{
                background: #229954;
                transform: translateY(-2px);
            }}
            
            .data-display {{
                background: white;
                padding: 25px;
                border-radius: 10px;
                border: 1px solid #e1e8ed;
                margin-top: 20px;
            }}
            
            .data-display h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            
            .data-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #f1f2f6;
            }}
            
            .data-item:last-child {{
                border-bottom: none;
            }}
            
            .data-label {{
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .data-value {{
                color: #7f8c8d;
                text-align: right;
                max-width: 300px;
                word-wrap: break-word;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            
            .loading {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
            }}
            
            .error {{
                background: #e74c3c;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }}
            
            .nav-links {{
                text-align: center;
                margin-bottom: 20px;
            }}
            
            .nav-links a {{
                display: inline-block;
                padding: 10px 20px;
                margin: 0 10px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.3s;
            }}
            
            .nav-links a:hover {{
                background: #2980b9;
                transform: translateY(-2px);
            }}
            
            .nav-links a.active {{
                background: #27ae60;
            }}
            
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            
            .data-table th,
            .data-table td {{
                padding: 8px 12px;
                border: 1px solid #e1e8ed;
                text-align: left;
            }}
            
            .data-table th {{
                background: #f8f9fa;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .data-table tr:nth-child(even) {{
                background: #f8f9fa;
            }}
            
            .race-header {{
                background: #3498db;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }}
            
            .race-header h4 {{
                margin: 0 0 10px 0;
                font-size: 1.3em;
            }}
            
            .race-header p {{
                margin: 5px 0;
                opacity: 0.9;
            }}
            
            .race-comments {{
                background: #e8f4fd;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                border-left: 4px solid #3498db;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Sports Data Preview</h1>
                <p>Test and view live sports data</p>
            </div>
            
            <div class="content">
                <div class="nav-links">
                    <a href="/">⚙️ Configuration</a>
                    <a href="/preview" class="active">📊 Data Preview</a>
                </div>
                
                <div class="nav-tabs">
                    <button class="nav-tab active" onclick="showTab('baseball')">⚾ Baseball Data</button>
                    <button class="nav-tab" onclick="showTab('nascar')">🏁 NASCAR Data</button>
                </div>
                
                <div id="baseball-tab" class="tab-content active">
                    <div class="data-controls">
                        <div class="control-group">
                            <label>Select Team:</label>
                            <select id="mlb-team">
                                {mlb_team_options}
                            </select>
                        </div>
                        <div class="control-group">
                            <label>Data Type:</label>
                            <select id="mlb-data-type">
                                <option value="last">Last Game</option>
                                <option value="next">Next Game</option>
                                <option value="live">Live Game</option>
                                <option value="live-details">Live Game Details</option>
                            </select>
                        </div>
                        <div class="control-group">
                            <label>&nbsp;</label>
                            <button class="btn btn-primary" onclick="fetchMLBData()">🔍 Fetch Data</button>
                        </div>
                    </div>
                    
                    <div id="mlb-data" class="data-display">
                        <h3>⚾ Baseball Data</h3>
                        <div class="loading">Select a team and data type, then click "Fetch Data"</div>
                    </div>
                </div>
                
                <div id="nascar-tab" class="tab-content">
                    <div class="data-controls">
                        <div class="control-group">
                            <label>Select Series:</label>
                            <select id="nascar-series">
                                {nascar_series_options}
                            </select>
                        </div>
                        <div class="control-group">
                            <label>Data Type:</label>
                            <select id="nascar-data-type">
                                <option value="standings">Standings</option>
                                <option value="race">Upcoming Race</option>
                                <option value="last">Last Race</option>
                                <option value="live">Live Race</option>
                            </select>
                        </div>
                        <div class="control-group">
                            <label>&nbsp;</label>
                            <button class="btn btn-primary" onclick="fetchNASCARData()">🔍 Fetch Data</button>
                        </div>
                    </div>
                    
                    <div id="nascar-data" class="data-display">
                        <h3>🏁 NASCAR Data</h3>
                        <div class="loading">Select a series and data type, then click "Fetch Data"</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function showTab(tabName) {{
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Remove active class from all tabs
                document.querySelectorAll('.nav-tab').forEach(tab => {{
                    tab.classList.remove('active');
                }});
                
                // Show selected tab content
                document.getElementById(tabName + '-tab').classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
            }}
            
            function fetchMLBData() {{
                const teamName = document.getElementById('mlb-team').value;
                const dataType = document.getElementById('mlb-data-type').value;
                
                const dataDiv = document.getElementById('mlb-data');
                dataDiv.innerHTML = '<h3>⚾ Baseball Data</h3><div class="loading">Loading...</div>';
                
                let endpoint = '';
                switch(dataType) {{
                    case 'last':
                        endpoint = `/baseball/last/${{encodeURIComponent(teamName)}}`;
                        break;
                    case 'next':
                        endpoint = `/baseball/next/${{encodeURIComponent(teamName)}}`;
                        break;
                    case 'live':
                        endpoint = `/baseball/live/${{encodeURIComponent(teamName)}}`;
                        break;
                    case 'live-details':
                        endpoint = `/baseball/live/${{encodeURIComponent(teamName)}}/details`;
                        break;
                }}
                
                fetch(endpoint)
                .then(response => response.json())
                .then(data => {{
                    displayData(dataDiv, data, 'Baseball');
                }})
                .catch(error => {{
                    dataDiv.innerHTML = `<h3>⚾ Baseball Data</h3><div class="error">Error: ${{error.message}}</div>`;
                }});
            }}
            
            function fetchNASCARData() {{
                const series = document.getElementById('nascar-series').value;
                const dataType = document.getElementById('nascar-data-type').value;
                
                const dataDiv = document.getElementById('nascar-data');
                dataDiv.innerHTML = '<h3>🏁 NASCAR Data</h3><div class="loading">Loading...</div>';
                
                let endpoint = '';
                switch(dataType) {{
                    case 'standings':
                        endpoint = `/nascar/standings/${{series === 'cup' ? '1' : series === 'xfinity' ? '2' : '3'}}`;
                        break;
                    case 'race':
                        endpoint = `/nascar/race/${{series === 'cup' ? '1' : series === 'xfinity' ? '2' : '3'}}`;
                        break;
                    case 'last':
                        endpoint = `/nascar/race/last/${{series === 'cup' ? '1' : series === 'xfinity' ? '2' : '3'}}`;
                        break;
                    case 'live':
                        endpoint = `/nascar/race/live`;
                        break;
                }}
                
                fetch(endpoint)
                .then(response => response.json())
                .then(data => {{
                    displayData(dataDiv, data, 'NASCAR');
                }})
                .catch(error => {{
                    dataDiv.innerHTML = `<h3>🏁 NASCAR Data</h3><div class="error">Error: ${{error.message}}</div>`;
                }});
            }}
            
            function displayData(container, data, sport) {{
                let html = `<h3>${{sport === 'Baseball' ? '⚾' : '🏁'}} ${{sport}} Data</h3>`;
                
                if (data.error) {{
                    html += `<div class="error">${{data.error}}</div>`;
                }} else if (Array.isArray(data)) {{
                    // Format NASCAR standings data as a table
                    if (data.length > 0 && data[0].first_name) {{
                        html += `
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Pos</th>
                                        <th>Driver</th>
                                        <th>Car #</th>
                                        <th>Points</th>
                                        <th>Delta</th>
                                        <th>Wins</th>
                                        <th>Top 5</th>
                                        <th>Top 10</th>
                                        <th>Poles</th>
                                        <th>Rookie</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `;
                        data.forEach((driver, index) => {{
                            const delta = driver.delta_leader === 0 ? 'Leader' : `-${{driver.delta_leader}}`;
                            const isRookie = driver.is_rookie ? '🟡' : '';
                            html += `
                                <tr>
                                    <td>${{driver.points_position || (index + 1)}}</td>
                                    <td>${{driver.first_name}} ${{driver.last_name}}</td>
                                    <td>#${{driver.car_number}}</td>
                                    <td>${{driver.points}}</td>
                                    <td>${{delta}}</td>
                                    <td>${{driver.wins}}</td>
                                    <td>${{driver.top_5}}</td>
                                    <td>${{driver.top_10}}</td>
                                    <td>${{driver.poles}}</td>
                                    <td>${{isRookie}}</td>
                                </tr>
                            `;
                        }});
                        html += '</tbody></table>';
                    }} else if (data.length > 0 && data[0].driver_name) {{
                        // Format live race data
                        html += `
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Pos</th>
                                        <th>Driver</th>
                                        <th>Car #</th>
                                        <th>Laps</th>
                                        <th>Last Lap Time</th>
                                        <th>Last Lap Speed</th>
                                    </tr>
                                </thead>
                                <tbody>
                        `;
                        data.forEach((vehicle) => {{
                            html += `
                                <tr>
                                    <td>${{vehicle.position}}</td>
                                    <td>${{vehicle.driver_name}}</td>
                                    <td>#${{vehicle.vehicle_number}}</td>
                                    <td>${{vehicle.laps_completed}}</td>
                                    <td>${{vehicle.last_lap_time ? vehicle.last_lap_time.toFixed(3) : 'N/A'}}</td>
                                    <td>${{vehicle.last_lap_speed ? vehicle.last_lap_speed.toFixed(2) + ' mph' : 'N/A'}}</td>
                                </tr>
                            `;
                        }});
                        html += '</tbody></table>';
                    }} else {{
                        // Fallback for other array data
                        html += '<div class="data-items">';
                        data.forEach((item, index) => {{
                            html += `<div class="data-item"><span class="data-label">${{index}}:</span><span class="data-value">${{JSON.stringify(item, null, 2)}}</span></div>`;
                        }});
                        html += '</div>';
                    }}
                }} else if (data.race_name) {{
                    // Format race data (upcoming or past)
                    const isUpcoming = data.is_next_race;
                    const isPast = data.is_last_race;
                    
                    html += `
                        <div class="race-header">
                            <h4>${{data.race_name}} ${{{isUpcoming ? '(Upcoming)' : isPast ? '(Past)' : ''}}}</h4>
                            <p><strong>Track:</strong> ${{data.track_name}}</p>
                            <p><strong>Date:</strong> ${{data.race_date_formatted}}</p>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    if (isPast) {{
                        // Past race details
                        html += `
                            <tr><td>Winner</td><td>${{data.winner_name || 'TBD'}}</td></tr>
                            <tr><td>Margin of Victory</td><td>${{data.margin_of_victory || 'N/A'}}</td></tr>
                            <tr><td>Total Race Time</td><td>${{data.total_race_time || 'N/A'}}</td></tr>
                            <tr><td>Average Speed</td><td>${{data.average_speed ? data.average_speed.toFixed(3) + ' mph' : 'N/A'}}</td></tr>
                            <tr><td>Lead Changes</td><td>${{data.number_of_lead_changes}}</td></tr>
                            <tr><td>Cautions</td><td>${{data.number_of_cautions}} for ${{data.number_of_caution_laps}} laps</td></tr>
                            <tr><td>Pole Winner Speed</td><td>${{data.pole_winner_speed ? data.pole_winner_speed.toFixed(3) + ' mph' : 'N/A'}}</td></tr>
                        `;
                    }} else {{
                        // Upcoming race details
                        html += `
                            <tr><td>Scheduled Distance</td><td>${{data.scheduled_distance}} miles</td></tr>
                            <tr><td>Scheduled Laps</td><td>${{data.scheduled_laps}}</td></tr>
                            <tr><td>Stage Lengths</td><td>${{data.stage_1_laps}}/${{data.stage_2_laps}}/${{data.stage_3_laps}} laps</td></tr>
                            <tr><td>Cars in Field</td><td>${{data.number_of_cars_in_field}}</td></tr>
                            <tr><td>TV Broadcaster</td><td>${{data.television_broadcaster}}</td></tr>
                            <tr><td>Radio Broadcaster</td><td>${{data.radio_broadcaster}}</td></tr>
                        `;
                    }}
                    
                    html += `
                            </tbody>
                        </table>
                    `;
                    
                    if (data.race_comments) {{
                        html += `<div class="race-comments"><strong>Comments:</strong> ${{data.race_comments}}</div>`;
                    }}
                    
                }} else if (data.lap_number !== undefined) {{
                    // Format live race data (main race info)
                    html += `
                        <div class="race-header">
                            <h4>${{data.run_name}} - Live</h4>
                            <p><strong>Track:</strong> ${{data.track_name}} (${{data.track_length}} miles)</p>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Field</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr><td>Current Lap</td><td>${{data.lap_number}} of ${{data.laps_in_race}}</td></tr>
                                <tr><td>Laps to Go</td><td>${{data.laps_to_go}}</td></tr>
                                <tr><td>Flag State</td><td>${{data.flag_state === 1 ? '🟢 Green' : data.flag_state === 2 ? '🟡 Yellow' : data.flag_state === 9 ? '🏁 Checkered' : 'Unknown'}}</td></tr>
                                <tr><td>Stage</td><td>${{data.stage ? `Stage ${{data.stage.stage_num}} (Lap ${{data.stage.finish_at_lap}})` : 'N/A'}}</td></tr>
                                <tr><td>Lead Changes</td><td>${{data.number_of_lead_changes}}</td></tr>
                                <tr><td>Leaders</td><td>${{data.number_of_leaders}}</td></tr>
                                <tr><td>Cautions</td><td>${{data.number_of_caution_segments}} for ${{data.number_of_caution_laps}} laps</td></tr>
                                <tr><td>Time</td><td>${{data.time_of_day_os_formatted}}</td></tr>
                            </tbody>
                        </table>
                        
                        <h4 style="margin-top: 20px;">Top 3 Positions</h4>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Pos</th>
                                    <th>Driver</th>
                                    <th>Car #</th>
                                    <th>Laps</th>
                                    <th>Last Lap Time</th>
                                    <th>Last Lap Speed</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    
                    if (data.vehicles && data.vehicles.length > 0) {{
                        data.vehicles.slice(0, 3).forEach((vehicle) => {{
                            html += `
                                <tr>
                                    <td>${{vehicle.position}}</td>
                                    <td>${{vehicle.driver_name}}</td>
                                    <td>#${{vehicle.vehicle_number}}</td>
                                    <td>${{vehicle.laps_completed}}</td>
                                    <td>${{vehicle.last_lap_time ? vehicle.last_lap_time.toFixed(3) : 'N/A'}}</td>
                                    <td>${{vehicle.last_lap_speed ? vehicle.last_lap_speed.toFixed(2) + ' mph' : 'N/A'}}</td>
                                </tr>
                            `;
                        }});
                    }}
                    
                    html += '</tbody></table>';
                    
                }} else {{
                    // Format single object data
                    html += '<div class="data-items">';
                    for (const [key, value] of Object.entries(data)) {{
                        if (key !== 'status') {{
                            const displayValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : value;
                            html += `
                                <div class="data-item">
                                    <span class="data-label">${{key}}:</span>
                                    <span class="data-value">${{displayValue}}</span>
                                </div>
                            `;
                        }}
                    }}
                    html += '</div>';
                }}
                
                container.innerHTML = html;
            }}
        </script>
    </body>
    </html>
    """)
