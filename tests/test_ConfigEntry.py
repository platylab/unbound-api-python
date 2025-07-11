from unboundapi.config import ConfigEntry, MalformedIDError, ZeroIDError

test_data = [
    {
        "id": "clause_server",
        "input": {
            "line_nb": "",
            "entry": "server:",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "unspecified",
            "raw": "server:",
            "attribute": "server",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "clause_remote-control",
        "input": {
            "line_nb": "1",
            "entry": "remote-control:",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "1",
            "raw": "remote-control:",
            "attribute": "remote-control",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "clause_forward-zone",
        "input": {
            "line_nb": "",
            "entry": "forward-zone:",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "unspecified",
            "raw": "forward-zone:",
            "attribute": "forward-zone",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "clause_auth-zone_spaces_before_after",
        "input": {
            "line_nb": "",
            "entry": "    auth-zone:    ",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "unspecified",
            "raw": "auth-zone:",
            "attribute": "auth-zone",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "clause_module-config_spaces_before",
        "input": {
            "line_nb": "",
            "entry": "    module-config:",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "unspecified",
            "raw": "module-config:",
            "attribute": "module-config",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "clause_dnscrypt_spaces_after",
        "input": {
            "line_nb": "67",
            "entry": "dnscrypt:   ",
        },
        "output": {
            "is_main_clause": True,
            "line_nb": "67",
            "raw": "dnscrypt:",
            "attribute": "dnscrypt",
            "value": "",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "id_malformed",
        "input": {
            "line_nb": "34",
            "entry": 'include: "/etc/unbound/server.d/*" #unsupported',
        },
        "output": {
            "is_main_clause": False,
            "line_nb": "34",
            "raw": 'include: "/etc/unbound/server.d/*" #unsupported',
            "attribute": "include",
            "value": '"/etc/unbound/server.d/*"',
            "id": 0,
        },
        "error": {
            "MalformedIDError": True,
            "ZeroIDError": False,
        },
    },
    {
        "id": "id_zero",
        "input": {
            "line_nb": "unspecified",
            "entry": "port:    53  #0",
        },
        "output": {
            "is_main_clause": False,
            "line_nb": "unspecified",
            "raw": "port: 53 #0",
            "attribute": "port",
            "value": "53",
            "id": 0,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": True,
        },
    },
    {
        "id": "well_formatted",
        "input": {
            "line_nb": "9999",
            "entry": 'local-zone: "test.example.com." static #7',
        },
        "output": {
            "is_main_clause": False,
            "line_nb": "9999",
            "raw": 'local-zone: "test.example.com." static #7',
            "attribute": "local-zone",
            "value": '"test.example.com." static',
            "id": 7,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
    {
        "id": "full_spaces",
        "input": {
            "line_nb": "",
            "entry": '  local-data:    "server.test.example.com.    IN   A     192.168.69.69"    #666  ',
        },
        "output": {
            "is_main_clause": False,
            "line_nb": "unspecified",
            "raw": 'local-data: "server.test.example.com. IN A 192.168.69.69" #666',
            "attribute": "local-data",
            "value": '"server.test.example.com. IN A 192.168.69.69"',
            "id": 666,
        },
        "error": {
            "MalformedIDError": False,
            "ZeroIDError": False,
        },
    },
]


def Set_ConfigEntry(test_data=test_data):
    target_data = list()
    for data in test_data:
        output = False
        error = {
            "MalformedIDError": False,
            "ZeroIDError": False,
        }
        try:
            if data["input"]["line_nb"] == "":
                output = ConfigEntry(data["input"]["entry"])
            else:
                output = ConfigEntry(data["input"]["entry"], data["input"]["line_nb"])
        except MalformedIDError:
            error["MalformedIDError"] = True
        except ZeroIDError:
            error["ZeroIDError"] = True
        finally:
            target_data.append(
                {
                    "output": output,
                    "error": error,
                },
            )
    return target_data


target_data = Set_ConfigEntry(test_data)


def test_error__MalformedIDError():
    for i in range(len(test_data)):
        test = test_data[i]["error"]["MalformedIDError"]
        target = target_data[i]["error"]["MalformedIDError"]
        assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_error__ZeroIDError():
    for i in range(len(test_data)):
        test = test_data[i]["error"]["ZeroIDError"]
        target = target_data[i]["error"]["ZeroIDError"]
        assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_met__is_main_clause():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["is_main_clause"]
            target = target_data[i]["output"].is_main_clause()
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_attr__line_nb():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["line_nb"]
            target = target_data[i]["output"].line_nb
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_attr__raw():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["raw"]
            target = target_data[i]["output"].raw
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_attr__attribute():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["attribute"]
            target = target_data[i]["output"].attribute
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_attr__value():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["value"]
            target = target_data[i]["output"].value
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"


def test_attr__id():
    for i in range(len(test_data)):
        if target_data[i]["output"]:
            test = test_data[i]["output"]["id"]
            target = target_data[i]["output"].id
            assert test == target, f"{test_data[i]['id']}: {test} != {target}"
