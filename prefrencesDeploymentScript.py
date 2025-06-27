import subprocess
import os
import sys
import argparse
import logging
from datetime import datetime

# Function to set up logger with timestamped filenames
def setup_logger():
    """Set up a logger to write log messages to a file with timestamped filenames."""
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

def run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, mode, action, log_file, xml_file_path):
    """Run the preferences_manager.exe utility from TC_ROOT/bin with the given parameters."""
    logging.info("inside function %s", tc_root)

    # Check if the XML file exists
    if not os.path.isfile(xml_file_path):
        logging.error(f"Error: The XML file does not exist at {xml_file_path}")
        return

    preferences_manager_path = os.path.join(tc_root, "bin", "preferences_manager.exe")

    # Log the constructed command
    command = f'{preferences_manager_path} -u={user} -pf="{password_file_name}" -g={group} -mode={mode} -action={action} -file="{xml_file_path}"'
    logging.info(f"Constructed command: {command}")

    try:
        # Run the command from the 'bin' directory inside TC_ROOT
        result = subprocess.run(command, capture_output=True, shell=True, text=True)

        # Log the result of the command execution
        if result.returncode == 0:
            logging.info(f"Command executed successfully for {xml_file_path}!")
            logging.info(f"Command output:\n{result.stdout}")
        else:
            logging.error(f"Error executing the command for {xml_file_path}: {result.stderr}")
    except FileNotFoundError as e:
        logging.error(f"Error running the command for {xml_file_path}: {e}")

def set_environment_variable_from_bat(bat_file_path, preferences_manager_path, user, password_file_name, group, mode, action, preferences_folder, log_file):
    """Execute the batch file to set TC_ROOT environment variable and then call preferences_manager.exe for each XML file in preferences folder."""
    logging.info(f"Running batch file {bat_file_path} to set TC_ROOT.")

    # Run the batch file to set TC_ROOT environment variable
    result = subprocess.run([bat_file_path], capture_output=True, shell=True, text=True)

    # Log the result of the batch file execution
    if result.returncode == 0:
        logging.info(f"Successfully executed {bat_file_path}")
    else:
        logging.error(f"Error executing {bat_file_path}")
        return None

    # Get the TC_ROOT from the batch output (assuming the batch file sets it)
    tc_root = "D:/apps/siemens/tc_root"  # This could be extracted from the batch output
    logging.info(f"TC_ROOT set to {tc_root}.")

    # Set the environment variable for TC_ROOT
    os.environ['TC_ROOT'] = tc_root
    logging.info(f"Environment variable TC_ROOT set to: {tc_root}")

    logging.info(f"TC_ROOT: {tc_root}")

    # Loop through all XML files in the preferences folder and run the command for each XML file
    try:
        # List all XML files in the preferences folder
        xml_files = [f for f in os.listdir(preferences_folder) if f.endswith(".xml")]
        logging.info(f"Found XML files: {xml_files}")

        # Run the command for each XML file
        for xml_file in xml_files:
            xml_file_path = os.path.join(preferences_folder, xml_file)  # Construct the full XML path
            logging.info(f"Processing {xml_file_path}...")
            run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, mode, action, log_file, xml_file_path)

    except Exception as e:
        logging.error(f"Error processing XML files: {e}")

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run preferences_manager.exe with dynamic parameters.")

    # Define the arguments expected
    parser.add_argument("preferences_manager", help="The relative or full path to preferences_manager.exe.")
    parser.add_argument("-u", "--user", required=True, help="The user name.")
    parser.add_argument("-g", "--group", required=True, help="The group.")
    parser.add_argument("-mode", "--mode", required=True, choices=['import', 'export'], help="The mode (import/export).")
    parser.add_argument("-action", "--action", required=True, choices=['OVERRIDE', 'ADD', 'REMOVE'], help="The action (OVERRIDE/ADD/REMOVE).")
    parser.add_argument("--folder", required=True, help="The folder containing the XML files (e.g., preferences).")
    parser.add_argument("-batch-file", "--bat_file", required=True, help="The path to the batch file for setting TC_ROOT.")
    parser.add_argument("-pf", "--password-file", required=True, help="The password file name located in the security folder.")

    # Parse the arguments
    args = parser.parse_args()

    # Set up logger
    log_file = setup_logger()

    # Call the function to process and run the command for each XML file
    set_environment_variable_from_bat(args.bat_file, args.preferences_manager, args.user, args.password_file, args.group, args.mode, args.action, args.folder, log_file)

if __name__ == "__main__":
    main()
