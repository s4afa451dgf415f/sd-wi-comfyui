import os
import sys


default_install_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CofyUI')


def main(install_location, should_install_manager=False):
    repo_url = 'https://github.com/s4afa451dgf415f/CofyUI.git'
    install_repo(repo_url, install_location)

    if should_install_manager:
        print("should_install_manager")
        manager_repo_url = 'https://github.com/ltdrdata/ComfyUI-Manager.git'
        hanhua_repo_url = 'https://github.com/AlekPet/ComfyUI_Custom_Nodes_AlekPet.git'
        prompt_repo_url = 'https://github.com/twri/sdxl_prompt_styler.git'
        manager_location = manager_location_from_comfyui_location(install_location)
        hanhua_location = hanhua_location_from_comfyui_location(install_location)
        prompt_location = prompt_location_from_comfyui_location(install_location)
        # install_repo(manager_repo_url, manager_location)
        # install_repo(hanhua_repo_url, hanhua_location)
        # install_repo(prompt_repo_url, prompt_location)

def manager_location_from_comfyui_location(comfyui_location):
    return os.path.join(comfyui_location, 'custom_nodes', 'ComfyUI-Manager')

def hanhua_location_from_comfyui_location(comfyui_location):
    return os.path.join(comfyui_location, 'custom_nodes', 'AIGODLIKE-ComfyUI-Translation')

def prompt_location_from_comfyui_location(comfyui_location):
    return os.path.join(comfyui_location, 'custom_nodes', 'sdxl_prompt_styler')

def install_repo(git_repo_url, install_location):
    import git
    print("install_location",install_location)
    os.mkdir(install_location)
    git.Repo.clone_from(git_repo_url, install_location)


def update(install_location):
    print("[sd-wi-comfyui]", f"Updating comfyui at {install_location}...")
    if not install_location.is_dir() or not any(install_location.iterdir()):
        print("[sd-wi-comfyui]", f"Cannot update comfyui since it is not installed.", file=sys.stderr)
        return

    import git
    repo = git.Repo(install_location)
    current = repo.head.commit
    repo.remotes.origin.pull()
    if current == repo.head.commit:
        print("[sd-wi-comfyui]", "Already up to date.")
    else:
        print("[sd-wi-comfyui]", "Done updating comfyui.")


if __name__ == '__main__':
    install_location = default_install_location
    if len(sys.argv) > 1:
        inistall_location = sys.argv[1]

    main(install_location)
