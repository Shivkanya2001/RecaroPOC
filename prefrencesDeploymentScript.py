import subprocess
import os
import sys
import argparse
import logging
from datetime import datetime

# Function to set up logger with timestamped filenames
def setup_logger():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"preferences_manager_{timestamp}.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w"
    )
    logging.info("Logger initialized.")
    return log_file

def run_preferences_through_batch_and_python(preferences_manager_path, user, password_file_name, group, scope, mode, action, folder, log_file):
    # Read the batch file path from the environment variable
    bat_file_path = os.environ.get("EXECUTE_SET_TC_CONFIG_BAT")

    if not bat_file_path:
        logging.error("❌ Environment variable 'EXECUTE_SET_TC_CONFIG_BAT' is not set.")
        sys.exit(1)

    if not os.path.isfile(bat_file_path):
        logging.error(f"❌ Batch file path '{bat_file_path}' does not exist.")
        sys.exit(1)

    # Dynamically build the python command that should run after the .bat file
    python_command = (
        f'python run_preferences.py {preferences_manager_path} '
        f'-u={user} -g={group} -scope={scope} -mode={mode} '
        f'-action={action} --folder="{folder}" -pf={password_file_name}'
    )

    # Combine the batch file call and the Python script into one Windows command
    full_command = f'cmd.exe /c "call \"{bat_file_path}\" && {python_command}"'
    logging.info(f"Executing combined command: {full_command}")

    try:
        result = subprocess.run(full_command, shell=True, text=True)
        if result.returncode == 0:
            logging.info("✅ Batch and Python script executed successfully.")
        else:
            logging.error(f"❌ Execution failed with return code: {result.returncode}")
    except Exception as e:
        logging.error(f"Exception during execution: {e}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run preferences_manager.exe with dynamic parameters via batch execution.")
    parser.add_argument("preferences_manager", help="The relative or full path to preferences_manager.exe.")
    parser.add_argument("-u", "--user", required=True, help="The user name.")
    parser.add_argument("-g", "--group", required=True, help="The group.")
    parser.add_argument("-scope", "--scope", required=True, help="The scope.")
    parser.add_argument("-mode", "--mode", required=True, choices=['import', 'export'], help="The mode (import/export).")
    parser.add_argument("-action", "--action", required=True, choices=['OVERRIDE', 'ADD', 'REMOVE'], help="The action (OVERRIDE/ADD/REMOVE).")
    parser.add_argument("--folder", required=True, help="The folder containing the XML files (e.g., preferences).")
    parser.add_argument("-pf", "--password-file", required=True, help="The password file name located in the security folder.")

    args = parser.parse_args()
    log_file = setup_logger()

    run_preferences_through_batch_and_python(
        args.preferences_manager,
        args.user,
        args.password_file,
        args.group,
        args.scope,
        args.mode,
        args.action,
        args.folder,
        log_file
    )

if __name__ == "__main__":
    main()
