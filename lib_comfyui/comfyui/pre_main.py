import os
import sys


def patch_sys_path():
    comfyui_install_dir = os.getcwd()
    extension_dir = os.getenv("SD_WEBUI_COMFYUI_EXTENSION_DIR")
    if not comfyui_install_dir or not extension_dir:
        print("[sd-wi-comfyui]", f"Could not add new entries to sys.path. install_dir={comfyui_install_dir}, extension_dir={extension_dir}, sys.path={sys.path}", file=sys.stderr)
        print("[sd-wi-comfyui]", f"Exiting...", file=sys.stderr)
        exit(1)

    sys.path[:0] = (comfyui_install_dir, extension_dir)


if __name__ == "__main__":
    patch_sys_path()


import atexit
import builtins
import psutil
import threading
import time
import runpy
from lib_comfyui import (
    custom_extension_injector,
    ipc,
)
from lib_comfyui.comfyui import routes_extension, queue_tracker
from lib_comfyui.wi import paths, settings


original_print = builtins.print
def comfyui_print(*args, **kwargs):
    return original_print('[ComfyUI]', *args, **kwargs)


@ipc.restrict_to_process('comfyui')
def main():
    builtins.print = comfyui_print
    setup_ipc()
    patch_comfyui()
    start_comfyui()


@ipc.restrict_to_process('comfyui')
def setup_ipc():
    print('[sd-wi-comfyui]', 'Setting up IPC...')
    ipc_strategy_class_name = os.getenv('SD_WEBUI_COMFYUI_IPC_STRATEGY_CLASS_NAME')
    print('[sd-wi-comfyui]', f'Using inter-process communication strategy: {settings.ipc_display_names[ipc_strategy_class_name]}')
    ipc_strategy_factory = getattr(ipc.strategies, os.getenv('SD_WEBUI_COMFYUI_IPC_STRATEGY_CLASS_NAME'))
    ipc.current_callback_listeners = {'comfyui': ipc.callback.CallbackWatcher(ipc.call_fully_qualified, 'comfyui', ipc_strategy_factory)}
    ipc.current_callback_proxies = {'wi': ipc.callback.CallbackProxy('wi', ipc_strategy_factory)}
    ipc.start_callback_listeners()
    atexit.register(ipc.stop_callback_listeners)

    parent_id = os.getppid()
    monitor_thread = threading.Thread(target=watch_wi_exit, args=(parent_id,))
    monitor_thread.start()


@ipc.restrict_to_process('comfyui')
def watch_wi_exit(parent_id):
    while True:
        if not psutil.pid_exists(parent_id):
            print("[sd-wi-comfyui]", "The wi has exited, exiting comfyui.")
            exit()

        time.sleep(1)


@ipc.restrict_to_process('comfyui')
def patch_comfyui():
    print('[sd-wi-comfyui]', 'Patching ComfyUI...')
    try:
        # workaround for newer versions of comfyui https://github.com/comfyanonymous/ComfyUI/commit/3039b08eb16777431946ed9ae4a63c5466336bff
        # remove the try-except to stop supporting older versions
        import comfy.options
        comfy.options.enable_args_parsing()
    except ImportError:
        pass

    paths.share_wi_folder_paths()
    custom_extension_injector.register_wi_extensions()
    routes_extension.patch_server_routes()
    queue_tracker.patch_prompt_queue()


@ipc.restrict_to_process('comfyui')
def start_comfyui():
    print('[sd-wi-comfyui]', f'Launching ComfyUI with arguments: {" ".join(sys.argv[1:])}')
    runpy.run_path(os.path.join(os.getcwd(), 'main.py'), {'comfyui_print': comfyui_print}, '__main__')


if __name__ == '__main__':
    ipc.current_process_id = 'comfyui'
    main()
