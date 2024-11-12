import os, sys, requests

PROJECTS_FILE = "projects.txt"
INSTALLATION_FOLDER = os.getcwd() + "\\minecraft\\wd"
LOADER_TYPE = sys.argv[1]
MINECRAFT_VERSION = sys.argv[2]

API_URL = "https://api.modrinth.com/v2"
visited_projects = set()

def get_project_info(url: str) -> tuple[str, str]:
    response = requests.get(f'{API_URL}/project/{url.rstrip("/").split("/")[-1]}')
    if response.status_code != 200: return None
    project_info = response.json()
    return project_info['title'], project_info['id']

def get_latest(project_id: str) -> str:
    version_url = f'{API_URL}/project/{project_id}/version'
    response = requests.get(version_url)
    
    if response.status_code != 200: return None
    versions = response.json()
    for version in versions:
        if MINECRAFT_VERSION in version['game_versions'] and LOADER_TYPE in version['loaders'] and version['version_type'] == 'release':
            return version
    return None

def download_project(version_info: str) -> str:
    for file in version_info['files']:
        if not file['primary']: continue
        download_url = file['url']
        file_name = file['filename']
        project_path = os.path.join(INSTALLATION_FOLDER, file_name)
        
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(project_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return file_name
    return None

def get_project_title(project_id: str) -> str:
    response = requests.get(f'{API_URL}/project/{project_id}')
    if response.status_code != 200: return None
    return response.json()['title']

def get_dependencies(project_version: str, parent_project_title: str) -> None:
    if not 'dependencies' in project_version: return
    count = sum(1 for item in project_version['dependencies'] if item['dependency_type'] == 'required')
    if count == 0: return
    
    print(f'[INFO] Found {count} required {'dependency' if count == 1 else 'dependencies'} for {parent_project_title}')
    i = 1
    for dependency in project_version['dependencies']:
        if not (dependency['dependency_type'] == 'required' and dependency['project_id']): return
        project_id = dependency['project_id']

        if project_id in visited_projects: continue
        
        project_title = get_project_title(project_id)
        print(f'[INFO] Dependency {i}: {project_title}')
        
        project_version = get_latest(project_id)
        if not project_version:
            print(f'[ERROR] No compatible version found for dependent project {project_title}')
            print(f'[INFO] You might have to delete the file for {parent_project_title} yourself.')
            return
        print(f'[INFO] Downloading dependent project {project_title}')
        file_name = download_project(project_version)
        print(f'[INFO] Successfully downloaded as "{file_name}"')
        visited_projects.add(project_id)
        get_dependencies(project_version, project_title)
        i += 1


if __name__ == "__main__":
    if not os.path.exists(INSTALLATION_FOLDER):
        os.makedirs(INSTALLATION_FOLDER)
    if not os.path.exists(PROJECTS_FILE):
        print(f'[ERROR] Projects file "{PROJECTS_FILE}" not found.')
        print(f'[INFO] Create the file and paste the project URLs or move it to the right directory.')
        exit()
    
    with open(PROJECTS_FILE, 'r') as f:
        project_urls = f.readlines()
    
    for url in project_urls:
        url = url.strip()
        if not url or url[0] == '#': continue
        
        project_title, project_id = get_project_info(url)
        if project_id in visited_projects: continue
        print(f'[INFO] Fetching project info for {project_title}')
        project_version = get_latest(project_id)
        if not project_version:
            print(f'[ERROR] No compatible version found for project {project_title}')
            continue
        print(f'[INFO] Downloading {project_title}')
        file_name = download_project(project_version)
        print(f'[INFO] Successfully downloaded as "{file_name}"')
        visited_projects.add(project_id)
        
        get_dependencies(project_version, project_title)
