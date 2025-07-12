from unboundapi.config.UnboundConfig import UnboundConfig
import filecmp

input_file = "tests/files/test_UnboundConfig/input.conf"
output_file = "tests/files/test_UnboundConfig/output.conf"
target_file = "tests/files/test_UnboundConfig/target.conf"

config = UnboundConfig(input_file)


def test_full(
    input_file: str = input_file,
    output_file: str = output_file,
    target_file: str = target_file,
):
    config.make(output_file)
    assert filecmp.cmp(target_file, output_file, shallow=False)


def test_unbound_checkconf(
    input_file: str = input_file,
    output_file: str = output_file,
    target_file: str = target_file,
):
    config.make(output_file)
    result = config.validate(output_file)
    assert result.returncode == 0, f"STDERR   : {result.stderr}"
