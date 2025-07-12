import re


class ConfigEntryError(Exception):
    """Base class for exceptions in ConfigEntry."""

    pass


class MalformedIDError(ConfigEntryError):
    """Raised when the ID is malformed."""

    def __init__(self, attribute: str, line: str, value: str):
        self.attribute = attribute
        self.line = line
        self.value = value
        super().__init__(
            f"The ID for attribute '{self.attribute}' is malformed, got '{self.value}'. Line in conf {self.line}.",
        )


class ZeroIDError(ConfigEntryError):
    """Raised when the ID is zero."""

    def __init__(self, attribute: str, line: str):
        self.attribute = attribute
        self.line = line
        super().__init__(
            f"The ID for attribute '{self.attribute}' cannot be equal to 0. Line in conf {self.line}.",
        )


class ConfigEntry:
    __allowed_clauses = {
        "server",
        "remote-control",
        "forward-zone",
        "auth-zone",
        "dnscrypt",
    }

    def __init__(self, entry: str, line_nb: str = "unspecified"):
        self.line_nb = str(line_nb)
        self.raw = str(entry)
        self.attribute = ""
        self.id = ""
        self.value = ""
        self.get_raw()
        self.get_attribute()
        self.get_id()
        self.get_value()

    def to_dict(self) -> dict:
        return {
            "line_nb": self.line_nb,
            "raw": self.raw,
            "attribute": self.attribute,
            "value": self.value,
            "id": self.id,
        }

    def __str__(self) -> str:
        return str(self.to_dict())

    def get_raw(self) -> str:
        self.raw = re.sub(r"\s+", " ", self.raw.strip())
        if self.raw.startswith("#"):
            self.raw = ""
        return self.raw

    def get_attribute(self) -> str:
        self.attribute = self.raw.split(" ")[0][:-1]
        return self.attribute

    def is_main_clause(self) -> bool:
        return self.attribute in ConfigEntry.__allowed_clauses

    def get_id(self) -> str:
        """
        The ID is defined for a non-clause attribute by '#ID', and should be an non-zero integer
        Returns the ID or 0 if malformated, unspecified or is a clause
        """
        self.id = "0"
        if self.is_main_clause():
            return self.id
        else:
            last_part = self.raw.split(" ")[-1]
            if last_part.startswith("#"):
                try:
                    self.id = str(int(last_part[1:]))
                    if self.id == "0":
                        raise ZeroIDError(self.attribute, self.line_nb)
                    return self.id
                except ValueError:
                    raise MalformedIDError(self.attribute, self.line_nb, last_part)
                    return self.id
            else:
                return self.id

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
        self.value = " ".join(value)
        return self.value
