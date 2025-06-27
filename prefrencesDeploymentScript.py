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

# Function to execute batch file and extract TC_ROOT from the output
def run_batch_file(bat_file_path):
    """Execute the batch file and extract TC_ROOT value."""
    logging.info(f"Running batch file {bat_file_path} to set TC_ROOT.")

    # Run the batch file and capture the output
    result = subprocess.run([bat_file_path], capture_output=True, shell=True, text=True)

    # Check the result and extract TC_ROOT from batch output if successful
    if result.returncode == 0:
        logging.info(f"Successfully executed {bat_file_path}")
        
        # Assuming the batch file echoes 'set TC_ROOT=' value
        tc_root = None
        for line in result.stdout.splitlines():
            if "set TC_ROOT=" in line:
                tc_root = line.split('=')[1].strip()
                logging.info(f"TC_ROOT set to {tc_root}.")
                break
        if not tc_root:
            logging.error("Error: TC_ROOT not found in batch file output.")
            return None
        
        return tc_root
    else:
        logging.error(f"Error executing {bat_file_path}")
        return None

# Function to run the preferences manager with the given parameters
def run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, mode, action, log_file, xml_file):
    """Run the preferences_manager.exe utility from TC_ROOT/bin with the given parameters."""
    logging.info("inside function %s", tc_root)

    # Construct the path to the 'bin' directory dynamically
    bin_dir = os.path.join(tc_root, "bin")

    # Log the current working directory before we change it
    logging.info(f"Current working directory: {os.getcwd()}")

    # Check if the 'bin' directory exists under TC_ROOT
    if not os.path.isdir(bin_dir):
        logging.error(f"Error: The 'bin' directory does not exist at {bin_dir}")
        return

    # Log the path of the bin directory
    logging.info(f"Changed working directory to {bin_dir}.")

    # Construct the full path to the password file inside the security folder
    password_file_path = os.path.join(tc_root, "security", password_file_name)
    logging.info("Password file path constructed %s", password_file_path)

    # Check if the password file exists
    if not os.path.isfile(password_file_path):
        logging.error(f"Error: The password file does not exist at {password_file_path}")
        return

    logging.info(f"Password file found at {password_file_path}.")

    # Construct the full path to the XML file
    xml_file_path = os.path.join(tc_root, "preferences", xml_file)

    # Check if the XML file exists
    if not os.path.isfile(xml_file_path):
        logging.error(f"Error: The XML file does not exist at {xml_file_path}")
        return

    logging.info(f"Processing XML file: {xml_file_path}")

    # Construct the command to run preferences_manager.exe
    command = f'"{preferences_manager_path}" -u={user} -pf="{password_file_path}" -g={group} -mode={mode} -action={action} -file="{xml_file_path}"'
    logging.info(f"Constructed command: {command}")

    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, shell=True, text=True)

        # Log the result of the command execution
        if result.returncode == 0:
            logging.info(f"Command executed successfully for {xml_file}!")
            logging.info(f"Command output:\n{result.stdout}")
        else:
            logging.error(f"Error executing the command for {xml_file}: {result.stderr}")
    except FileNotFoundError as e:
        logging.error(f"Error running the command for {xml_file}: {e}")

# Function to set environment variable and process XML files
def set_environment_variable_from_bat(bat_file_path, preferences_manager_path, user, password_file_name, group, mode, action, preferences_folder, log_file):
    """Execute the batch file to set TC_ROOT environment variable and then call preferences_manager for each XML file."""
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

    # Loop through all XML files in the preferences folder
    try:
        # List all XML files in the preferences folder
        xml_files = [f for f in os.listdir(preferences_folder) if f.endswith(".xml")]
        logging.info(f"Found XML files: {xml_files}")

        # Run the command for each XML file
        for xml_file in xml_files:
            logging.info(f"Processing {xml_file}...")
            run_preferences_manager(tc_root, preferences_manager_path, user, password_file_name, group, mode, action, log_file, xml_file)

    except Exception as e:
        logging.error(f"Error processing XML files: {e}")

# Main function to parse arguments and execute the workflow
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
