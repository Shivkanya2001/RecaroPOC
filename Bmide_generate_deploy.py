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

def run_tc_env_and_get_tcroot(tc_bat):
    logging.info(f"Running batch file to get TC_ROOT and TC_DATA: {tc_bat}")
    process = subprocess.run(f'cmd /c "{tc_bat} && set"', capture_output=True, shell=True, text=True)
    if process.returncode != 0:
        logging.error("Failed to execute tc_env.bat")
        logging.error(process.stderr)
        sys.exit(1)

    tc_root = None
    for line in process.stdout.splitlines():
        if line.startswith("TC_ROOT="):
            tc_root = line.split("=", 1)[1].strip()

    if not tc_root:
        logging.error("Could not extract TC_ROOT from batch file output.")
        sys.exit(1)

    logging.info(f"Resolved TC_ROOT: {tc_root}")
    return tc_root

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
        f'"{tem_bat}" -update -templates={template_name} -full '
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
    parser = argparse.ArgumentParser(description="Dynamic BMIDE template updater (reads TC_ROOT from bat file)")
    parser.add_argument("-tc_bat", required=True, help="Path to tc_env.bat file to set TC_ROOT")
    parser.add_argument("-template", required=True, help="Template name (e.g., t5recaro)")
    parser.add_argument("-pf_file", required=True, help="Password filename inside security folder (e.g., config1_infodba.pwf)")
    parser.add_argument("-platform", default="wntx64", help="Platform name, default=wntx64")
    parser.add_argument("-version", required=True, help="Template version (e.g., 1.0_2412)")
    parser.add_argument("-fullkit_path", required=True, help="Path to fullkit directory (e.g., D:\\tc2412_wntx64)")

    args = parser.parse_args()
    setup_logger()

    tc_root = run_tc_env_and_get_tcroot(args.tc_bat)

    command = build_command(
        tc_root, args.template, args.pf_file, args.platform, args.version, args.fullkit_path
    )
    run_command(command)

if __name__ == "__main__":
    main()
