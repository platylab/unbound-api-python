from unboundapi.config.ConfigEntry import ConfigEntry
import subprocess


class UnboundConfigError(Exception):
    """Base class for exceptions in UnboundConfig"""

    pass


class DuplicateIDError(UnboundConfigError):
    """Raised when a duplicate ID has been found"""

    def __init__(self, attribute: str, line: str, id: str):
        self.attribute = attribute
        self.line = line
        self.id = id
        super().__init__(
            f"Found duplicate ID #{self.id} for attribute {self.attribute} line {self.line}",
        )


class UnboundConfig:
    __supported_attributes = {
        "remote-control": {
            "control-enable": dict(),
            "control-interface": dict(),
            "control-port": dict(),
            "server-key-file": dict(),
            "server-cert-file": dict(),
            "control-key-file": dict(),
            "control-cert-file": dict(),
        },
        "forward-zone": {
            "name": dict(),
            "forward-addr": dict(),
        },
        "auth-zone": {
            "name": dict(),
        },
        "dnscrypt": {
            "dnscrypt-enable": dict(),
            "dnscrypt-port": dict(),
        },
        "server": {
            "module-config": dict(),
            "interface": dict(),
            "port": dict(),
            "prefer-ip4": dict(),
            "do-ip4": dict(),
            "do-ip6": dict(),
            "do-udp": dict(),
            "do-tcp": dict(),
            "access-control": dict(),
            "interface-action": dict(),
            "serve-expired": dict(),
            "serve-expired-ttl": dict(),
            "serve-expired-client-timeout": dict(),
            "local-zone": dict(),
            "local-data": dict(),
        },
    }

    def __init__(self, config_file: str = "/etc/unboud/unboud.conf"):
        self.remote_control = UnboundConfig.__supported_attributes["remote-control"]
        self.forward_zone = UnboundConfig.__supported_attributes["forward-zone"]
        self.auth_zone = UnboundConfig.__supported_attributes["auth-zone"]
        self.dnscrypt = UnboundConfig.__supported_attributes["dnscrypt"]
        self.server = UnboundConfig.__supported_attributes["server"]
        self.__load_config(config_file)

    def __str__(self) -> str:
        return str(self.to_dict())

    def to_dict(self):
        return {
            "remote-control": self.remote_control,
            "forward-zone": self.forward_zone,
            "auth-zone": self.auth_zone,
            "dnscrypt": self.dnscrypt,
            "server": self.server,
        }

    def __load_config(self, config_file: str = "/etc/unboud/unboud.conf"):
        self.remote_control = UnboundConfig.__supported_attributes["remote-control"]
        self.forward_zone = UnboundConfig.__supported_attributes["forward-zone"]
        self.auth_zone = UnboundConfig.__supported_attributes["auth-zone"]
        self.dnscrypt = UnboundConfig.__supported_attributes["dnscrypt"]
        self.server = UnboundConfig.__supported_attributes["server"]

        with open(config_file, "r") as file:
            current_clause = ""
            line_nb = 0
            for line in file:
                line_nb += 1
                entry = ConfigEntry(line, line_nb=str(line_nb))
                # If the line is empty, do not treat it
                if not entry.raw:
                    continue
                # If this is a main clause, shift the current clause and continue reading
                if entry.attribute in UnboundConfig.__supported_attributes.keys():
                    current_clause = entry.attribute.replace("-", "_")
                    continue
                # If the attribute is a supported attribute for the clause, treat the entry
                if entry.attribute in getattr(self, current_clause).keys():
                    # ID should be unique for a particular attibute type
                    if (
                        entry.id
                        not in getattr(self, current_clause)[entry.attribute].keys()
                    ):
                        getattr(self, current_clause)[entry.attribute][entry.id] = (
                            entry.value
                        )
                    else:
                        raise DuplicateIDError(entry.attribute, entry.line_nb, entry.id)

    def clear(self):
        """Clear the current configuration data."""
        for attribute in UnboundConfig.__supported_attributes.keys():
            getattr(self, attribute.replace("-", "_")).clear()

    def reload_config(self, config_file: str = "/etc/unboud/unboud.conf"):
        self.clear()
        self.__load_config(config_file)

    def make(self, target_file: str) -> str:
        """Create the config file from the stored config. The file must not be existant"""
        lines_to_write = list()
        for clause in UnboundConfig.__supported_attributes.keys():
            clause_lines = list()
            clause_lines.append(f"{clause}:")
            for attribute, data in UnboundConfig.__supported_attributes[clause].items():
                for value_id, value in data.items():
                    clause_lines.append(f"  {attribute}: {value} #{value_id}")
            clause_lines.append("")
            if len(clause_lines) > 2:
                lines_to_write += clause_lines
        with open(target_file, "w") as file:
            for line in lines_to_write[:-1]:
                file.write(line + "\n")
        return target_file

    def validate(self, target_file: str) -> subprocess.CompletedProcess:
        """Verify that the created file is valid with unboud-checkconf"""
        return subprocess.run(
            ["unbound-checkconf", target_file],
            capture_output=True,
            text=True,
        )
