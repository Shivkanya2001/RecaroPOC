import subprocess
import sys
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Log to stdout for Jenkins
)

def list_services():
    # PowerShell command to list services on the local machine
    command = """
    Get-Service | Select-Object -Property Name, Status, DisplayName
    """
    
    try:
        # Run the PowerShell command locally and capture the output
        logging.info("Fetching list of services from local machine...")
        result = subprocess.run(
            ["powershell", "-Command", command],
            check=True,
            capture_output=True,
            text=True
        )
        
        services = result.stdout.strip().split("\n")
        logging.info("Services fetched successfully.")

        # Logging service details
        logging.info(f"{'Service Name':<40}{'Display Name':<50}{'Status':<15}")
        logging.info("-" * 120)

        # Regex pattern to capture Name, Status, and DisplayName
        pattern = re.compile(r"^(?P<name>\S+)\s+(?P<status>\S+)\s+(?P<display_name>.+)$")

        for service in services:
            # Try matching the service line
            match = pattern.match(service.strip())
            if match:
                service_info = match.groupdict()
                logging.info(f"{service_info['name']:<40}{service_info['display_name']:<50}{service_info['status']:<15}")
            else:
                logging.warning(f"Skipping invalid service format: {service}")
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list services. Error: {e}")
        logging.error("Output: %s", e.output)
        logging.error("Error: %s", e.stderr)
        sys.exit(1)

def main():
    logging.info("Starting the service listing process.")
    list_services()

if __name__ == "__main__":
    main()
