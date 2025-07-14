import os
import sys
import subprocess
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime


def setup_logger():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(os.getcwd(), f"Aws_Manager_Build_{timestamp}.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(console_handler)

    return log_file


def run_tc_bat_file_and_capture_env(bat_file_path):
    logging.info(f"Running batch file to set TC_ROOT and TC_DATA: {bat_file_path}")
    # Run the batch file and then 'set' to capture environment variables it sets
    process = subprocess.run(f'cmd /c "{bat_file_path} && set"', capture_output=True, shell=True, text=True)

    if process.returncode != 0:
        logging.error("Failed to execute batch file.")
        logging.error(process.stderr)
        sys.exit(1)

    tc_root = None
    tc_data = None

    for line in process.stdout.splitlines():
        if line.startswith("TC_ROOT="):
            tc_root = line.split("=", 1)[1].strip()
        elif line.startswith("TC_DATA="):
            tc_data = line.split("=", 1)[1].strip()

    if not tc_root or not tc_data:
        logging.error("Could not extract TC_ROOT or TC_DATA from batch file output.")
        sys.exit(1)

    os.environ['TC_ROOT'] = tc_root
    os.environ['TC_DATA'] = tc_data
    logging.info(f"Set TC_ROOT={tc_root}")
    logging.info(f"Set TC_DATA={tc_data}")

    return tc_root


def validate_environment(tc_root, target_path):
    if not tc_root:
        logging.error("Missing required configuration: TC_ROOT")
        sys.exit(1)

    stage_path = os.path.join(tc_root, "aws2", "stage")

    if not os.path.exists(stage_path):
        logging.error("The aws stage folder does not exist:")
        logging.error(stage_path)
        sys.exit(1)

    if not os.path.exists(target_path):
        logging.error("The target folder does not exist:")
        logging.error(target_path)
        sys.exit(1)

    if not os.path.isdir(target_path):
        logging.error("The target path exists but is not a directory:")
        logging.error(target_path)
        sys.exit(1)

    logging.info(f"Validation successful: TC_ROOT={tc_root}, TARGET_PATH={target_path}")
    return stage_path

def replace_stage_with_target(stage_path, target_path):
    # Clear stage directory
    logging.info(f"Clearing stage directory: {stage_path}")
    for item in os.listdir(stage_path):
        item_path = os.path.join(stage_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            logging.error(f"Failed to delete {item_path}: {e}")
            sys.exit(1)

    # Copy contents from target_path to stage_path
    logging.info(f"Copying contents from {target_path} to {stage_path}")
    for item in os.listdir(target_path):
        s = os.path.join(target_path, item)
        d = os.path.join(stage_path, item)
        try:
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        except Exception as e:
            logging.error(f"Failed to copy {s} to {d}: {e}")
            sys.exit(1)

    logging.info("Stage folder successfully replaced with target folder contents.")






def main():
    parser = argparse.ArgumentParser(description="Import XML Stylesheets to Teamcenter.")
    parser.add_argument("-target-path", type=str, required=True, help="Directory containing stage folder (searched recursively).")
    parser.add_argument("-tc-bat", type=str, required=True, help="Path to batch file to set TC environment")
    args = parser.parse_args()
    setup_logger()

    logging.info("Starting AWC build  Process...")
    tc_root = run_tc_bat_file_and_capture_env(args.tc_bat)

    exe_path = validate_environment(install_user, install_group, tc_root)


    logging.info(f"Found {len(xml_files)} XML files to process.")

    if not prepare_input_file(xml_files, STAGING_DIR, INPUT_FILE):
        sys.exit(1)

 
    logging.info("Build completed successfully.")


if __name__ == "__main__":
    main()
