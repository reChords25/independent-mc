import os, requests

class Project:
  def __init__(self, url):
    response = requests.get(f'https://api.modrinth.com/v2/project/{url.rstrip("/").split("/")[-1] if 'modrinth' in url else url}')
    if response.status_code != 200:
      self = None
      return
    project_info = response.json()
    self.title = project_info['title']
    self.slug = project_info['slug']
    self.id = project_info['id']
    self.type = project_info['project_type']
    self.game_versions = [version for version in project_info['game_versions']]
    self.version = None
    self.file_size = None
    self.dependencies = []

  def get_title(self):
    return self.title
  
  def get_slug(self):
    return self.slug
  
  def get_id(self):
    return self.id
  
  def get_type(self):
    return self.type

  def get_dependencies(self):
    return self.dependencies if len(self.dependencies) > 0 else None
  
  def has_version(self, game_version: str, loader_type: str) -> bool:
    if self.version != None: return True
    response = requests.get(f'https://api.modrinth.com/v2/project/{self.id}/version')
    if response.status_code != 200: return None
    versions = response.json()
    for version in versions:
      if game_version in version['game_versions'] and loader_type in version['loaders'] and version['version_type'] == 'release':
        self.version = version
        self.dependencies = [[dependency['project_id'], dependency['version_id']] for dependency in version['dependencies'] if dependency['dependency_type'] == 'required']
        return True
    return False
  
  def set_version(self, version_id: str) -> bool:
    if self.version != None: return True
    response = requests.get(f'https://api.modrinth.com/v2/project/{self.id}/version/{version_id}')
    if response.status_code != 200: return False
    return True
  
  # Only for shaders and resourcepacks because they may be of the wrong version and still work as intended
  def set_latest_version(self):
    response = requests.get(f'https://api.modrinth.com/v2/project/{self.id}/version')
    if response.status_code != 200: return None
    versions = response.json()
    self.version = versions[0]

  
  def download(self, installation_folder: str):
    match self.type:
      case 'mod':
        installation_folder = os.path.join(installation_folder, 'mods')
      case 'shader':
        installation_folder = os.path.join(installation_folder, 'shaderpacks')
      case 'resourcepack':
        installation_folder = os.path.join(installation_folder, 'resourcepacks')
      case 'datapack':
        installation_folder = os.path.join(installation_folder, 'datapacks')
      case _:
        print(f'[ERROR] Project type not supported!')

    if not os.path.exists(installation_folder):
      os.makedirs(installation_folder)

    for file in self.version['files']:
      if not file['primary']: continue
      download_url = file['url']
      file_name = file['filename']

      print(f'[INFO] Downloading {self.get_title()}, appr. {round(float(file['size']/1000000), 3)}MB in total')
      
      with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(installation_folder, file_name), 'wb') as f:
          for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
      return file_name
    return None