import os
import sys
import subprocess
import logging
import argparse
import tempfile

# Setup logging
log_file = "deployment_log.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode='w'
)

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Teamcenter Preference Loader Script")
parser.add_argument("-u", required=True, help="Teamcenter username")
parser.add_argument("-g", required=True, help="Teamcenter group")
parser.add_argument("-pf", dest="pwf_file", required=True, help="Password file name (e.g., config1_infodba.pwf)")
parser.add_argument("-mode", required=True, help="Preference mode (e.g., import)")
parser.add_argument("-scope", required=True, help="Preference scope (e.g., SITE)")
parser.add_argument("-action", required=True, help="Preference action (e.g., OVERRIDE)")
parser.add_argument("-profile", required=True, help="Path to tc_DEVBOX.bat or equivalent")
args = parser.parse_args()

# --- Load TC_ROOT and TC_DATA from .bat file ---
def extract_env_from_bat(bat_file_path):
    if not os.path.isfile(bat_file_path):
        logging.error(f"Profile batch file not found: {bat_file_path}")
        sys.exit(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bat", mode='w', encoding='utf-8') as temp_bat:
        temp_bat.write(f'@echo off\n')
        temp_bat.write(f'call "{bat_file_path}"\n')
        temp_bat.write(f'set TC_ROOT\n')
        temp_bat.write(f'set TC_DATA\n')

    result = subprocess.run(
        ['cmd.exe', '/c', temp_bat.name],
        capture_output=True,
        text=True,
        shell=False
    )

    os.unlink(temp_bat.name)

    tc_root, tc_data = None, None
    for line in result.stdout.splitlines():
        if line.startswith("TC_ROOT="):
            tc_root = line.split("=", 1)[1].strip()
        elif line.startswith("TC_DATA="):
            tc_data = line.split("=", 1)[1].strip()

    if not tc_root or not tc_data:
        logging.error("TC_ROOT or TC_DATA not found in the profile batch file.")
        sys.exit(1)

    logging.info(f"Loaded TC_ROOT: {tc_root}")
    logging.info(f"Loaded TC_DATA: {tc_data}")
    return tc_root, tc_data

# --- Load Environment ---
TC_ROOT, TC_DATA = extract_env_from_bat(args.profile)

# --- Set Executable and .pwf file paths ---
preferences_manager = os.path.join(TC_ROOT, "bin", "preferences_manager.exe")
pwf_path = os.path.join(TC_ROOT, "security", args.pwf_file)
preferences_folder = "preferences"

if not os.path.isfile(preferences_manager):
    logging.error(f"preferences_manager.exe not found: {preferences_manager}")
    sys.exit(1)

if not os.path.isfile(pwf_path):
    logging.error(f".pwf file not found: {pwf_path}")
    sys.exit(1)

if not os.path.isdir(preferences_folder):
    logging.error(f"Preferences folder not found: {preferences_folder}")
    sys.exit(1)

# --- Set environment for subprocess ---
env_vars = os.environ.copy()
env_vars['TC_ROOT'] = TC_ROOT
env_vars['TC_DATA'] = TC_DATA

# --- Process preference XML files ---
for filename in os.listdir(preferences_folder):
    if filename.endswith(".xml"):
        file_path = os.path.join(preferences_folder, filename)

        command = [
            preferences_manager,
            f"-u={args.u}",
            f"-pf={pwf_path}",
            f"-g={args.g}",
            f"-mode={args.mode}",
            f"-scope={args.scope}",
            f"-action={args.action}",
            f"-file={file_path}"
        ]

        logging.info(f"Executing command: {' '.join(command)}")

        try:
            result = subprocess.run(command, env=env_vars, capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"Success: {filename}")
                logging.debug(result.stdout)
            else:
                logging.error(f"Error importing {filename}:\n{result.stderr}")
        except Exception as e:
            logging.exception(f"Exception during execution for {filename}: {str(e)}")




























