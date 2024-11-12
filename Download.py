import os, sys
from Project import Project

PROJECTS_FILE = "projects.txt"
INSTALLATION_FOLDER = os.getcwd() + "\\minecraft\\wd"
LOADER_TYPE = sys.argv[1]
MINECRAFT_VERSION = sys.argv[2]

checked_projects = set()

if not os.path.exists(PROJECTS_FILE):
  print(f'[ERROR] Projects file "{PROJECTS_FILE}" not found')
  print(f'[INFO] Create the file and paste the project URLs or move it to the right directory')
  exit()

with open(PROJECTS_FILE, 'r') as f:
  project_urls = f.readlines()

for url in project_urls:
  url = url.strip()
  if not url or url[0] == '#': continue
  
  p = Project(url)
  print(f'[INFO] Fetching project info for {p.get_title()}')
  if not p:
    print(f'[ERROR] Error fetching data for "{url}"! Skipping')
    continue
  if p.get_id() in checked_projects:
    print(f'[INFO] {p.get_title()} was already visited. Skipping')
    continue
  if not p.has_version(MINECRAFT_VERSION, LOADER_TYPE):
    if p.get_type() == 'mod':
      print(f'[ERROR] No compatible version found for project {p.get_title()}! Skipping')
      continue
    else:
      print(f'[INFO] No correct version found for project {p.get_title()}, installing the newest')
      p.set_latest_version()
  file_name = p.download(INSTALLATION_FOLDER)
  if file_name:
    print(f'[INFO] Successfully downloaded as "{file_name}"')
  else:
    print(f'[ERROR] Error downloading {p.get_title()}!')

  checked_projects.add(p.get_id())
  
  i = 1
  if not p.get_dependencies():
    print(f'[INFO] No dependencies found')
    continue
  print(f'[INFO] {len(p.get_dependencies())} dependencies found for {p.get_title()}')
  for dependency in p.get_dependencies():
    print(f'[INFO] Fetching project info for dependency no. {i}')
    d = Project(dependency[0])
    if not p:
      print(f'[ERROR] Error fetching data for "{url}"! Skipping. {p.get_title()} might not work correctly')
      continue
    print(f'[INFO] Dependency {d.get_title()} found')
    if d.get_id() in checked_projects:
      print(f'[INFO] {d.get_title()} was already visited. Skipping')
      continue
    if dependency[1]:
      d.set_version(dependency[1])
    else:
      if not d.has_version(MINECRAFT_VERSION, LOADER_TYPE):
        print(f'[ERROR] No compatible version found for project {d.get_title()}! Skipping')
        continue
      file_name = d.download(INSTALLATION_FOLDER)
      if file_name:
        print(f'[INFO] Successfully downloaded as "{file_name}"')
      else:
        print(f'[ERROR] Error downloading {d.get_title()}!')
      checked_projects.add(d.get_id())
    i += 1
      