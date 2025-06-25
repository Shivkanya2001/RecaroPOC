import os
import subprocess
import logging
import argparse

# Set up logging configuration with overwrite mode
log_file = "deployment_log.log"  # Log file name

# Initialize ArgumentParser
parser = argparse.ArgumentParser(description="A simple script that demonstrates argparse.")

# Add arguments
parser.add_argument("-u", type=str, help="The username of tc.")
parser.add_argument("-g", type=str, help="The group of tc.")
parser.add_argument("-p", type=str, help="The password file path")  # Password file path
parser.add_argument("-mode", type=str, help="The mode of the file")
parser.add_argument("-scope", type=str, help="The scope of the file")
parser.add_argument("-action", type=str, help="The action of the file")

# Parse arguments
args = parser.parse_args()

# Set up logging configuration
logging.basicConfig(
    filename=log_file,  # Save logs to this file
    level=logging.DEBUG,  # Capture all log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format with timestamp, log level, and message
    filemode='w'  # Overwrite the log file every time the script is run
)

folder_path = r"preferences"  # Folder containing preferences XML files
target_directory = r"D:/apps/siemens/tc_root/bin"  # Teamcenter bin directory

def read_password_from_file(password_file):
    """Read the password from a file."""
    try:
        with open(password_file, 'r') as file:
            return file.read().strip()  # Read the content and remove any trailing newlines/whitespaces
    except Exception as e:
        logging.error(f"Error reading password file {password_file}: {e}")
        raise

try:
    # Verify if the preferences folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")
    
    logging.info(f"Folder path: {folder_path}")  # Log folder path
    logging.info(f"Target directory: {target_directory}")  # Log target directory

    # Check if the password file path is provided
    if args.p:
        password = read_password_from_file(args.p)
    else:
        raise ValueError("Password file path (-p) is required.")
    
    # Loop through the files in the folder
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        # Check if it's a file (skip directories)
        if os.path.isfile(full_path):
            logging.info(f"Processing file: {full_path}")  # Log the file being processed

            # Construct the full file path (absolute path) and include it in the command
            absolute_file_path = os.path.abspath(full_path)
            logging.info(f"Absolute file path: {absolute_file_path}")  # Log absolute path for debugging

            # Prepare the command with string formatting
            preferences_manager_path = r"D:/apps/siemens/tc_root/bin/preferences_manager.exe"
            command = f"{preferences_manager_path} -u={args.u} -p={password} -g={args.g} -mode={args.mode} -scope={args.scope} -action={args.action} -file={absolute_file_path}"

            try:
                # Run the command using subprocess, setting the working directory to the target directory
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    cwd=target_directory,  # Use the correct working directory for preferences_manager.exe
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Log the result (stdout of the command)
                logging.info(f"Command executed successfully for {absolute_file_path}: {result.stdout}")

            except subprocess.CalledProcessError as e:
                # Log error if the command fails
                logging.error(f"Error: Command failed for {absolute_file_path} with return code {e.returncode}. Output: {e.output}")
                logging.error(f"Error Details: {e.stderr}")  # Log stderr for additional information
                logging.exception(f"Exception details for {absolute_file_path}: {str(e)}")

except FileNotFoundError as fnf_error:
    # Log specific FileNotFoundError
    logging.error(f"File Not Found Error: {fnf_error}")

except Exception as e:
    # Log general exception
    logging.error(f"Error occurred: {str(e)}")
    logging.exception("Exception details:")
