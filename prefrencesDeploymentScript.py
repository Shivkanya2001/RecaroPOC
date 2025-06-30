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

def get_tc_root_from_bat(bat_file_path):
    command = f'cmd.exe /c "call \"{bat_file_path}\" && echo %TC_ROOT%"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        lines = result.stdout.strip().splitlines()
        if lines:
            return lines[-1].strip()
    return None

def run_preferences_manager(user, password_file_name, group, scope, mode, action, folder, log_file, xml_file, tc_root):
    logging.info("Executing preferences_manager.exe with resolved TC_ROOT")

    xml_file_path = os.path.join(folder, xml_file).replace("\\", "/")
    if not os.path.isfile(xml_file_path):
        logging.error(f"XML file does not exist: {xml_file_path}")
        return

    preferences_manager_path = os.path.join(tc_root, "bin", "preferences_manager.exe").replace("\\", "/")
    password_file_path = os.path.join(tc_root, "security", password_file_name).replace("\\", "/")

    logging.info(f"Using preferences_manager path: {preferences_manager_path}")
    logging.info(f"Using password file path: {password_file_path}")

    command = (
        f'"{preferences_manager_path}" -u={user} -pf="{password_file_path}" '
        f'-g={group} -scope={scope} -mode={mode} -action={action} -file="{xml_file_path}"'
    )

    logging.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, capture_output=True, shell=True, text=True)
        if result.returncode == 0:
            logging.info(f"✅ Successfully executed for {xml_file_path}")
            logging.info(result.stdout)
        else:
            logging.error(f"❌ Command failed for {xml_file_path}")
            logging.error(result.stderr)
    except Exception as e:
        logging.error(f"Exception while executing command for {xml_file_path}: {e}")

def set_environment_and_execute(user, password_file_name, group, scope, mode, action, folder, log_file):
    bat_file_path = os.environ.get("EXECUTE_SET_TC_CONFIG_BAT")
    logging.info(f"Reading batch file path from environment variable: {bat_file_path}")

    if not bat_file_path or not os.path.isfile(bat_file_path):
        logging.error(f"❌ Batch file path is not set or invalid: '{bat_file_path}'")
        return

    tc_root = get_tc_root_from_bat(bat_file_path)
    if not tc_root:
        logging.error("❌ Could not extract TC_ROOT from the batch file.")
        return

    try:
        xml_files = [f for f in os.listdir(folder) if f.endswith(".xml")]
        logging.info(f"Found XML files: {xml_files}")

        for xml_file in xml_files:
            run_preferences_manager(
                user,
                password_file_name,
                group,
                scope,
                mode,
                action,
                folder,
                log_file,
                xml_file,
                tc_root
            )

    except Exception as e:
        logging.error(f"Error while processing XML files: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run preferences_manager.exe with dynamic parameters.")
    parser.add_argument("preferences_manager", help="The name of preferences_manager.exe (used for validation only).")
    parser.add_argument("-u", "--user", required=True, help="The user name.")
    parser.add_argument("-g", "--group", required=True, help="The group.")
    parser.add_argument("-scope", "--scope", required=True, help="The scope.")
    parser.add_argument("-mode", "--mode", required=True, choices=['import', 'export'], help="The mode (import/export).")
    parser.add_argument("-action", "--action", required=True, choices=['OVERRIDE', 'ADD', 'REMOVE'], help="The action.")
    parser.add_argument("--folder", required=True, help="The folder containing the XML files.")
    parser.add_argument("-pf", "--password-file", required=True, help="The password file name inside the security folder.")

    args = parser.parse_args()
    log_file = setup_logger()

    set_environment_and_execute(
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
