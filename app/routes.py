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

    # Generate mode options
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
            <h3>{panel_name.title()} Panel</h3>
            <div class="form-group">
                <label>
                    <input type="checkbox" name="panels.{panel_name}.enabled" {enabled_checked}>
                    Enabled
                </label>
            </div>
            <div class="form-group">
                <label>Duration (seconds):</label>
                <input type="number" name="panels.{panel_name}.duration" value="{duration_value}" min="5" max="300">
            </div>
            <div class="form-group">
                <label>Priority:</label>
                <select name="panels.{panel_name}.priority">
                    {priority_options}
                </select>
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
            
            .section {{
                margin-bottom: 40px;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #3498db;
            }}
            
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.5em;
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
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}
            
            .panel-config {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #e1e8ed;
            }}
            
            .panel-config h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 8px;
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
            
            .status-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            
            .status-item {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            
            .status-label {{
                font-size: 0.9em;
                color: #7f8c8d;
                margin-bottom: 5px;
            }}
            
            .status-value {{
                font-size: 1.2em;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .api-links {{
                margin-top: 40px;
                padding: 20px;
                background: #ecf0f1;
                border-radius: 10px;
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
            
            .device-selector {{
                background: #ecf0f1;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            
            .device-selector h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            
            .device-controls {{
                display: flex;
                gap: 10px;
                align-items: center;
                margin-top: 15px;
            }}
            
            .device-controls input {{
                flex: 1;
                padding: 8px 12px;
                border: 2px solid #e1e8ed;
                border-radius: 5px;
            }}
            
            .device-controls button {{
                padding: 8px 16px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            
            .device-controls button:hover {{
                background: #2980b9;
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
                <div class="device-selector">
                    <h3>📱 Device Selection</h3>
                    <form method="GET" action="/">
                        <div class="form-group">
                            <label for="device">Select Device:</label>
                            <select name="device" id="device" onchange="this.form.submit()">
                                {device_options}
                            </select>
                        </div>
                    </form>
                    
                    <div class="device-controls">
                        <input type="text" id="newDeviceId" placeholder="New device ID (e.g., office_display)">
                        <button onclick="addDevice()">➕ Add Device</button>
                        <button onclick="removeDevice()" style="background: #e74c3c;">🗑️ Remove Device</button>
                    </div>
                </div>
                
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">Current Device</div>
                        <div class="status-value">{device_id}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Display Mode</div>
                        <div class="status-value">{config.get("mode", "auto").title()}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Rotation Interval</div>
                        <div class="status-value">{int(timing_config.get("rotation_interval", 15000)) // 1000}s</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Live Timeout</div>
                        <div class="status-value">{int(timing_config.get("live_content_timeout", 120000)) // 1000}s</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Sub-panel Offset</div>
                        <div class="status-value">{int(timing_config.get("sub_panel_duration_offset", 5000)) // 1000}s</div>
                    </div>
                </div>
                
                <form action="/save_config" method="POST">
                    <input type="hidden" name="device_id" value="{device_id}">
                    
                    <div class="section">
                        <h2>🎛️ Display Mode</h2>
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
                    </div>
                    
                    <div class="section">
                        <h2>⏱️ Timing Configuration</h2>
                        <div class="timing-grid">
                            <div class="form-group">
                                <label>Live Content Timeout (seconds):</label>
                                <input type="number" name="live_content_timeout" 
                                       value="{timing_config.get("live_content_timeout", 120000) // 1000}" 
                                       min="30" max="600" step="30">
                                <small style="color: #7f8c8d;">How long to show live content before rotating</small>
                            </div>
                            <div class="form-group">
                                <label>Rotation Interval (seconds):</label>
                                <input type="number" name="rotation_interval" 
                                       value="{timing_config.get("rotation_interval", 15000) // 1000}" 
                                       min="5" max="120" step="5">
                                <small style="color: #7f8c8d;">Time between panel rotations</small>
                            </div>
                            <div class="form-group">
                                <label>Sub-panel Duration Offset (seconds):</label>
                                <input type="number" name="sub_panel_duration_offset" 
                                       value="{timing_config.get("sub_panel_duration_offset", 5000) // 1000}" 
                                       min="1" max="30" step="1">
                                <small style="color: #7f8c8d;">Additional time for sub-panels</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📺 Panel Configuration</h2>
                        {panel_configs}
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn btn-success">💾 Save Configuration</button>
                        <a href="/config?device={device_id}" class="btn btn-secondary">📋 View Raw Config</a>
                        <a href="/status/panels?device={device_id}" class="btn btn-secondary">📊 Panel Status</a>
                        <a href="/status/system?device={device_id}" class="btn btn-secondary">🔧 System Status</a>
                    </div>
                </form>
                
                <div class="api-links">
                    <h3>🔗 API Endpoints</h3>
                    <a href="/config?device={device_id}" target="_blank">GET /config</a>
                    <a href="/status/panels?device={device_id}" target="_blank">GET /status/panels</a>
                    <a href="/status/system?device={device_id}" target="_blank">GET /status/system</a>
                    <a href="/status?device={device_id}" target="_blank">GET /status</a>
                </div>
            </div>
        </div>
        
        <script>
            function addDevice() {{
                const deviceId = document.getElementById('newDeviceId').value.trim();
                if (deviceId) {{
                    window.location.href = '/?device=' + encodeURIComponent(deviceId);
                }}
            }}
            
            function removeDevice() {{
                const currentDevice = '{device_id}';
                if (currentDevice !== 'baseball_1') {{
                    if (confirm('Are you sure you want to remove device "' + currentDevice + '"?')) {{
                        // This would need a backend endpoint to remove devices
                        alert('Device removal not yet implemented');
                    }}
                }} else {{
                    alert('Cannot remove the default device (baseball_1)');
                }}
            }}
            
            // Auto-refresh status every 30 seconds
            setInterval(() => {{
                // Refresh the page to get updated status
                // window.location.reload();
            }}, 30000);
        </script>
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
