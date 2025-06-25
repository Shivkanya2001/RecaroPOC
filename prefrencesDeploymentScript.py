import os
import subprocess
import logging

# Set up logging configuration with overwrite mode
log_file = "deployment_log.log"  # Log file name

logging.basicConfig(
    filename=log_file,  # Save logs to this file
    level=logging.DEBUG,  # Capture all log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format with timestamp, log level, and message
    filemode='w'  # Overwrite the log file every time the script is run
)

folder_path = r"preferences"  # Folder containing preferences XML files
target_directory = r"D:/SOFT/Teamcenter13/TC_ROOT/bin"  # Teamcenter bin directory

try:
    # Verify if the preferences folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")
    
    logging.info(f"Folder path: {folder_path}")  # Log folder path
    logging.info(f"Target directory: {target_directory}")  # Log target directory

    # Loop through the files in the folder
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        # Check if it's a file (skip directories)
        if os.path.isfile(full_path):
            logging.info(f"Processing file: {full_path}")  # Log the file being processed

            # Prepare the command with string formatting
            command = f"preferences_manager -u=infodba -p=infodba -g=dba -mode=import -scope=SITE -action=OVERWRITE -file={full_path}"

            try:
                # Run the command using subprocess
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    cwd=target_directory,  # Use the raw string path for `cwd`
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Log the result (stdout of the command)
                logging.info(f"Command executed successfully for {full_path}: {result.stdout}")

            except subprocess.CalledProcessError as e:
                # Log error if the command fails
                logging.error(f"Error: Command failed for {full_path} with return code {e.returncode}. Output: {e.output}")
                logging.exception(f"Exception details for {full_path}: {str(e)}")

except FileNotFoundError as fnf_error:
    # Log specific FileNotFoundError
    logging.error(f"File Not Found Error: {fnf_error}")

except Exception as e:
    # Log general exception
    logging.error(f"Error occurred: {str(e)}")
    logging.exception("Exception details:")
