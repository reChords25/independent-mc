# Basic imports
import os, sys, logging
# Pathlib for better cross-compatibility in the end
from pathlib import Path
# Program-specific imports
from project import Project

# Configure logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger()

# Constants
PROJECTS_FILE = "projects.txt"
INSTALLATION_FOLDER = os.path.join(os.getcwd(), "..", "minecraft", "wd")
LOADER_TYPE = sys.argv[1]
MC_VERSION = sys.argv[2]

# Set so that projects are not checked twice
checked_projects = []
checked_project_versions = []

# Check for PROJECTS_FILE (where Mods etc. are defined)
def check_for_projects_file():
  if not Path(PROJECTS_FILE).exists():
    logger.error(f'Projects file "{PROJECTS_FILE}" not found')
    logger.info('Create the file and paste the project URLs or move it to the correct directory')
    sys.exit(1)

def download_dependencies(p):
  print('')
  # Log dependency count
  dependencies = p.get_req_dependencies()
  if dependencies is None:
    logger.info(f'No dependencies found')
    return
  count = len(dependencies)
  logger.info(f'{count} {'dependency' if count == 1 else 'dependencies'} found for "{p.get_title()}"')

  # For every dependency
  for i, (d_id, d_version_id) in enumerate(dependencies, 1):
    logger.info(f'Fetching project info for dependency no. {i}')
    d = Project(d_id)
    if not d:
      logger.error(f'Could not fetch data for "{entry}"! Skipping. "{p.get_title()}" might not work correctly without!')
      continue
    logger.info(f'Dependency "{d.get_title()}" found')
    
    if d_version_id is None:
      if d.get_id() in checked_projects:
        logger.info(f'"{d.get_title()}" was already visited. Skipping!')
        continue
      if not d.has_version(MC_VERSION):
        logger.error(f'"{d.get_title()}" might not work correctly without "{d.get_title()}"!')
        continue
      version = d.get_version(MC_VERSION, LOADER_TYPE)
      if version is None:
        logger.error(f'"{d.get_title()}" might not work correctly without "{d.get_title()}"!')
      checked_projects.append(d.get_id())
    else:
      d.set_version(d_version_id)
      version = d.get_version(MC_VERSION, LOADER_TYPE)
      if d.get_id() + version['id'] in checked_project_versions:
        logger.info(f'"{d.get_title()}" version ID "{version['id']}" was already visited. Skipping!')
        continue
      checked_projects.append(d.get_id())
      checked_project_versions.append(d.get_id() + version['id'])
      
    d.download(INSTALLATION_FOLDER)
    file_name = d.get_file_name()
    if file_name:
      logger.info(f'Successfully downloaded as "{file_name}"')
    else:
      logger.error(f'Error downloading "{p.get_title()}", version ID "{version['id']}"!')
    download_dependencies(d)
    

def download_project(identifier):
  # Get info
  logger.info(f'Fetching project info for "{identifier}"')
  p = Project(identifier)

  # Handle errors
  if not p:
    logger.error(f'Error fetching data for "{identifier}"! Skipping!')
    return
  logger.info(f'Found "{p.get_title()}" ({p.get_type().capitalize()})')

  # Skip if project was already visited
  if p.get_slug() in checked_projects:
    logger.info(f'"{p.get_title()}" was already visited. Skipping!')
    return
  # Else: Mark it as visited
  checked_projects.append(p.get_slug())
  

  # Version available?
  if not p.has_version(MC_VERSION):
    return
  version = p.get_version(MC_VERSION, LOADER_TYPE)
  if version is None:
    return
  checked_project_versions.append(version['id'])

  p.download(INSTALLATION_FOLDER)
  file_name = p.get_file_name()
  if file_name:
    logger.info(f'Successfully downloaded as "{file_name}"')
  else:
    logger.error(f'Error downloading "{p.get_title()}", version ID "{version['id']}"!')

  download_dependencies(p)
  if p.get_type() == 'shader' and 'iris' not in checked_projects:
    logger.info('To use shaders, the Iris mod will be installed')
  download_project('Iris')

# Read PROJECTS_FILE and create a new project for each valid URL / SLUG / ID
with open(PROJECTS_FILE, 'r') as f:
  project_entries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
for entry in project_entries:
  print('\n')
  download_project(entry)
  


      