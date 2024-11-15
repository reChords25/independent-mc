import os, requests
from pathlib import Path
import util

class Project:
  def __init__(self, entry):
    response = requests.get(f'https://api.modrinth.com/v2/project/{entry.rstrip("/").split("/")[-1] if 'modrinth' in entry else entry}')
    if response.status_code != 200: return None
    p_info = response.json()
    self.title = p_info['title']
    self.slug = p_info['slug']
    self.id = p_info['id']
    self.type = p_info['project_type']
    self.mc_versions = [version for version in p_info['game_versions']]
    self.valid_for_client = True if p_info['client_side'] in ['required', 'optional'] else False
    self.version = None
    self.file_name = None
    self.file_size = None

  def get_title(self) -> str:
    return self.title
  
  def get_slug(self) -> str:
    return self.slug
  
  def get_id(self) -> str:
    return self.id
  
  def get_type(self) -> str:
    return self.type
    
  def get_file_name(self) -> str:
    if self.version is None: return None
    return self.file_name
  
  def get_file_size(self) -> str:
    if self.file_name is None: return None
    return self.file_size
  
  def has_version(self, mc_version) -> bool:
    if self.type not in ['mod', 'datapack']: return True
    if mc_version in self.mc_versions:
      print(f'[INFO] Compatible version found')
      return True
    else:
      print(f'[ERROR] No compatible version found. Skipping!')
      return False

  def get_req_dependencies(self) -> list[list[str, str | None]] | None:
    return [[dependency['project_id'], dependency['version_id']] for dependency in self.version['dependencies'] if dependency['dependency_type'] == 'required'] if self.version['dependencies'] else None
    
  def get_version(self, mc_version: str, loader_type: str):
    if self.version is not None: return self.version
    response = requests.get(f'https://api.modrinth.com/v2/project/{self.id}/version')
    if response.status_code != 200: return None
    versions = response.json()
    match self.type:
      case 'mod':
        for version in versions:
          if mc_version in version['game_versions'] and loader_type in version['loaders'] and version['version_type'] == 'release':
            self.version = version
            return version
      case 'datapack':
        for version in versions:
          if mc_version in version['game_versions'] and version['version_type'] == 'release':
            self.version = version
            return version
      case 'shader' | 'resourcepack':
        for version in versions:
          if mc_version in version['game_versions'] and ('iris' in version['loaders'] or 'minecraft' in version['loaders']) and version['version_type'] == 'release':
            self.version = version
            return version
        for version in versions:
          if 'iris' in version['loaders'] or 'minecraft' in version['loaders'] and version['version_type'] == 'release':
            print(f'[INFO] No current version found for selected Minecraft version, installing version for {version['game_versions'][-1]} anyway')
            self.version = version
            return version
      case _:
        print(f'[ERROR] Project type not (yet) supported!')
        return None
    print(f'[ERROR] Correct version SOMEHOW could not be found (no release or wrong loader)!')
    return None
  
  def set_version(self, version_id: str) -> str | None:
    response = requests.get(f'https://api.modrinth.com/v2/project/{self.id}/version/{version_id}')
    if response.status_code != 200: return None
    self.version = response.json()
    
  def download(self, installation_folder: str):
    folder_map = {
      'mod': 'mods',
      'shader': 'shaderpacks',
      'resourcepack': 'resourcepacks',
      'datapack': 'datapacks'
    }
    destination_path = os.path.join(installation_folder, folder_map.get(self.type, ''))
    if not os.path.exists(destination_path):
      os.makedirs(destination_path)

    for file in self.version['files']:
      if not file['primary']: continue
      download_url = file['url']
      file_name = file['filename']
      file_size = file['size']
      
      downloaded_bytes = 0
      with requests.get(download_url, stream = True) as r:
        r.raise_for_status()
        with open(os.path.join(destination_path, file_name), 'wb') as f:
          for chunk in r.iter_content(chunk_size = 8192):
            print(f'[INFO] Downloading "{self.get_title()}", approx. {util.convert_file_size(file_size)} in total ({round((downloaded_bytes / file_size)  * 100)}%)', end='\r')
            f.write(chunk)
            downloaded_bytes += len(chunk)
        print(f'[INFO] Downloading "{self.get_title()}", approx. {util.convert_file_size(file_size)} in total (100%)', end='\n')
      
      self.file_name = file_name
      self.file_size = file_size