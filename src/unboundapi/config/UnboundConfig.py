from .ConfigEntry import ConfigEntry


class UnboundConfig:
    def __init__(self, config_file: str = "/etc/unboud/unboud.conf"):
        with open(config_file, "r") as file:
            line_nb = 0
            for line in file:
                line_nb += 1
                entry = ConfigEntry(line, line_nb=str(line_nb))

                print(entry)

        return

    pass
