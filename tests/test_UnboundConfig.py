from unboundapi.config.UnboundConfig import (
    UnboundConfig,
    DuplicateIDError,
    UnknowedIDError,
)
import filecmp

input_file = "tests/files/test_UnboundConfig/input.conf"
output_file = "tests/files/test_UnboundConfig/output.conf"
target_file = "tests/files/test_UnboundConfig/target.conf"

config = UnboundConfig(input_file)


def test_met__make():
    config.make(output_file)
    assert filecmp.cmp(target_file, output_file, shallow=False)


def test_met__validate():
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
                "error": "UnknowedIDError",
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
        except UnknowedIDError:
            value = ""
            error = "UnknowedIDError"
        finally:
            test = {"value": value, "error": error}
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
        finally:
            test = {"output": output, "error": error}
            target = data["target"]
        assert test == target, f"{data['id']}: {test} != {target}"


def test_met__update_value():
    assert True


def test_met__delete_value():
    assert True
