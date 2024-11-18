# Basic imports
import os, sys
# Pathlib for better cross-compatibility in the end
from pathlib import Path
# Program-specific imports
from project import Project
import util

# Constants
PROJECTS_FILE = "projects.txt"
INSTALLATION_FOLDER = os.path.join(os.getcwd(), "minecraft", "wd")
LOADER_TYPE = sys.argv[1]
MC_VERSION = sys.argv[2]

# Set so that projects are not checked twice
checked_projects = []
checked_project_versions = []
file_sizes = [0, 0, 0, 0] # Mods, Resourcepacks, Shaders, Datapacks


# Check for PROJECTS_FILE (where Mods etc. are defined)
def check_for_projects_file():
  if not Path(PROJECTS_FILE).exists():
    print(f'[ERROR] Projects file "{PROJECTS_FILE}" not found')
    print(f'[INFO] Create the file and paste the project URLs or move it to the correct directory')
    sys.exit(1)

def add_file_size(p):
  match p.get_type():
    case 'mod':
      file_sizes[0] += p.get_file_size()
    case 'resourcepack':
      file_sizes[1] += p.get_file_size()
    case 'shader':
      file_sizes[2] += p.get_file_size()
    case 'datapack':
      file_sizes[3] += p.get_file_size()

  
def download_dependencies(p):
  # Log dependency count
  dependencies = p.get_req_dependencies()
  if dependencies is None:
    print(f'[INFO] No dependencies found')
    return
  print()
  count = len(dependencies)
  print(f'[INFO] {count} {'dependency' if count == 1 else 'dependencies'} found for "{p.get_title()}"')

  # For every dependency
  for i, (d_id, d_version_id) in enumerate(dependencies, 1):
    print()
    print(f'[INFO] Fetching project info for dependency no. {i}')
    d = Project(d_id)
    if not d:
      print(f'[ERROR] Could not fetch data for "{entry}"! Skipping. "{p.get_title()}" might not work correctly without!')
      continue
    print(f'[INFO] Dependency "{d.get_title()}" found')
    
    if d_version_id is None:
      if d.get_id() in checked_projects:
        print(f'[INFO] "{d.get_title()}" was already visited. Skipping!')
        continue
      if not d.has_version(MC_VERSION):
        print(f'[ERROR] "{d.get_title()}" might not work correctly without "{d.get_title()}"!')
        continue
      version = d.get_version(MC_VERSION, LOADER_TYPE)
      if version is None:
        print(f'[ERROR] "{d.get_title()}" might not work correctly without "{d.get_title()}"!')
      checked_projects.append(d.get_id())
    else:
      d.set_version(d_version_id)
      version = d.get_version(MC_VERSION, LOADER_TYPE)
      if d.get_id() + version['id'] in checked_project_versions:
        print(f'[INFO] "{d.get_title()}" version ID "{version['id']}" was already visited. Skipping!')
        continue
      checked_projects.append(d.get_id())
      checked_project_versions.append(d.get_id() + version['id'])
      
    d.download(INSTALLATION_FOLDER)
    file_name = d.get_file_name()
    if file_name:
      print(f'[INFO] Successfully downloaded as "{file_name}"')
      add_file_size(d)
    else:
      print(f'[ERROR] Error downloading "{p.get_title()}", version ID "{version['id']}"!')
    download_dependencies(d)
    

def download_project(identifier):
  # Get info
  print(f'[INFO] Fetching project info for "{identifier}"')
  p = Project(identifier)

  # Handle errors
  if not p:
    print(f'[ERROR] Error fetching data for "{identifier}"! Skipping!')
    return
  print(f'[INFO] Found "{p.get_title()}" ({p.get_type().capitalize()})')

  # Skip if project was already visited
  if p.get_slug() in checked_projects:
    print(f'[INFO] "{p.get_title()}" was already visited. Skipping!')
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
    print(f'[INFO] Successfully downloaded as "{file_name}"')
    add_file_size(p)
  else:
    print(f'[ERROR] Error downloading "{p.get_title()}", version ID "{version['id']}"!')

  download_dependencies(p)
  if p.get_type() == 'shader' and 'iris' not in checked_projects:
    print(f'[INFO] To use shaders, the Iris mod will be installed')
    download_project('Iris')

if __name__ == '__main__':
  # Read PROJECTS_FILE and create a new project for each valid URL / SLUG / ID
  with open(PROJECTS_FILE, 'r') as f:
    project_entries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
  for entry in project_entries:
    download_project(entry)
    print('--------------------------------------')
  print(f'[INFO] Approx. {util.convert_file_size(sum(file_size for file_size in file_sizes))} downloaded in total.')
  


      