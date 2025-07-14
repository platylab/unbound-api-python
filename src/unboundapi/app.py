from flask import Flask, request, jsonify
from unboundapi.main import main as unbound_config
from unboundapi.config.UnboundConfig import (
    DuplicateIDError,
    UnknownIDError,
    UnsupportedClauseError,
    UnsupportedAttributeError,
)

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
            return jsonify(
                {"error": "UnknownIDError", "reason": "ID must be an integer"},
            ), 400

    try:
        if request.method == "POST":
            if not request.json or "value" not in request.json:
                return jsonify({"error": "Value is required"}), 400
            value = request.get_json().get("value")
            return jsonify(
                {
                    "items": unbound_config(
                        "create",
                        clause,
                        attribute,
                        value,
                        value_id=value_id,
                    ),
                },
            ), 201

        elif request.method == "GET":
            return jsonify(
                {"items": unbound_config("read", clause, attribute, value_id=value_id)},
            ), 200

        elif request.method == "PUT":
            if not request.json or "value" not in request.json:
                return jsonify({"error": "Value is required"}), 400
            value = request.get_json().get("value")
            return jsonify(
                {
                    "items": unbound_config(
                        "update",
                        clause,
                        attribute,
                        value,
                        value_id=value_id,
                    ),
                },
            ), 200

        elif request.method == "DELETE":
            return jsonify(
                {
                    "items": unbound_config(
                        "delete",
                        clause,
                        attribute,
                        value_id=value_id,
                    ),
                },
            ), 200

    except DuplicateIDError as e:
        return jsonify({"error": "DuplicateIDError", "reason": str(e)}), 409
    except UnknownIDError as e:
        return jsonify({"error": "UnknownIDError", "reason": str(e)}), 404
    except UnsupportedClauseError as e:
        return jsonify({"error": "UnsupportedClauseError", "reason": str(e)}), 404
    except UnsupportedAttributeError as e:
        return jsonify({"error": "UnsupportedAttributeError", "reason": str(e)}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
