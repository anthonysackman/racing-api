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
    config = config_manager.get_config()

    # Generate mode options
    mode_options = "\n".join(
        f'<option value="{mode.value}"{" selected" if mode.value == config["mode"] else ""}>{mode.name.title()}</option>'
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
    timing_config = config_manager.get_timing_config() or {}

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
                padding: 30px;
            }}
            
            .section {{
                margin-bottom: 40px;
                padding: 25px;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
                background: #f8f9fa;
            }}
            
            .section h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
                font-size: 1.5em;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            
            .form-group {{
                margin-bottom: 20px;
            }}
            
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #34495e;
            }}
            
            .form-group input[type="text"],
            .form-group input[type="number"],
            .form-group select {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }}
            
            .form-group input[type="text"]:focus,
            .form-group input[type="number"]:focus,
            .form-group select:focus {{
                outline: none;
                border-color: #3498db;
                box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
            }}
            
            .form-group input[type="checkbox"] {{
                margin-right: 10px;
                transform: scale(1.2);
            }}
            
            .panel-config {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border: 1px solid #ddd;
            }}
            
            .panel-config h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
            }}
            
            .timing-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }}
            
            .btn {{
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                margin: 5px;
            }}
            
            .btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
            }}
            
            .btn-secondary {{
                background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
            }}
            
            .btn-success {{
                background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            }}
            
            .status-bar {{
                background: #ecf0f1;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }}
            
            .status-item {{
                text-align: center;
                flex: 1;
                min-width: 120px;
            }}
            
            .status-label {{
                font-size: 0.9em;
                color: #7f8c8d;
                margin-bottom: 5px;
            }}
            
            .status-value {{
                font-size: 1.1em;
                font-weight: 600;
                color: #2c3e50;
            }}
            
            .api-links {{
                margin-top: 20px;
                padding: 20px;
                background: #e8f4fd;
                border-radius: 8px;
                border-left: 4px solid #3498db;
            }}
            
            .api-links h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            
            .api-links a {{
                color: #3498db;
                text-decoration: none;
                margin-right: 20px;
                padding: 8px 12px;
                border-radius: 4px;
                background: white;
                border: 1px solid #3498db;
                transition: all 0.3s ease;
            }}
            
            .api-links a:hover {{
                background: #3498db;
                color: white;
            }}
            
            @media (max-width: 768px) {{
                .timing-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .status-bar {{
                    flex-direction: column;
                    gap: 10px;
                }}
                
                .status-item {{
                    min-width: auto;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏈 Sports Matrix Display</h1>
                <p>Configuration & Control Panel</p>
            </div>
            
            <div class="content">
                <div class="status-bar">
                    <div class="status-item">
                        <div class="status-label">Current Mode</div>
                        <div class="status-value">{config["mode"].title()}</div>
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
                                       value="{timing_config["live_content_timeout"] // 1000}" 
                                       min="30" max="600" step="30">
                                <small style="color: #7f8c8d;">How long to show live content before rotating</small>
                            </div>
                            <div class="form-group">
                                <label>Rotation Interval (seconds):</label>
                                <input type="number" name="rotation_interval" 
                                       value="{timing_config["rotation_interval"] // 1000}" 
                                       min="5" max="120" step="5">
                                <small style="color: #7f8c8d;">Time between panel rotations</small>
                            </div>
                            <div class="form-group">
                                <label>Sub-panel Duration Offset (seconds):</label>
                                <input type="number" name="sub_panel_duration_offset" 
                                       value="{timing_config["sub_panel_duration_offset"] // 1000}" 
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
                        <a href="/config" class="btn btn-secondary">📋 View Raw Config</a>
                        <a href="/status/panels" class="btn btn-secondary">📊 Panel Status</a>
                        <a href="/status/system" class="btn btn-secondary">🔧 System Status</a>
                    </div>
                </form>
                
                <div class="api-links">
                    <h3>🔗 API Endpoints</h3>
                    <a href="/config" target="_blank">GET /config</a>
                    <a href="/status/panels" target="_blank">GET /status/panels</a>
                    <a href="/status/system" target="_blank">GET /status/system</a>
                    <a href="/status" target="_blank">GET /status</a>
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh status every 30 seconds
            setInterval(() => {{
                fetch('/status/system')
                    .then(response => response.json())
                    .then(data => {{
                        // Update status bar with new data
                        console.log('Status updated:', data);
                    }})
                    .catch(error => console.error('Status update failed:', error));
            }}, 30000);
            
            // Form validation
            document.querySelector('form').addEventListener('submit', function(e) {{
                const durationInputs = document.querySelectorAll('input[name*="duration"]');
                durationInputs.forEach(input => {{
                    const value = parseInt(input.value);
                    if (value < 5 || value > 300) {{
                        e.preventDefault();
                        alert('Panel duration must be between 5 and 300 seconds');
                        input.focus();
                        return;
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """)


@index_bp.post("/save_config")
async def save_config(request: Request):
    """Save configuration from form"""
    try:
        # Parse form data
        form_data = request.form

        # Extract mode
        mode = form_data.get("mode", "auto")

        # Extract timing configuration
        timing_config = {
            "live_content_timeout": int(form_data.get("live_content_timeout", 120))
            * 1000,
            "rotation_interval": int(form_data.get("rotation_interval", 15)) * 1000,
            "sub_panel_duration_offset": int(
                form_data.get("sub_panel_duration_offset", 5)
            )
            * 1000,
        }

        # Extract panel configurations
        panels = {}
        for key, value in form_data.items():
            if key.startswith("panels."):
                parts = key.split(".")
                if len(parts) >= 3:
                    panel_name = parts[1]
                    field_name = parts[2]

                    if panel_name not in panels:
                        panels[panel_name] = {}

                    if field_name == "enabled":
                        panels[panel_name][field_name] = True
                    elif field_name == "duration":
                        panels[panel_name][field_name] = (
                            int(value) * 1000
                        )  # Convert to milliseconds
                    else:
                        panels[panel_name][field_name] = value

        # Update configuration
        config_updates = {
            "mode": mode,
            "live_content_timeout": timing_config["live_content_timeout"],
            "rotation_interval": timing_config["rotation_interval"],
            "sub_panel_duration_offset": timing_config["sub_panel_duration_offset"],
            "panels": panels,
        }

        success = config_manager.update_config(config_updates)

        if success:
            return response.redirect("/?success=1")
        else:
            return response.redirect("/?error=save_failed")

    except Exception as e:
        print(f"Error saving config: {e}")
        return response.redirect("/?error=invalid_data")


@index_bp.get("/config")
async def get_config(request: Request):
    """Get full configuration"""
    return response.json(config_manager.get_config())


@index_bp.get("/status/panels")
async def get_panel_status(request: Request):
    """Get real-time panel status"""
    # This would normally check actual panel states
    # For now, return mock data
    config = config_manager.get_config()
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
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        config = config_manager.get_config()

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
    return response.json({"mode": config_manager.get_mode()})
