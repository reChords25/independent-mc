import os, requests, logging
from pathlib import Path

logger = logging.getLogger(__name__)

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
  
  def has_version(self, mc_version) -> bool:
    if self.type not in ['mod', 'datapack']: return True
    if mc_version in self.mc_versions:
      logger.info(f'Compatible version found')
      return True
    else:
      logger.error(f'No compatible version found. Skipping!')
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
          if mc_version in version['game_versions'] and 'iris' in version['loaders'] or 'minecraft' in version['loaders'] and version['version_type'] == 'release':
            self.version = version
            return version
        for version in versions:
          if 'iris' in version['loaders'] or 'minecraft' in version['loaders'] and version['version_type'] == 'release':
            self.version = version
            return version
      case _:
        logger.error(f'Project type not (yet) supported!')
        return None
    logger.error('Correct version SOMEHOW could not be found (no release or wrong loader)!')
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

      logger.info(f'Downloading "{self.get_title()}", approx. {f'{file_size / 1000:.1f}KB' if file_size < 1000000 else f'{file_size / 1000000:.1f}MB'} in total')
      
      with requests.get(download_url, stream = True) as r:
        r.raise_for_status()
        with open(os.path.join(destination_path, file_name), 'wb') as f:
          for chunk in r.iter_content(chunk_size = 8192):
            f.write(chunk)
      
      self.file_name = file_name