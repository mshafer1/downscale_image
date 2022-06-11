import winreg

_file_types = [".jpg", ".png", ".bmp"]


def register_downscale_commands(path_to_program, args):
    for file_type in [rf"SystemFileAssociations\{ext}\shell" for ext in _file_types]:
        set_run_key(file_type + r"\DownscaleImage", "Downscale image")
        set_run_key(file_type + r"\DownscaleImage\command", path_to_program + " " + " ".join(args))


def set_run_key(key, value, *_, section=winreg.HKEY_CLASSES_ROOT):
    """
    Set/Remove Run Key in windows registry.

    :param key: Run Key Name
    :param value: Program to Run
    :return: None
    """
    # This is for the system run variable
    print("key is", key, "<->", value)
    winreg.SetValue(section, key, winreg.REG_SZ, value)

    return


if __name__ == "__main__":
    register_downscale_commands("cmd", ["/c", "echo foo && pause"])
