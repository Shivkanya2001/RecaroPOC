import subprocess
import sys

def get_service_name_from_display(display_name):
    """Resolve internal service name from display name using PowerShell."""
    ps_script = f"""
    $svc = Get-Service | Where-Object {{ $_.DisplayName -eq "{display_name}" }}
    if ($svc) {{ $svc.Name }} else {{ "NOT_FOUND" }}
    """
    result = subprocess.run(["powershell", "-Command", ps_script],
                            capture_output=True, text=True)
    return result.stdout.strip()

def get_service_status(service_name):
    """Retrieve the current status (Running, Stopped, etc.) of a service."""
    ps_script = f"(Get-Service -Name '{service_name}').Status"
    result = subprocess.run(["powershell", "-Command", ps_script],
                            capture_output=True, text=True)
    return result.stdout.strip()

def control_service(display_name, action):
    action = action.lower()
    if action not in ["start", "stop"]:
        print("Invalid action. Use 'start' or 'stop'.")
        return

    service_name = get_service_name_from_display(display_name)
    if service_name == "NOT_FOUND":
        print(f"[SKIPPED] Could not find service with display name: '{display_name}'")
        return

    # Get current status
    before_status = get_service_status(service_name)

    # Determine if action is needed
    if action == "start" and before_status.lower() == "running":
        print(f"[NO ACTION] '{display_name}' is already running.")
        return
    elif action == "stop" and before_status.lower() == "stopped":
        print(f"[NO ACTION] '{display_name}' is already stopped.")
        return

    # Execute the start/stop action
    command = f"{action}-Service -Name '{service_name}'"
    try:
        subprocess.run(["powershell", "-Command", command],
                       check=True, capture_output=True, text=True)
        after_status = get_service_status(service_name)
        print(f"[SUCCESS] {action.capitalize()}ed '{display_name}' (internal name: '{service_name}').")
        print(f"    Previous status: {before_status}")
        print(f"    Current status : {after_status}")
    except subprocess.CalledProcessError as e:
        print(f"[FAILED] Could not {action} '{display_name}' (internal name: '{service_name}').")
        print("    Output:", e.stdout.strip())
        print("    Error :", e.stderr.strip())

def main():
    if len(sys.argv) != 3:
        print("Usage: python control_service.py <path_to_service_list.txt> <start|stop>")
        sys.exit(1)

    service_list_file = sys.argv[1]
    action = sys.argv[2]

    try:
        with open(service_list_file, 'r', encoding='utf-8') as f:
            services = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] File not found: {service_list_file}")
        sys.exit(1)

    for display_name in services:
        print(f"\n--- Processing: {display_name} ---")
        control_service(display_name, action)

if __name__ == "__main__":
    main()
