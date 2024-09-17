import os, sys, requests

MODS_FILE = "mods.txt"  # The file containing the URLs to the modrinth mods
MODS_FOLDER = os.getcwd() + "\\minecraft\\wd\\mods"
LOADER_TYPE = sys.argv[1]
MINECRAFT_VERSION = sys.argv[2]

API_URL = "https://api.modrinth.com/v2"

def get_mod_info(url):
    # Mod URL structure: https://modrinth.com/mod/{mod_id}
    response = requests.get(f'{API_URL}/project/{url.rstrip('/').split('/')[-1]}')

    if response.status_code != 200: return None
    return response.json()['title'], response.json()['id']

def get_latest(mod_id):
    version_url = f'{API_URL}/project/{mod_id}/version'
    response = requests.get(version_url)

    if response.status_code != 200: return None
    versions = response.json()
    for version in versions:
        if MINECRAFT_VERSION in version['game_versions'] and LOADER_TYPE in version['loaders'] and version['version_type'] == 'release':
            return version

def download_mod(version_info):
    for file in version_info['files']:
        if file['primary']:
            download_url = file['url']
            file_name = file['filename']
            mod_path = os.path.join(MODS_FOLDER, file_name)
            
            # Download and save the file
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(mod_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            break
    return file_name

def download_mods():
    if not os.path.exists(MODS_FILE):
        print(f'[ERROR] Mods file "{MODS_FILE}" not found.')
        print(f'[INFO] Create the file and paste the mod URLs or move it to the right directory.')
        return
    
    with open(MODS_FILE, 'r') as f:
        mod_urls = f.readlines()
    
    for url in mod_urls:
        url = url.strip()
        if not url or url[0] == '#':
            continue
        
        mod_name, mod_id = get_mod_info(url)
        print(f'[INFO] Fetching mod: {mod_name}')
        
        mod_version = get_latest(mod_id)
        if mod_version:
            file_name = download_mod(mod_version)
            print(f'[INFO] Downloaded {mod_name} as "{file_name}"')
        else:
            print(f'[ERROR] No compatible version found for mod {mod_id}')

if __name__ == "__main__":
    if not os.path.exists(MODS_FOLDER):
        os.makedirs(MODS_FOLDER)
    download_mods()
