from unboundapi.config.UnboundConfig import (
    UnboundConfig,
    DuplicateIDError,
    UnknownIDError,
    UnsupportedClauseError,
    UnsupportedAttributeError,
)
import filecmp

input_file = "tests/files/test_UnboundConfig/input.conf"

config = UnboundConfig(input_file)


def test_met__make_before():
    target_file = "tests/files/test_UnboundConfig/before_target.conf"
    output_file = "tests/files/test_UnboundConfig/before_output.conf"
    config.make(output_file)
    assert filecmp.cmp(target_file, output_file, shallow=False)


def test_met__validate_before():
    output_file = "tests/files/test_UnboundConfig/before_output.conf"
    result = config.validate(output_file)
    assert result.returncode == 0, f"STDERR   : {result.stderr}"


def test_met__get_value():
    test_data = [
        {
            "id": "local-data",
            "input": {"clause": "server", "attribute": "local-data", "value_id": "32"},
            "target": {
                "value": '"lgtm-da01.eni.platylab.com. IN A 172.20.12.20"',
                "error": "",
            },
        },
        {
            "id": "unknowed_id",
            "input": {"clause": "server", "attribute": "local-zone", "value_id": "7"},
            "target": {
                "value": "",
                "error": "UnknownIDError",
            },
        },
    ]

    for data in test_data:
        value = ""
        error = ""
        try:
            value = config.get_value(
                clause=data["input"]["clause"],
                attribute=data["input"]["attribute"],
                value_id=data["input"]["value_id"],
            )
        except UnknownIDError:
            value = ""
            error = "UnknownIDError"
        finally:
            test = {"value": value, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met_get_attribute():
    test_data = [
        {
            "id": "successful_get_attribute",
            "input": {
                "clause": "server",
                "attribute": "interface-action",
            },
            "target": {
                "output": {
                    "1": "10.10.10.51 allow",
                    "2": "127.0.0.1 allow",
                },
                "error": "",
            },
        },
        {
            "id": "error_UnsupportedClause",
            "input": {
                "clause": "unsupported-clause",
                "attribute": "something",
            },
            "target": {
                "output": {},
                "error": "UnsupportedClauseError",
            },
        },
        {
            "id": "error_UnsupportedAttribute",
            "input": {
                "clause": "server",
                "attribute": "forward-addr",
            },
            "target": {
                "output": {},
                "error": "UnsupportedAttributeError",
            },
        },
    ]

    for data in test_data:
        output = dict()
        error = ""
        try:
            output = config.get_attribute(
                clause=data["input"]["clause"],
                attribute=data["input"]["attribute"],
            )
        except UnsupportedClauseError:
            error = "UnsupportedClauseError"
        except UnsupportedAttributeError:
            error = "UnsupportedAttributeError"
        finally:
            test = {"output": output, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met__create_value():
    test_data = [
        {
            "id": "create_with_id",
            "input": {
                "clause": "server",
                "attribute": "local-zone",
                "value": '"test.example.com." static',
                "value_id": "6",
            },
            "target": {
                "output": {
                    "id": "6",
                },
                "error": "",
            },
        },
        {
            "id": "create_without_id",
            "input": {
                "clause": "server",
                "attribute": "local-data",
                "value": '"www.test.example.com. IN A 1.2.3.4"',
                "value_id": "",
            },
            "target": {
                "output": {
                    "id": "44",
                },
                "error": "",
            },
        },
        {
            "id": "already_exists",
            "input": {
                "clause": "forward-zone",
                "attribute": "forward-addr",
                "value": "1.1.1.1",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "DuplicateIDError",
            },
        },
        {
            "id": "error_UnsupportedClause",
            "input": {
                "clause": "unsupported-clause",
                "attribute": "something",
                "value": "something",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "UnsupportedClauseError",
            },
        },
        {
            "id": "error_UnsupportedAttribute",
            "input": {
                "clause": "server",
                "attribute": "forward-addr",
                "value": "something",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "UnsupportedAttributeError",
            },
        },
    ]

    for data in test_data:
        output = dict()
        error = ""
        try:
            output = config.create_value(
                clause=data["input"]["clause"],
                attribute=data["input"]["attribute"],
                value=data["input"]["value"],
                value_id=data["input"]["value_id"],
            )
        except DuplicateIDError:
            error = "DuplicateIDError"
        except UnsupportedClauseError:
            error = "UnsupportedClauseError"
        except UnsupportedAttributeError:
            error = "UnsupportedAttributeError"
        finally:
            test = {"output": output, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met__update_value():
    test_data = [
        {
            "id": "update_value_id",
            "input": {
                "clause": "server",
                "attribute": "local-zone",
                "value": '"ipa.platylab.com." transparent',
                "value_id": "5",
            },
            "target": {
                "output": {
                    "5": {
                        "id": "5",
                        "old_value": '"ipa.platylab.com." typetransparent',
                        "new_value": '"ipa.platylab.com." transparent',
                    },
                },
                "error": "",
            },
        },
        {
            "id": "update_attribute",
            "input": {
                "clause": "server",
                "attribute": "interface",
                "value": "10.10.10.55",
                "value_id": "",
            },
            "target": {
                "output": {
                    "1": {
                        "id": "1",
                        "old_value": "10.10.10.51",
                        "new_value": "10.10.10.55",
                    },
                    "2": {
                        "id": "2",
                        "old_value": "127.0.0.1",
                        "new_value": "",
                    },
                },
                "error": "",
            },
        },
        {
            "id": "error_UnknownID",
            "input": {
                "clause": "forward-zone",
                "attribute": "forward-addr",
                "value": "1.1.1.1",
                "value_id": "35",
            },
            "target": {
                "output": {},
                "error": "UnknownIDError",
            },
        },
        {
            "id": "error_UnsupportedClause",
            "input": {
                "clause": "unsupported-clause",
                "attribute": "something",
                "value": "something",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "UnsupportedClauseError",
            },
        },
        {
            "id": "error_UnsupportedAttribute",
            "input": {
                "clause": "server",
                "attribute": "forward-addr",
                "value_id": "1",
                "value": "something",
            },
            "target": {
                "output": {},
                "error": "UnsupportedAttributeError",
            },
        },
    ]

    for data in test_data:
        output = dict()
        error = ""
        try:
            output = config.update_value(
                clause=data["input"]["clause"],
                attribute=data["input"]["attribute"],
                value=data["input"]["value"],
                value_id=data["input"]["value_id"],
            )
        except UnknownIDError:
            error = "UnknownIDError"
        except UnsupportedClauseError:
            error = "UnsupportedClauseError"
        except UnsupportedAttributeError:
            error = "UnsupportedAttributeError"
        finally:
            test = {"output": output, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met__delete_value():
    test_data = [
        {
            "id": "delete_value_id",
            "input": {
                "clause": "server",
                "attribute": "local-data",
                "value_id": "15",
            },
            "target": {
                "output": {
                    "15": {
                        "id": "15",
                        "old_value": '"ipamaster.adm.platylab.com. IN A 10.10.10.55"',
                    },
                },
                "error": "",
            },
        },
        {
            "id": "delete_attribute",
            "input": {
                "clause": "server",
                "attribute": "access-control",
                "value_id": "",
            },
            "target": {
                "output": {
                    "1": {
                        "id": "1",
                        "old_value": "10.10.10.0/24 allow",
                    },
                    "2": {
                        "id": "2",
                        "old_value": "127.0.0.0/8 allow",
                    },
                },
                "error": "",
            },
        },
        {
            "id": "error_UnknownID",
            "input": {
                "clause": "forward-zone",
                "attribute": "forward-addr",
                "value_id": "35",
            },
            "target": {
                "output": {},
                "error": "UnknownIDError",
            },
        },
        {
            "id": "error_UnsupportedClause",
            "input": {
                "clause": "unsupported-clause",
                "attribute": "something",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "UnsupportedClauseError",
            },
        },
        {
            "id": "error_UnsupportedAttribute",
            "input": {
                "clause": "server",
                "attribute": "forward-addr",
                "value_id": "1",
            },
            "target": {
                "output": {},
                "error": "UnsupportedAttributeError",
            },
        },
    ]

    for data in test_data:
        output = dict()
        error = ""
        try:
            output = config.delete_value(
                clause=data["input"]["clause"],
                attribute=data["input"]["attribute"],
                value_id=data["input"]["value_id"],
            )
        except UnknownIDError:
            error = "UnknownIDError"
        except UnsupportedClauseError:
            error = "UnsupportedClauseError"
        except UnsupportedAttributeError:
            error = "UnsupportedAttributeError"
        finally:
            test = {"output": output, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met__make_after():
    target_file = "tests/files/test_UnboundConfig/after_target.conf"
    output_file = "tests/files/test_UnboundConfig/after_output.conf"
    config.make(output_file)
    assert filecmp.cmp(target_file, output_file, shallow=False)


def test_met__validate_after():
    output_file = "tests/files/test_UnboundConfig/after_output.conf"
    result = config.validate(output_file)
    assert result.returncode == 0, f"STDERR   : {result.stderr}"
