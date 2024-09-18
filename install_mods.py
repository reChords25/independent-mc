import os, sys, requests

MODS_FILE = "mods.txt"
MODS_FOLDER = os.getcwd() + "\\minecraft\\wd\\mods"
LOADER_TYPE = sys.argv[1]
MINECRAFT_VERSION = sys.argv[2]

API_URL = "https://api.modrinth.com/v2"
visited_mods = set()

def get_mod_info(url: str) -> tuple[str, str]:
    response = requests.get(f'{API_URL}/project/{url.rstrip("/").split("/")[-1]}')
    if response.status_code != 200: return None
    mod_info = response.json()
    return mod_info['title'], mod_info['id']

def get_latest(mod_id: str) -> str:
    version_url = f'{API_URL}/project/{mod_id}/version'
    response = requests.get(version_url)
    
    if response.status_code != 200: return None
    versions = response.json()
    for version in versions:
        if MINECRAFT_VERSION in version['game_versions'] and LOADER_TYPE in version['loaders'] and version['version_type'] == 'release':
            return version
    return None

def download_mod(version_info: str) -> str:
    for file in version_info['files']:
        if file['primary']:
            download_url = file['url']
            file_name = file['filename']
            mod_path = os.path.join(MODS_FOLDER, file_name)
            
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(mod_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return file_name
    return None

def get_mod_title(mod_id: str) -> str:
    response = requests.get(f'{API_URL}/project/{mod_id}')
    if response.status_code != 200: return None
    return response.json()['title']

def get_dependencies(mod_version: str, parent_mod_title: str) -> None:
    if not 'dependencies' in mod_version: return
    count = len(mod_version['dependencies'])
    if count == 0: return
    
    print(f'[INFO] Found {count} {'dependency' if count == 1 else 'dependencies'} for {parent_mod_title}')
    i = 1
    for dependency in mod_version['dependencies']:
        if not (dependency['dependency_type'] == 'required' and dependency['project_id']): return
        mod_id = dependency['project_id']

        if mod_id in visited_mods: continue
        
        mod_title = get_mod_title(mod_id)
        print(f'[INFO] Dependency {i}: {mod_title}')
        
        mod_version = get_latest(mod_id)
        if not mod_version:
            print(f'[ERROR] No compatible version found for dependent mod {mod_title}')
            print(f'[INFO] You might have to delete the file for {parent_mod_title} yourself.')
            return
        print(f'[INFO] Downloading dependent mod {mod_title}')
        file_name = download_mod(mod_version)
        print(f'[INFO] Successfully downloaded as "{file_name}"')
        visited_mods.add(mod_id)
        get_dependencies(mod_version, mod_title)
        i += 1


if __name__ == "__main__":
    if not os.path.exists(MODS_FOLDER):
        os.makedirs(MODS_FOLDER)
    if not os.path.exists(MODS_FILE):
        print(f'[ERROR] Mods file "{MODS_FILE}" not found.')
        print(f'[INFO] Create the file and paste the mod URLs or move it to the right directory.')
        exit()
    
    with open(MODS_FILE, 'r') as f:
        mod_urls = f.readlines()
    
    for url in mod_urls:
        url = url.strip()
        if not url or url[0] == '#': continue
        
        mod_title, mod_id = get_mod_info(url)
        if mod_id in visited_mods: continue
        print(f'[INFO] Fetching mod info for {mod_title}')
        mod_version = get_latest(mod_id)
        if not mod_version:
            print(f'[ERROR] No compatible version found for mod {mod_title}')
            continue
        print(f'[INFO] Downloading {mod_title}')
        file_name = download_mod(mod_version)
        print(f'[INFO] Successfully downloaded as "{file_name}"')
        visited_mods.add(mod_id)
        
        get_dependencies(mod_version, mod_title)
