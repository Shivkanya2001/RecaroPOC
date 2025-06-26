import os
import sys
import subprocess
import logging
import argparse

# Setup logging configuration
log_file = "deployment_log.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Teamcenter Preference Loader Script")
parser.add_argument("-u", type=str, required=True, help="The username of Teamcenter.")
parser.add_argument("-g", type=str, required=True, help="The group of Teamcenter.")
parser.add_argument("-pwf_file", type=str, required=True, help="The password file name (e.g., tc_user.pwf)")
parser.add_argument("-mode", type=str, required=True, help="The mode of the preference operation (e.g., import).")
parser.add_argument("-scope", type=str, required=True, help="The scope of the preference (e.g., site).")
parser.add_argument("-action", type=str, required=True, help="The action to perform (e.g., replace, merge).")
parser.add_argument("-profile", type=str, required=True, help="Path to profilevars file to extract TC_ROOT and TC_DATA")
args = parser.parse_args()

# Function to read TC_ROOT and TC_DATA from profilevars
def get_tc_env_from_profile(profile_path):
    """Reads the TC_ROOT and TC_DATA from the profilevars file."""
    if not os.path.exists(profile_path):
        logging.error(f"Profilevars file not found: {profile_path}")
        sys.exit(1)

    tc_root, tc_data = None, None
    with open(profile_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.lower().startswith("set tc_root"):
                tc_root = line.split("=", 1)[1].strip().strip('"')
            elif line.lower().startswith("set tc_data"):
                tc_data = line.split("=", 1)[1].strip().strip('"')

    if not tc_root or not tc_data:
        logging.error("Could not extract TC_ROOT and TC_DATA from profilevars.")
        sys.exit(1)

    # Set the environment variables directly in Python
    os.environ['TC_ROOT'] = tc_root
    os.environ['TC_DATA'] = tc_data

    logging.info(f"Set TC_ROOT: {tc_root}")
    logging.info(f"Set TC_DATA: {tc_data}")

    return tc_root, tc_data

# Function to get the full path for the .pwf file
def get_pwf_file_path(tc_root, pwf_filename):
    """Constructs the full path for the .pwf file."""
    pwf_path = os.path.join(tc_root, "security", pwf_filename)
    if not os.path.exists(pwf_path):
        logging.error(f".pwf file not found: {pwf_path}")
        sys.exit(1)
    return pwf_path

# Log initialization
logging.info("Starting Teamcenter Preference Loader Script")

# Step 1: Load TC_ROOT and TC_DATA from profilevars
TC_ROOT, TC_DATA = get_tc_env_from_profile(args.profile)

# Step 2: Set paths and preferences manager executable path
folder_path = "preferences"  # Folder with preference XML files
target_directory = os.path.join(TC_ROOT, "bin")
preferences_manager_path = os.path.join(target_directory, "preferences_manager.exe")

# Step 3: Ensure the preferences_manager.exe exists
if not os.path.exists(preferences_manager_path):
    logging.error(f"'preferences_manager.exe' not found at: {preferences_manager_path}")
    sys.exit(1)

# Step 4: Process each file in the preferences folder
try:
    # Verify the preferences folder exists
    if not os.path.exists(folder_path):
        logging.error(f"The folder '{folder_path}' does not exist.")
        sys.exit(1)

    # Resolve the full path to the .pwf file
    pwf_path = get_pwf_file_path(TC_ROOT, args.pwf_file)

    # Loop through each file in the preferences folder
    for filename in os.listdir(folder_path):
        full_path = os.path.join(folder_path, filename)

        if os.path.isfile(full_path):
            logging.info(f"Processing file: {full_path}")

            # Construct the command string for preferences_manager.exe
            command = (
                f'"{preferences_manager_path}" '
                f'-u={args.u} '
                f'-pwf_file="{pwf_path}" '
                f'-g={args.g} '
                f'-mode={args.mode} '
                f'-scope={args.scope} '
                f'-action={args.action} '
                f'-file="{full_path}"'
            )

            try:
                # Run the command using subprocess
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    cwd=target_directory,
                    capture_output=True,
                    text=True,
                    check=True
                )
                logging.info(f"Command succeeded for {filename}: {result.stdout}")

            except subprocess.CalledProcessError as e:
                logging.error(f"Command failed for {filename} with return code {e.returncode}")
                logging.error(f"Output: {e.output}")
                logging.exception("Exception details:")

except FileNotFoundError as fnf_error:
    logging.error(f"File Not Found Error: {fnf_error}")

except Exception as e:
    logging.error(f"Unexpected error occurred: {str(e)}")
    logging.exception("Exception details:")
