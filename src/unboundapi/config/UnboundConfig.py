from unboundapi.config.ConfigEntry import ConfigEntry
import subprocess
import os


class UnboundConfigError(Exception):
    """Base class for exceptions in UnboundConfig"""

    pass


class DuplicateIDError(UnboundConfigError):
    """Raised when a duplicate ID has been found"""

    def __init__(self, value_id: str, attribute: str, line: str = ""):
        self.id = value_id
        self.attribute = attribute
        self.line = line
        if line:
            msg = f"Duplicate ID #{self.id} for attribute {self.attribute} line {self.line}"
        else:
            msg = f"Duplicate ID #{self.id} for attribute {self.attribute}"
        super().__init__(msg)


class UnknownIDError(UnboundConfigError):
    """Raised when the specified ID does not exist"""

    def __init__(self, attribute: str, value_id: str):
        self.id = value_id
        self.attribute = attribute
        msg = f"Unknown ID #{self.id} for attribute {self.attribute}"
        super().__init__(msg)


class UnsupportedClauseError(UnboundConfigError):
    """Raised when the specified clause is not supported"""

    def __init__(self, clause: str):
        self.clause = clause
        msg = f'Unsupported clause "{self.clause}"'
        super().__init__(msg)


class UnsupportedAttributeError(UnboundConfigError):
    """Raised when the specified attribute does not exist"""

    def __init__(self, clause: str, attribute: str):
        self.clause = clause
        self.attribute = attribute
        msg = f'Unsupported attribute "{self.attribute}" in clause "{self.clause}"'
        super().__init__(msg)


class ValidateError(UnboundConfigError):
    """Raised when the generated config is not valid"""

    def __init__(self, target_file: str, stderr: str):
        self.target_file = target_file
        self.stderr = stderr
        msg = f'The generated config file "{self.target_file}" is not valid\nSTDERR : {self.stderr}'
        super().__init__(msg)


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
                        raise DuplicateIDError(entry.id, entry.attribute, entry.line_nb)

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

    def validate(
        self,
        target_file: str = "/etc/unboud/unboud.conf",
    ) -> subprocess.CompletedProcess:
        """Verify that the created file is valid with unboud-checkconf"""
        return subprocess.run(
            ["unbound-checkconf", target_file],
            capture_output=True,
            text=True,
        )

    def reload_service(self, service_name: str = "unbound.service"):
        """
        Reloads the unbound service
        Raise the error subprocess.CalledProcessError if failed
        """
        subprocess.run(["systemctl", "reload", service_name], check=True)

    def apply(self, target_file: str, tmp_file: str):
        """
        Generates a temporary file and validate it
        If OK, replaces the target_file and reloads unbound service
        """
        self.make(tmp_file)
        result = self.validate(tmp_file)
        if result.returncode == 0:
            os.replace(tmp_file, target_file)
            self.reload_service()
        else:
            raise ValidateError(tmp_file, result.stderr)

    def get_value(self, clause: str, attribute: str, value_id: str) -> str:
        """
        Returns the value for a given attribute and ID.
        If the ID is not found, raise UnknownIDError
        """
        try:
            return getattr(self, clause.replace("-", "_"))[attribute][value_id]
        except KeyError:
            raise UnknownIDError(attribute, value_id)

    def get_attribute(self, clause: str, attribute: str) -> dict:
        """
        Returns all values for a given attribute
        """
        if clause not in UnboundConfig.__supported_attributes.keys():
            raise UnsupportedClauseError(clause)
        elif attribute not in UnboundConfig.__supported_attributes[clause].keys():
            raise UnsupportedAttributeError(clause, attribute)
        return getattr(self, clause.replace("-", "_"))[attribute]

    def create_value(
        self,
        clause: str,
        attribute: str,
        value: str,
        value_id: str = "",
    ) -> dict:
        """
        Creates a new attribute/value pair with specified ID
        If the ID is already used, raise DuplicateIDError
        If no ID is specified, get the first available one
        Can create new attributes with ID=1
        """
        try:
            if clause not in UnboundConfig.__supported_attributes.keys():
                raise UnsupportedClauseError(clause)
            elif attribute not in UnboundConfig.__supported_attributes[clause].keys():
                raise UnsupportedAttributeError(clause, attribute)
            self.get_value(clause, attribute, value_id)
        except UnknownIDError:
            # If no ID is specified, use the first available
            if not value_id:
                i = 0
                while i < 1000:
                    i += 1
                    try:
                        self.get_value(clause, attribute, str(i))
                    except UnknownIDError:
                        value_id = str(i)
                        break
                if i == 1000:
                    raise RuntimeError(
                        f"You have more that 1000 entries for the attribute {attribute}",
                    )
            getattr(self, clause.replace("-", "_"))[attribute][value_id] = value

        else:
            raise DuplicateIDError(value_id, attribute)
        return {"id": value_id}

    def update_value(
        self,
        clause: str,
        attribute: str,
        value: str,
        value_id: str = "",
    ) -> dict:
        """
        Updates value with specified ID
        If the ID is not found, raise UnknownIDError
        Replace whole attribute if no id is specified
        """
        answer = dict()
        if clause not in UnboundConfig.__supported_attributes.keys():
            raise UnsupportedClauseError(clause)
        elif attribute not in UnboundConfig.__supported_attributes[clause].keys():
            raise UnsupportedAttributeError(clause, attribute)

        if value_id:
            old_value = self.get_value(clause, attribute, value_id)
            getattr(self, clause.replace("-", "_"))[attribute][value_id] = value
            answer[value_id] = {
                "id": value_id,
                "old_value": old_value,
                "new_value": value,
            }
        else:
            for old_id, old_value in self.get_attribute(clause, attribute).items():
                if old_id == "1":
                    answer["1"] = {
                        "id": "1",
                        "old_value": old_value,
                        "new_value": value,
                    }
                else:
                    answer[old_id] = {
                        "id": old_id,
                        "old_value": old_value,
                        "new_value": "",
                    }
            getattr(self, clause.replace("-", "_"))[attribute] = {"1": value}
        return answer

    def delete_value(self, clause: str, attribute: str, value_id: str = "") -> dict:
        """
        Deletes value with specified ID
        If the ID is not found, raise UnknownIDError
        Can delete complete attribute if no id is specified
        """
        answer = dict()
        if clause not in UnboundConfig.__supported_attributes.keys():
            raise UnsupportedClauseError(clause)
        elif attribute not in UnboundConfig.__supported_attributes[clause].keys():
            raise UnsupportedAttributeError(clause, attribute)

        if value_id:
            old_value = self.get_value(clause, attribute, value_id)
            getattr(self, clause.replace("-", "_"))[attribute].pop(value_id)
            answer[value_id] = {"id": value_id, "old_value": old_value}
        else:
            for old_id, old_value in self.get_attribute(clause, attribute).items():
                answer[old_id] = {"id": old_id, "old_value": old_value}
            getattr(self, clause.replace("-", "_"))[attribute] = {}
        return answer
