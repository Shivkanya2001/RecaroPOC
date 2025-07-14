import os
import sys
import subprocess
import argparse
import logging
import shutil
from pathlib import Path
from datetime import datetime
import zipfile


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


def backup_aws2_folder(tc_root):
    aws2_path = os.path.join(tc_root, "aws2")
    if not os.path.exists(aws2_path):
        logging.warning(f"No aws2 folder found at {aws2_path}, skipping backup.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_zip_path = os.path.join(os.path.dirname(aws2_path), f"aws2_backup_{timestamp}.zip")

    logging.info(f"Creating backup of aws2 folder: {backup_zip_path}")
    with zipfile.ZipFile(backup_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(aws2_path):
            for file in files:
                abs_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_file_path, os.path.dirname(aws2_path))
                zipf.write(abs_file_path, rel_path)

    logging.info("Backup completed successfully.")


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


def run_awbuild_in_stage(stage_path):
    awbuild_bat = os.path.join(stage_path, "awbuild.cmd")
    if not os.path.exists(awbuild_bat):
        logging.error(f"'awbuild.bat' not found in stage folder: {awbuild_bat}")
        sys.exit(1)

    logging.info(f"Running awbuild.bat inside: {stage_path}")
    process = subprocess.run(f'cmd /c "{awbuild_bat}"', cwd=stage_path, capture_output=True, text=True, shell=True)

    if process.returncode != 0:
        logging.error("awbuild.bat failed to execute successfully.")
        logging.error(f"STDOUT:\n{process.stdout}")
        logging.error(f"STDERR:\n{process.stderr}")
        sys.exit(1)

    logging.info("awbuild.bat executed successfully.")
    logging.info(f"STDOUT:\n{process.stdout}")
    logging.info(f"STDERR:\n{process.stderr}")


def main():
    parser = argparse.ArgumentParser(description="AWS Stage Manager: Replace stage folder and run awbuild.bat")
    parser.add_argument("-target_path", type=str, required=True, help="Directory containing stage folder contents to copy")
    parser.add_argument("-tc_bat", type=str, required=True, help="Path to batch file to set TC environment")
    args = parser.parse_args()

    setup_logger()
    logging.info("Starting AWS stage manager process...")

    tc_root = run_tc_bat_file_and_capture_env(args.tc_bat)
    backup_aws2_folder(tc_root)
    stage_path = validate_environment(tc_root, args.target_path)
    replace_stage_with_target(stage_path, args.target_path)
    run_awbuild_in_stage(stage_path)

    logging.info("Build process completed successfully.")


if __name__ == "__main__":
    main()
