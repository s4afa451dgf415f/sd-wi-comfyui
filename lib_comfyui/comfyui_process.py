import atexit
import inspect
import os
import subprocess
import sys
from pathlib import Path

from lib_comfyui import ipc, torch_utils, argv_conversion, global_state
from lib_comfyui.wi import settings
from lib_comfyui.comfyui import pre_main


comfyui_process = None


@ipc.restrict_to_process('wi')
def start():
    if not global_state.enabled:
        return

    install_location = settings.get_install_location()
    if not install_location.exists():
        print('[sd-wi-comfyui]', f'Could not find ComfyUI under directory "{install_location}". The server will NOT be started.', file=sys.stderr)
        return

    ipc.current_callback_listeners = {'wi': ipc.callback.CallbackWatcher(ipc.call_fully_qualified, 'wi', global_state.ipc_strategy_class, clear_on_init=True)}
    ipc.current_callback_proxies = {'comfyui': ipc.callback.CallbackProxy('comfyui', global_state.ipc_strategy_class, clear_on_init=True)}
    ipc.start_callback_listeners()
    atexit.register(stop)
    start_comfyui_process(install_location)


@ipc.restrict_to_process('wi')
def start_comfyui_process(comfyui_install_location):
    global comfyui_process

    executable = get_comfyui_executable(comfyui_install_location)
    comfyui_env = get_comfyui_env(comfyui_install_location)
    install_comfyui_requirements(executable, comfyui_install_location, comfyui_env)
    args = [executable, inspect.getfile(pre_main)] + argv_conversion.get_comfyui_args()

    print('[sd-wi-comfyui]', 'Starting subprocess for comfyui...')
    comfyui_process = subprocess.Popen(
        args=args,
        executable=executable,
        cwd=str(comfyui_install_location),
        env=comfyui_env,
    )


def get_comfyui_executable(comfyui_install_location: Path) -> str:
    executable = sys.executable

    if os.name == 'nt':
        executable_paths = [
            comfyui_install_location / 'venv' / 'scripts' / 'python.exe',
            comfyui_install_location.parent / 'python_embeded' / 'python.exe',
        ]
    else:
        executable_paths = [
            comfyui_install_location / 'venv' / 'bin' / 'python',
            comfyui_install_location.parent / 'python_embeded' / 'python',
        ]

    for potential_executable in executable_paths:
        if potential_executable.exists():
            executable = potential_executable
            print('[sd-wi-comfyui]', 'Detected custom ComfyUI venv:', executable)
            break

    return str(executable)


def get_comfyui_env(comfyui_install_location):
    comfyui_env = os.environ.copy()
    if 'PYTHONPATH' in comfyui_env:
        del comfyui_env['PYTHONPATH']

    problematic_windows_tmp_dirs = {
        k: v
        for k, v in comfyui_env.items()
        if k in ("TMP", "TEMP") and v == "tmp"
    }
    if os.name == "nt" and problematic_windows_tmp_dirs:
        problematic_windows_tmp_dirs = " and ".join(f'{k}="{v}"' for k, v in problematic_windows_tmp_dirs.items())
        message_prefix = "[sd-wi-comfyui] "
        print(
            "\n".join([
                f'{message_prefix}Found {problematic_windows_tmp_dirs} in the environment. On Windows, this is known to cause issues.',
                f'{message_prefix}If ComfyUI refuses to start, consider using TEMP="temp" or TMP="temp" as a workaround.',
                f'{message_prefix}For more information, see https://github.com/ModelSurge/sd-wi-comfyui/issues/170#issuecomment-1792009789',
            ]),
            file=sys.stderr,
        )

    comfyui_env['SD_WEBUI_COMFYUI_EXTENSION_DIR'] = settings.get_extension_base_dir()
    comfyui_env['SD_WEBUI_COMFYUI_IPC_STRATEGY_CLASS_NAME'] = global_state.ipc_strategy_class.__name__
    return comfyui_env


def install_comfyui_requirements(executable, comfyui_install_location, comfyui_env):
    if executable == sys.executable:
        # requirements already installed in the wi by install.py
        return

    print('[sd-wi-comfyui]', 'Installing mandatory pip requirements in ComfyUI venv...')
    subprocess.check_call(
        args=[
            executable,
            *(['-s'] if "python_embeded" in executable or "python_embedded" in executable else []),
            '-m',
            'pip',
            'install',
            '-r',
            str(Path(settings.get_extension_base_dir(), 'requirements.txt')),
        ],
        executable=executable,
        cwd=str(comfyui_install_location),
        env=comfyui_env,
    )


@ipc.restrict_to_process('wi')
def stop():
    atexit.unregister(stop)
    stop_comfyui_process()
    ipc.stop_callback_listeners()


@ipc.restrict_to_process('wi')
def stop_comfyui_process():
    global comfyui_process
    if comfyui_process is None:
        return

    print('[sd-wi-comfyui]', 'Attempting to gracefully terminate the ComfyUI server...')
    comfyui_process.terminate()
    try:
        comfyui_process.wait(global_state.comfyui_graceful_termination_timeout)
        print('[sd-wi-comfyui]', 'The ComfyUI server was gracefully terminated')
    except subprocess.TimeoutExpired:
        print('[sd-wi-comfyui]', 'Graceful termination timed out. Killing the ComfyUI server...')
        comfyui_process.kill()
        print('[sd-wi-comfyui]', 'The ComfyUI server was killed')
    comfyui_process = None
