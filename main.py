# Basic imports
import os, sys, logging
# Pathlib for better cross-compatibility in the end
from pathlib import Path
# Program-specific imports
from .project import Project

# Configure logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger()

# Constants
PROJECTS_FILE = "projects.txt"
INSTALLATION_FOLDER = os.getcwd() + "\\minecraft\\wd"
LOADER_TYPE = sys.argv[1]
MC_VERSION = sys.argv[2]

# Set so that projects are not checked twice
checked_projects = set()
checked_project_versions = set()

# Check for PROJECTS_FILE (where Mods etc. are defined)
if not Path(PROJECTS_FILE).exists():
  logger.error(f'Projects file "{PROJECTS_FILE}" not found')
  logger.info('Create the file and paste the project URLs or move it to the correct directory')
  sys.exit(1)

# Read PROJECTS_FILE and create a new project for each valid URL / SLUG / ID
with open(PROJECTS_FILE, 'r') as f:
  project_entries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
for entry in project_entries:
  # Get info
  logger.info(f'Fetching project info for "{entry}"')
  p = Project(entry)

  # Handle errors
  if not p:
    logger.error(f'Error fetching data for "{entry}"! Skipping!')
    continue
  logger.info(f'Found "{p.get_title()}" ({p.get_type().capitalize()})')

  # Skip if project was already visited
  if p.get_id() in checked_projects:
    logger.info(f'"{p.get_title()}" was already visited. Skipping!')
    continue
  # Else: Mark it as visited
  checked_projects.add(p.get_id())
  

  # Version available?
  if not p.has_version(MC_VERSION):
    continue
  version = p.get_version(MC_VERSION, LOADER_TYPE)
  if version is None:
    continue
  checked_project_versions.add(p.get_id() + version['id'])

  p.download(INSTALLATION_FOLDER)
  file_name = p.get_file_name()
  if file_name:
    logger.info(f'Successfully downloaded as "{file_name}"')
  else:
    logger.error(f'Error downloading "{p.get_title()}", version ID "{version['id']}"!')

  # Log dependency count
  dependencies = version.get_req_dependencies()
  if dependencies is None:
    logger.info(f'No dependencies found')
    continue
  logger.info(f'{len(dependencies)} dependencies found for {p.get_title()}')

  # For every dependency
  for i, (d_id, d_version_id) in enumerate(dependencies, 1):
    logger.info(f'Fetching project info for dependency no. {i}')
    d = Project(d_id)
    if not d:
      logger.error(f'Could not fetch data for "{entry}"! Skipping. {p.get_title()} might not work correctly without!')
      continue
    logger.info(f'Dependency "{d.get_title()}" found')
    
    if d_version_id is None:
      if d.get_id() in checked_projects:
        logger.info(f'"{d.get_title()} was already visited. Skipping!')
      if not d.has_version():
        logger.error(f'"{d.get_title()}" might not work correctly without "{d.get_title()}"!')
        continue
      version = d.get_version(MC_VERSION, LOADER_TYPE)
      if version is None:
        logger.error(f'"{d.get_title()}" might not work correctly without "{d.get_title()}"!')
      checked_projects.add(d.get_id())
    else:
      d.set_version(d_version_id)
      version = d.get_version()
      if d.get_id() + version['id'] in checked_project_versions:
        logger.info(f'"{d.get_title()} version ID {version['id']} was already visited. Skipping!')
        continue
      checked_projects.add(d.get_id())
      checked_project_versions.add(d.get_id() + version['id'])
      
    d.download(INSTALLATION_FOLDER)
    file_name = d.get_file_name()
    if file_name:
      logger.info(f'Successfully downloaded as "{file_name}"')
    else:
      logger.error(f'Error downloading "{p.get_title()}", version ID "{version['id']}"!')
        