from unboundapi.config.ConfigEntry import ConfigEntry


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
    }

    def __init__(self, config_file: str = "/etc/unboud/unboud.conf"):
        self.server = UnboundConfig.__supported_attributes["server"]
        self.remote_control = UnboundConfig.__supported_attributes["remote-control"]
        self.forward_zone = UnboundConfig.__supported_attributes["forward-zone"]
        self.auth_zone = UnboundConfig.__supported_attributes["auth-zone"]
        self.dnscrypt = UnboundConfig.__supported_attributes["dnscrypt"]

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

    def to_dict(self):
        return {
            "server": self.server,
            "remote-control": self.remote_control,
            "forward-zone": self.forward_zone,
            "auth-zone": self.auth_zone,
            "dnscrypt": self.dnscrypt,
        }

    def __str__(self):
        return str(self.to_dict())
