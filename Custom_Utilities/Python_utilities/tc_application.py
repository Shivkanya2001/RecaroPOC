import os
import subprocess
import shutil
import logging
from datetime import datetime
import argparse

# Setup logger to track the build and deployment process
def setup_logger():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(os.getcwd(), f"Deployment_{timestamp}.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(console_handler)

    return log_file

# Step 1: Set up Visual Studio environment using vcvarsall.bat
# Step 1: Set up Visual Studio environment using vcvarsall.bat
def setup_visual_studio_env():
    vcvars_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"
    
    if not os.path.exists(vcvars_path):
        logging.error(f"vcvarsall.bat not found at {vcvars_path}")
        return False
    
    # Check if we're running in PowerShell or CMD
    if os.name == 'nt':  # Check if we are on Windows
        if 'powershell' in os.environ.get('SHELL', '').lower():
            # PowerShell: Use call operator (&) for PowerShell compatibility
            process = subprocess.run([f'& "{vcvars_path}" x64'], shell=True, capture_output=True, text=True)
        else:
            # CMD: Standard command execution for CMD
            process = subprocess.run([vcvars_path, "x64"], shell=True, capture_output=True, text=True)

    if process.returncode != 0:
        logging.error(f"Failed to set up Visual Studio environment. Error: {process.stderr}")
        return False
    
    logging.info("Visual Studio environment set up successfully.")
    return True

# Step 2: Extract TC_ROOT from the tcvar.bat or tcvar file
def extract_tc_root(tc_bat_path):
    if not os.path.exists(tc_bat_path):
        logging.error(f"tcvar.bat file not found at {tc_bat_path}")
        return None

    # Run tcvar.bat to extract TC_ROOT
    process = subprocess.run([tc_bat_path], shell=True, capture_output=True, text=True)

    if process.returncode != 0:
        logging.error(f"Failed to run tcvar.bat. Error: {process.stderr}")
        return None

    # Extract TC_ROOT value from the output of tcvar.bat
    for line in process.stdout.splitlines():
        if "TC_ROOT=" in line:
            tc_root = line.split("=", 1)[1].strip()
            logging.info(f"TC_ROOT extracted: {tc_root}")
            return tc_root

    logging.error("TC_ROOT not found in tcvar.bat output.")
    return None

# Step 3: Build the ITK Project
def build_itk_project(project_dir):
    logging.info(f"Building ITK project at {project_dir}")

    # Automatically derive the project name from the folder name
    project_name = os.path.basename(project_dir)

    solution_path = os.path.join(project_dir, f"{project_name}.sln")

    if not os.path.exists(solution_path):
        logging.error(f"Solution file {project_name}.sln not found in the project folder.")
        return None

    # MSBuild command to build the project
    msbuild_command = f'msbuild "{solution_path}" /p:Configuration=Release /p:Platform=x64'

    # Run MSBuild to build the project
    process = subprocess.run(msbuild_command, capture_output=True, shell=True, text=True)

    if process.returncode != 0:
        logging.error(f"Build failed for {project_name}")
        logging.error(process.stderr)
        return None

    logging.info(f"Build completed successfully for {project_name}")

    # Assuming the .exe is located in the project's x64/Release folder
    exe_path = os.path.join(project_dir, "x64", "Release", f"{project_name}.exe")
    if os.path.exists(exe_path):
        logging.info(f".exe file generated: {exe_path}")
        return exe_path
    else:
        logging.error(f".exe file not found in: {exe_path}")
        return None

# Step 4: Deploy the generated .exe to the bin folder
def deploy_exe_to_bin(exe_path, bin_folder):
    logging.info(f"Deploying .exe to {bin_folder}")

    # Ensure the bin folder exists
    os.makedirs(bin_folder, exist_ok=True)

    # Move the .exe file to the bin folder
    try:
        shutil.copy(exe_path, bin_folder)
        logging.info(f"Successfully deployed {exe_path} to {bin_folder}")
        return True
    except Exception as e:
        logging.error(f"Failed to deploy .exe to bin folder: {e}")
        return False

# Main execution
def main():
    # Setup argparse for command line arguments
    parser = argparse.ArgumentParser(description="Build and deploy ITK project.")
    parser.add_argument("--target-path", required=True, help="Path to the ITK project folder")
    parser.add_argument("--tc-bat", required=True, help="Path to tcvar.bat or file to extract TC_ROOT")

    args = parser.parse_args()

    setup_logger()

    # Step 1: Check if the ITK project folder exists
    if not os.path.exists(args.target_path):
        logging.error(f"Deployment failed: Folder does not exist: {args.target_path}")
        return

    # Step 2: Extract TC_ROOT using tcvar.bat
    tc_root = extract_tc_root(args.tc_bat)
    if not tc_root:
        logging.error("Deployment failed: TC_ROOT extraction failed.")
        return

    # Step 3: Construct the bin folder path based on TC_ROOT
    bin_folder = os.path.join(tc_root, "bin")
    logging.info(f"Bin folder path: {bin_folder}")

    # Step 4: Set up Visual Studio environment
    if not setup_visual_studio_env():
        logging.error("Deployment failed: Visual Studio environment setup failed.")
        return

    # Step 5: Build the ITK project (no need to pass project name anymore)
    exe_path = build_itk_project(args.target_path)
    if not exe_path:
        logging.error("Build failed, .exe not generated.")
        return

    # Step 6: Deploy the .exe to the bin folder
    if not deploy_exe_to_bin(exe_path, bin_folder):
        logging.error("Deployment failed.")
        return

    logging.info("Project successfully built and deployed!")

if __name__ == "__main__":
    main()
