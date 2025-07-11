import re


class ConfigEntryError(Exception):
    """Base class for exceptions in ConfigEntry."""

    pass


class MalformedIDError(ConfigEntryError):
    """Raised when the ID is malformed."""

    def __init__(self, attribute, line, value):
        self.attribute = attribute
        self.line = line
        self.value = value
        super().__init__(
            f"The ID for attribute '{self.attribute}' is malformed, got '{self.value}'. Line in conf {self.line}.",
        )


class ZeroIDError(ConfigEntryError):
    """Raised when the ID is zero."""

    def __init__(self, attribute, line):
        self.attribute = attribute
        self.line = line
        super().__init__(
            f"The ID for attribute '{self.attribute}' cannot be equal to 0. Line in conf {self.line}.",
        )


class ConfigEntry:
    __allowed_clauses = {
        "server:",
        "remote-control:",
        "forward-zone:",
        "auth-zone:",
        "module-config:",
        "dnscrypt",
    }

    def __init__(self, entry: str, line_nb: str = "unspecified"):
        self.line_nb = line_nb
        self.raw = entry
        self.attribute = ""
        self.data = {"id": "", "value": ""}
        self.clean()
        self.get_attribute()
        self.get_data()

    def clean(self) -> str:
        self.raw = re.sub(r"\s+", " ", self.raw.strip())
        if self.raw.startswith("#"):
            self.raw = ""
        return self.raw

    def get_attribute(self) -> str:
        self.attribute = self.raw.split(" ")[0][:-1]
        return self.attribute

    def is_main_clause(self) -> bool:
        return self.attribute in ConfigEntry.__allowed_clauses

    def get_id(self) -> int:
        """
        The ID is defined for a non-clause attribute by '#ID', and should be an non-zero integer
        Returns the ID or 0 if malformated, unspecified or is a clause
        """
        if self.is_main_clause():
            return 0
        else:
            last_part = self.raw.split(" ")[-1]
            if last_part.startswith("#"):
                try:
                    attr_id = int(last_part[1:])
                    if attr_id == 0:
                        raise ZeroIDError(self.attribute, self.line_nb)
                    return attr_id
                except ValueError:
                    raise MalformedIDError(self.attribute, self.line_nb, last_part)
                    return 0
            else:
                return 0

    def get_value(self) -> str:
        """
        The value is defined for an attribute only. It is the part after "attribute_name:" and before any end of line comments.
        If the attribute is a clause, the value is an empty string.
        """
        if self.is_main_clause():
            return ""
        else:
            value = []
            for item in self.raw.split(" ")[1:]:
                if item.startswith("#"):
                    break
                else:
                    value.append(item)
        return " ".join(value).strip('"')

    def get_data(self) -> dict:
        self.data["id"] = str(self.get_id())
        self.data["value"] = self.get_value()
        return self.data


class Config:
    def __init__(self, config_file: str = "/etc/unboud/unboud.conf"):
        with open(config_file, "r") as file:
            line_nb = 0
            for line in file:
                line_nb += 1
                entry = ConfigEntry(line, line_nb=str(line_nb))

                print(entry)

        return

    pass
