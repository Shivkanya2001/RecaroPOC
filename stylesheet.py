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
    log_file = os.path.join(os.getcwd(), f"stylesheet_import_{timestamp}.log")

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


def validate_environment(install_user, install_group, tc_root):
    if not install_user or not install_group or not tc_root:
        logging.error("Missing required configuration: INSTALL_USER, INSTALL_GROUP, or TC_ROOT")
        sys.exit(1)

    exe_path = os.path.join(tc_root, "bin", "install_xml_stylesheet_datasets.exe")
    if not os.path.exists(exe_path):
        logging.error("install_xml_stylesheet_datasets executable not found in expected path:")
        logging.error(exe_path)
        sys.exit(1)

    return exe_path


def find_pwf_file(tc_root, pwf_filename):
    pwf_path = os.path.join(tc_root, "security", pwf_filename)
    if not os.path.exists(pwf_path):
        logging.error(f".pwf file not found inside TC_ROOT/security: {pwf_path}")
        sys.exit(1)
    logging.info(f"Using password file at: {pwf_path}")
    return pwf_path


def collect_xml_files(source_dir):
    xml_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.xml') and file != "build.xml":
                xml_files.append(os.path.join(root, file))
    return xml_files


def prepare_input_file(xml_files, staging_dir, input_file_path, backup_old=True):
    try:
        os.makedirs(staging_dir, exist_ok=True)

        if backup_old and os.path.exists(input_file_path):
            shutil.move(input_file_path, input_file_path + ".bak")
            logging.info(f"Backed up old input file to {input_file_path}.bak")

        with open(input_file_path, 'w', encoding='utf-8') as input_file:
            for file_path in xml_files:
                filename = Path(file_path).name
                dataset_name = Path(file_path).stem
                staged_path = os.path.join(staging_dir, filename)
                shutil.copy(file_path, staged_path)
                input_file.write(f"{dataset_name}, {filename}\n")

        logging.info(f"Input file prepared at: {input_file_path}")
        return True
    except Exception as e:
        logging.error(f"Error preparing input file: {e}")
        return False


def import_stylesheets(exe_path, install_user, install_pwf, install_group, input_file, staging_dir, tc_bat_path):
    # Construct command string to run batch file first, then exe with arguments
    command = f'cmd /c "{tc_bat_path} && "{exe_path}" -u={install_user} -pf={install_pwf} -g={install_group} -input={input_file} -filepath={staging_dir} -replace"'

    logging.info(f"Prepared command: {command}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            logging.info(f"Command STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"Command STDERR:\n{result.stderr}")
            logging.info("Stylesheet import completed successfully.")
        else:
            logging.error(f"Import failed with return code {result.returncode}")
            logging.error(f"STDOUT:\n{result.stdout}")
            logging.error(f"STDERR:\n{result.stderr}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to run the import command: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Import XML Stylesheets to Teamcenter.")
    parser.add_argument("-target-path", type=str, required=True, help="Directory containing stylesheet XMLs (searched recursively).")
    parser.add_argument("-pwf-file", type=str, required=True, help=".pwf file name (inside TC_ROOT/security)")
    parser.add_argument("-install-user", type=str, required=True, help="Install user")
    parser.add_argument("-install-group", type=str, required=True, help="Install group")
    parser.add_argument("-tc-bat", type=str, required=True, help="Path to batch file to set TC environment")
    args = parser.parse_args()
    setup_logger()

    logging.info("Starting XML Stylesheet Import Process...")
    tc_root = run_tc_bat_file_and_capture_env(args.tc_bat)

    install_user = args.install_user
    install_group = args.install_group
    install_pwf = find_pwf_file(tc_root, args.pwf_file)
    exe_path = validate_environment(install_user, install_group, tc_root)

    TEMP_DIR = os.getenv('TEMP', '/tmp')
    WORK_DIR = os.path.join(TEMP_DIR, 'stylesheet_import')
    STAGING_DIR = os.path.join(WORK_DIR, 'xml_files')
    INPUT_FILE = os.path.join(os.getcwd(), 'input.txt')

    xml_files = collect_xml_files(args.target_path)
    if not xml_files:
        logging.error("No XML files found to import.")
        sys.exit(1)

    logging.info(f"Found {len(xml_files)} XML files to process.")

    if not prepare_input_file(xml_files, STAGING_DIR, INPUT_FILE):
        sys.exit(1)

    import_stylesheets(
        exe_path,
        install_user,
        install_pwf,
        install_group,
        INPUT_FILE,
        STAGING_DIR,
        args.tc_bat
    )

    logging.info("Script completed successfully.")


if __name__ == "__main__":
    main()
