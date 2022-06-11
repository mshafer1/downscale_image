import winreg

_file_types = [".jpg", ".png", ".bmp"]


def register_downscale_commands(path_to_program, args):
    """Register 'Downscale image' as right click option for each of _file_types to call program."""
    for file_type in [rf"SystemFileAssociations\{ext}\shell" for ext in _file_types]:
        _set_run_key(file_type + r"\DownscaleImage", "Downscale image")
        _set_run_key(file_type + r"\DownscaleImage\command", path_to_program + " " + " ".join(args))


def _set_run_key(key, value, *_, section=winreg.HKEY_CLASSES_ROOT):
    """Set/Remove Run Key in windows registry."""
    # This is for the system run variable
    print("key is", key, "<->", value)
    winreg.SetValue(section, key, winreg.REG_SZ, value)

    return
