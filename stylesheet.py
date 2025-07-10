import os
import subprocess
import argparse
import logging
import shutil
from pathlib import Path

# Configure logging
logfilename = f"stylesheet_import_{Path.cwd().name}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logfilename),
        logging.StreamHandler()
    ]
)

# Get environment variables (fallback if needed)
TC_ROOT = os.getenv('TC_ROOT')
INSTALL_USER = os.getenv('INSTALL_USER')
INSTALL_GROUP = os.getenv('INSTALL_GROUP')

def validate_environment(install_user, install_group, tc_root):
    if not install_user or not install_group or not tc_root:
        logging.error("Missing required configuration: INSTALL_USER, INSTALL_GROUP, or TC_ROOT")
        exit(1)
    if shutil.which("install_xml_stylesheet_datasets") is None:
        logging.error("install_xml_stylesheet_datasets executable not found in PATH")
        exit(1)

def find_pwf_file(tc_root, pwf_filename):
    pwf_path = os.path.join(tc_root, "security", pwf_filename)
    if not os.path.exists(pwf_path):
        logging.error(f".pwf file not found: {pwf_path}")
        exit(1)
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

def import_stylesheets(install_user, install_pwf, install_group, input_file, staging_dir, replace=True, dry_run=False):
    command = [
        "install_xml_stylesheet_datasets",
        f"-u={install_user}",
        f"-pf={install_pwf}",
        f"-g={install_group}",
        f"-input={input_file}",
        f"-filepath={staging_dir}"
    ]
    if replace:
        command.append("-replace")

    logging.info(f"Prepared command: {' '.join(command)}")

    if dry_run:
        logging.info("Dry-run mode enabled. Command not executed.")
        return

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info(f"Command STDOUT:\n{result.stdout}")
        if result.stderr:
            logging.warning(f"Command STDERR:\n{result.stderr}")
        logging.info("Stylesheet import completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Import failed with return code {e.returncode}")
        logging.error(f"STDOUT:\n{e.stdout}")
        logging.error(f"STDERR:\n{e.stderr}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Import XML Stylesheets to Teamcenter.")
    parser.add_argument("--target-path", type=str, required=True, help="Directory containing stylesheet XMLs (searched recursively).")
    parser.add_argument("--pwf-file", type=str, required=True, help=".pwf file name (inside TC_ROOT/security)")
    parser.add_argument("--install-user", type=str, default=INSTALL_USER, help="Install user (fallback if not set in env)")
    parser.add_argument("--install-group", type=str, default=INSTALL_GROUP, help="Install group (fallback if not set in env)")
    parser.add_argument("--no-replace", action='store_true', help="Do not use -replace (skip existing datasets)")
    parser.add_argument("--dry-run", action='store_true', help="Simulate run without executing import command")

    args = parser.parse_args()
    install_user = args.install_user
    install_group = args.install_group

    validate_environment(install_user, install_group, TC_ROOT)
    install_pwf = find_pwf_file(TC_ROOT, args.pwf_file)

    # Define working directories
    TEMP_DIR = os.getenv('TEMP', '/tmp')
    WORK_DIR = os.path.join(TEMP_DIR, 'stylesheet_import')
    STAGING_DIR = os.path.join(WORK_DIR, 'xml_files')
    INPUT_FILE = os.path.join(os.getcwd(), 'input.txt')  # <-- generate in current directory

    xml_files = collect_xml_files(args.target_path)
    if not xml_files:
        logging.error("No XML files found to import.")
        exit(1)

    logging.info(f"Found {len(xml_files)} XML files to process.")

    if not prepare_input_file(xml_files, STAGING_DIR, INPUT_FILE):
        exit(1)

    import_stylesheets(install_user, install_pwf, install_group, INPUT_FILE, STAGING_DIR, replace=not args.no_replace, dry_run=args.dry_run)

if __name__ == "__main__":
    logging.info("Starting XML Stylesheet Import Process...")
    main()
    logging.info("Script completed successfully.")
