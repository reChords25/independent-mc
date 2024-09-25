import os, json, requests
from zipfile import ZipFile

MODPACK_INFO_FILE_NAME = "modrinth.index.json"

for mrpack in os.listdir("."):
    if not mrpack.endswith(".mrpack"): continue
    print(f"[INFO] Found modpack \"{mrpack}\"")
    with ZipFile(mrpack) as zip:
        if not MODPACK_INFO_FILE_NAME in zip.namelist():
            print(f"[ERROR] Modpack \"{mrpack}\" is not valid, skipping!")
            continue
        with zip.open(MODPACK_INFO_FILE_NAME) as jsonfile:
            data = json.load(jsonfile)

    project_names = []

    for project in data['files']:
        for download_url in project['downloads']:
            project_id = download_url.split('/')[4]
            response = requests.get(f"https://api.modrinth.com/v2/project/{project_id}")
            if response.status_code != 200:
                print(f"[ERROR] HTTP Error code {response.status_code}! Unable to fetch data for project with id ID {project_id}")
                continue
            print(f"[INFO] Found {response.json()['title']}")
            project_type = response.json()['project_type']
            project_slug = response.json()['slug']
            if project_type and project_slug:
                project_names.append(f"https://modrinth.com/{project_type}/{project_slug}")

    project_list = f'{mrpack[:-len(".mrpack")]}.txt'
    with open(project_list, 'w') as file:
        file.write(f"# Mod file generated by reChords25' generator tool.\n# Generated from \"{mrpack}\".\n\n")
        for project_name in project_names:
            file.write(project_name + '\n')
        file.write("\n# End of generated file.")
    print(f"\nMod list has been written to {project_list}")
