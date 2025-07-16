import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime

def setup_logger():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(os.getcwd(), f"bmide_update_{timestamp}.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(console_handler)
    return log_file

def build_dynamic_path(tc_root, template_name, platform, version):
    today = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    full_path = os.path.join(
        tc_root, "bmide", "workspace", template_name, "output", platform, "packaging", "full_update",
        f"{template_name}_{platform}_{version}_{today}"
    )
    logging.info(f"Constructed dynamic BMIDE path: {full_path}")
    return full_path

def build_command(tc_root, template_name, pf_file, platform, version, fullkit_path):
    tem_bat = os.path.join(tc_root, "install", "tem.bat")
    pf_file = os.path.join(tc_root, "security", pf_file)

    dynamic_path = build_dynamic_path(tc_root, template_name, platform, version)
    command = (
        f' cmd /c"{tem_bat}" -update -templates={template_name} -full '
        f'-pf="{pf_file}" -verbose '
        f'-path="{dynamic_path}" '
        f'-fullkit="{fullkit_path}"'
    )
    logging.info(f"Constructed command: {command}")
    return command

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, shell=True, text=True)
        if result.returncode == 0:
            logging.info("Command executed successfully.")
            logging.info(f"stdout:\n{result.stdout}")
        else:
            logging.error("Command failed.")
            logging.error(f"stderr:\n{result.stderr}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Dynamic BMIDE template updater")
    parser.add_argument("-tc_root", required=True, help="Path to TC_ROOT directory")
    parser.add_argument("-template", required=True, help="Template name (e.g., t5recaro)")
    parser.add_argument("-pf_file", required=True, help="Path to .pwf password file")
    parser.add_argument("-platform", default="wntx64", help="Platform name, default=wntx64")
    parser.add_argument("-version", required=True, help="Template version (e.g., 1.0_2412)")
    parser.add_argument("-fullkit_path", required=True, help="Path to fullkit directory (e.g., D:\\tc2412_wntx64)")

    args = parser.parse_args()
    setup_logger()

    command = build_command(
        args.tc_root, args.template, args.pf_file, args.platform, args.version, args.fullkit_path
    )
    run_command(command)

if __name__ == "__main__":
    main()
