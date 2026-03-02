from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify
from unboundapi.main import main as unbound_config
from unboundapi.config.UnboundConfig import (
    DuplicateIDError,
    UnknownIDError,
    UnsupportedClauseError,
    UnsupportedAttributeError,
)

load_dotenv(find_dotenv())
load_dotenv(find_dotenv(".env.local"))

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route(
    "/config/<clause>/<attribute>/<value_id>",
    methods=["GET", "POST", "PUT", "DELETE"],
)
def configure(clause, attribute, value_id):
    if value_id == "*":
        value_id = ""
    else:
        try:
            int(value_id)
        except ValueError:
            http_code = 400
            body = {
                "error": "UnknownIDError",
                "reason": "ID must be an integer",
                "status": http_code,
            }
            return jsonify(body), http_code

    try:
        if request.method == "POST":
            if not request.json or "value" not in request.json:
                http_code = 400
                body = {
                    "error": "MissingValueError",
                    "reason": "value is required in json payload",
                    "status": http_code,
                }
                return jsonify(body), 400
            value = request.get_json().get("value")
            http_code = 201
            body = {
                "items": unbound_config("create", clause, attribute, value, value_id),
                "status": http_code,
            }
            return jsonify(body), http_code

        elif request.method == "GET":
            http_code = 200
            body = {
                "items": unbound_config("read", clause, attribute, value_id=value_id),
                "status": http_code,
            }
            return jsonify(body), http_code

        elif request.method == "PUT":
            if not request.json or "value" not in request.json:
                http_code = 400
                body = {
                    "error": "MissingValueError",
                    "reason": "value is required in json payload",
                    "status": http_code,
                }
                return jsonify(body), 400
            value = request.get_json().get("value")
            http_code = 200
            body = {
                "items": unbound_config("update", clause, attribute, value, value_id),
                "status": http_code,
            }
            return jsonify(body), http_code

        elif request.method == "DELETE":
            http_code = 200
            body = {
                "items": unbound_config("delete", clause, attribute, value_id=value_id),
                "status": http_code,
            }
            return jsonify(body), http_code

    except DuplicateIDError as e:
        http_code = 409
        body = {
            "error": "DuplicateIDError",
            "reason": str(e),
            "status": http_code,
        }
        return jsonify(body), http_code
    except UnknownIDError as e:
        http_code = 404
        body = {
            "error": "UnknownIDError",
            "reason": str(e),
            "status": http_code,
        }
        return jsonify(body), http_code
    except UnsupportedClauseError as e:
        http_code = 404
        body = {
            "error": "UnsupportedClauseError",
            "reason": str(e),
            "status": http_code,
        }
        return jsonify(body), http_code
    except UnsupportedAttributeError as e:
        http_code = 404
        body = {
            "error": "UnsupportedAttributeError",
            "reason": str(e),
            "status": http_code,
        }
        return jsonify(body), http_code


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
