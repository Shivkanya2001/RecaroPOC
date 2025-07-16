import os
import sys
import subprocess
import argparse
import logging
from datetime import datetime

def setup_logger():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(os.getcwd(), f"bmide_generate_{timestamp}.log")

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

    return tc_root, tc_data

def build_bmide_generate_package_path(tc_root, bmide_generate_package_name):
    bmide_generate_package_name = bmide_generate_package_name.replace("/", "\\")
    resolved_path = os.path.join(tc_root, "bin", bmide_generate_package_name)
    logging.info(f"Constructed bmide_generate_package path: {resolved_path}")
    return resolved_path

def build_dynamic_paths(tc_root, tc_data, workspace_folder_name):
    workspace_folder_name = workspace_folder_name.replace("/", "\\")
    if not workspace_folder_name.lower().startswith("bmide\\workspace"):
        workspace_folder_name = os.path.join("bmide", "workspace", workspace_folder_name)

    project_location = os.path.join(tc_root, workspace_folder_name)
    package_location = os.path.join(project_location, "output")
    code_generation_folder = os.path.join(package_location, "wntx64")
    dependency_template_folder = os.path.join(tc_data, "model")
    log_file = os.path.join(package_location, "bmide_generate.log")

    logging.info(f"Resolved projectLocation: {project_location}")
    logging.info(f"Resolved packageLocation: {package_location}")
    logging.info(f"Resolved codeGenerationFolder: {code_generation_folder}")
    logging.info(f"Resolved dependencyTemplateFolder: {dependency_template_folder}")
    logging.info(f"Resolved logFile: {log_file}")

    return project_location, package_location, code_generation_folder, dependency_template_folder, log_file

def bmide_generate_package(bat_file_path, bmide_generate_package_path, projectLocation, packageLocation,
                           dependencyTemplateFolder, codeGenerationFolder, softwareVersion, buildVersion,
                           allPlatform, log_file):
    command = (
        f'"{bat_file_path}" && "{bmide_generate_package_path}" '
        f'-projectLocation="{projectLocation}" '
        f'-packageLocation="{packageLocation}" '
    )

    if dependencyTemplateFolder:
        command += f'-dependencyTemplateFolder="{dependencyTemplateFolder}" '

    if codeGenerationFolder:
        command += f'-codeGenerationFolder="{codeGenerationFolder}" '

    if softwareVersion:
        command += f'-softwareVersion="{softwareVersion}" '

    if buildVersion:
        command += f'-buildVersion="{buildVersion}" '

    if allPlatform:
        command += '-allPlatform '

    if log_file:
        command += f'-log="{log_file}" '

    logging.info(f"Constructed command: {command}")

    try:
        result = subprocess.run(command, capture_output=True, shell=True, text=True)
        if result.returncode == 0:
            logging.info("Successfully executed BMIDE generate package command.")
            logging.info(f"stdout:\n{result.stdout}")
        else:
            logging.error("Command failed.")
            logging.error(f"stderr:\n{result.stderr}")
            logging.error(f"stdout:\n{result.stdout}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Exception occurred while executing command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="BMIDE package generation script")

    # Positional (required) argument
    parser.add_argument("bmide_generate_package", type=str, help="Executable name only, e.g., 'bmide_generate_package.exe'")

    # Optional but required flags
    parser.add_argument("-tc_bat", type=str, required=True, help="Path to batch file to set TC environment")
    parser.add_argument("-workspace_folder_name", type=str, required=True, help="Name or relative path, e.g., 't5recaro' or 'bmide\\workspace\\t5recaro'")
    parser.add_argument("-softwareVersion", type=str, help="Software version")
    parser.add_argument("-buildVersion", type=str, help="Build version")
    parser.add_argument("-allPlatform", action='store_true', help="Flag to include all platforms")

    args = parser.parse_args()

    setup_logger()
    logging.info("Starting BMIDE package generation process...")

    # Get TC_ROOT and TC_DATA from environment
    tc_root, tc_data = run_tc_bat_file_and_capture_env(args.tc_bat)

    # Always construct bmide_generate_package path under TC_ROOT\bin
    bmide_generate_package_path = build_bmide_generate_package_path(tc_root, args.bmide_generate_package)

    # Dynamically build workspace-related paths
    projectLocation, packageLocation, codeGenerationFolder, dependencyTemplateFolder, log_file = build_dynamic_paths(
        tc_root, tc_data, args.workspace_folder_name)

    # Run BMIDE package generation
    bmide_generate_package(
        args.tc_bat,
        bmide_generate_package_path,
        projectLocation,
        packageLocation,
        dependencyTemplateFolder,
        codeGenerationFolder,
        args.softwareVersion,
        args.buildVersion,
        args.allPlatform,
        log_file
    )

    logging.info("Build process completed successfully.")

if __name__ == "__main__":
    main()
