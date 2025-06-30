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

def run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, scope, mode, action, folder, log_file, xml_files, bat_file_path):
    logging.info("Inside run_preferences_manager with TC_ROOT: %s", tc_root)

    # Ensure xml_files is not empty
    if not xml_files:
        logging.error("No XML files provided.")
        return
    
    logging.info(f"Processing XML files: {xml_files}")

    for xml_file in xml_files:
        # Dynamically construct full XML file path using folder path and file name
        xml_file_path = os.path.join(folder, xml_file.strip()).replace("\\", "/")
        
        # Log the XML file path
        logging.info(f"Constructed XML file path: {xml_file_path}")

        # Ensure the XML file path exists
        if not os.path.isfile(xml_file_path):
            logging.error(f"Error: The XML file does not exist at {xml_file_path}")
            continue

        # Skip empty files
        if os.path.getsize(xml_file_path) == 0:
            logging.warning(f"Skipping empty file: {xml_file_path}")
            continue

        bin_dir = os.path.join(tc_root, "bin").replace("\\", "/")
        preferences_manager_path = os.path.join(bin_dir, "preferences_manager.exe").replace("\\", "/")
        password_file_path = os.path.join(tc_root, "security", password_file_name).replace("\\", "/")

        logging.info(f"Password file path: {password_file_path}")

        if not os.path.isfile(password_file_path):
            logging.error(f"Error: The password file does not exist at {password_file_path}")
            continue

        # Construct the command to execute the preferences_manager.exe after setting the environment
        command = f'"{bat_file_path}" && "{preferences_manager_path}" -u={user} -pf="{password_file_path}" -g={group} -scope={scope} -mode={mode} -action={action} -file="{xml_file_path}"'

        logging.info(f"Constructed command: {command}")

        try:
            result = subprocess.run(command, capture_output=True, shell=True, text=True)
            if result.returncode == 0:
                logging.info(f"✅ Successfully executed for {xml_file_path}")
                logging.info(f"stdout:\n{result.stdout}")
            else:
                logging.error(f"Command failed for {xml_file_path}")
                logging.error(f"stderr: {result.stderr}")
                logging.error(f"stdout: {result.stdout}")
        except FileNotFoundError as e:
            logging.error(f"Exception running command for {xml_file_path}: {e}")

def set_environment_variable_from_bat(bat_file_path, preferences_manager_path, user, password_file_name, group, scope, mode, action, folder, log_file, xml_files):
    logging.info(f"Running batch file: {bat_file_path}")

    result = subprocess.run([bat_file_path], capture_output=True, shell=True, text=True)

    if result.returncode != 0:
        logging.error(f"Failed to execute batch file: {bat_file_path}")
        logging.error(result.stderr)
        return

    tc_root = None
    tc_data = None

    for line in result.stdout.splitlines():
        if "TC_ROOT=" in line:
            tc_root = line.split('=')[1].strip()
        elif "TC_DATA=" in line:
            tc_data = line.split('=')[1].strip()

    if not tc_root or not tc_data:
        logging.error("Could not capture TC_ROOT or TC_DATA from batch output.")
        return

    os.environ['TC_ROOT'] = tc_root
    os.environ['TC_DATA'] = tc_data
    logging.info(f"Set TC_ROOT={tc_root}")
    logging.info(f"Set TC_DATA={tc_data}")

    try:
        # If no xml_files are provided, get all XML files in the folder
        if not xml_files:
            logging.info(f"Getting all XML files from the folder: {folder}")
            xml_files = [f for f in os.listdir(folder) if f.endswith(".xml")]
        logging.info(f"Found XML files: {xml_files}")
        
        for xml_file in xml_files:
            run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, scope, mode, action, folder, log_file, [xml_file], bat_file_path)
    except Exception as e:
        logging.error(f"Error during XML processing: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run preferences_manager.exe with dynamic parameters.")
    parser.add_argument("preferences_manager", help="Relative or full path to preferences_manager.exe.")
    parser.add_argument("-u", "--user", required=True, help="Teamcenter username.")
    parser.add_argument("-g", "--group", required=True, help="Group name.")
    parser.add_argument("-scope", "--scope", required=True, help="Preference scope.")
    parser.add_argument("-mode", "--mode", required=True, choices=['import', 'export'], help="Mode of operation.")
    parser.add_argument("-action", "--action", required=True, choices=['OVERRIDE', 'ADD', 'REMOVE'], help="Action type.")
    parser.add_argument("--folder", required=False, help="Folder containing XML files. Provide either this or --xml-files, not both.")
    parser.add_argument("-pf", "--password-file", required=True, help="Password file name inside TC security folder.")
    parser.add_argument("--xml-files", nargs='*', help="List of XML files to process. Provide either this or --folder, not both.")

    args = parser.parse_args()

    # Ensure that both --folder and --xml-files are not provided together
    if args.folder and args.xml_files:
        logging.error("Error: You cannot provide both --folder and --xml-files at the same time.")
        sys.exit(1)

    log_file = setup_logger()

    # Read batch file path from environment variable
    bat_file_path = os.environ.get('EXECUTE_SET_TC_CONFIG_BAT')
    if not bat_file_path:
        logging.error("Environment variable 'EXECUTE_SET_TC_CONFIG_BAT' is not set.")
        sys.exit(1)
    if not os.path.isfile(bat_file_path):
        logging.error(f"Batch file path '{bat_file_path}' does not exist.")
        sys.exit(1)

    # If --folder is provided, process all XML files in that folder
    if args.folder:
        set_environment_variable_from_bat(
            bat_file_path,
            args.preferences_manager,
            args.user,
            args.password_file,
            args.group,
            args.scope,
            args.mode,
            args.action,
            args.folder,
            log_file,
            []  # No XML files specified, process all files in the folder
        )
    elif args.xml_files:
        # If --xml-files is provided, process only those specific files
        set_environment_variable_from_bat(
            bat_file_path,
            args.preferences_manager,
            args.user,
            args.password_file,
            args.group,
            args.scope,
            args.mode,
            args.action,
            args.folder,
            log_file,
            args.xml_files  # Process the passed XML files
        )

if __name__ == "__main__":
    main()
