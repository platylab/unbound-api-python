import os
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt,
)
from unboundapi.main import main as unbound_config
from unboundapi.config.UnboundConfig import (
    DuplicateIDError,
    UnknownIDError,
    UnsupportedClauseError,
    UnsupportedAttributeError,
)
from passlib.hash import sha512_crypt

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["JWT_SECRET_KEY"] = os.environ["UNBOUNDAPI_JWT_SECRET_KEY"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
    seconds=int(
        os.environ.get(
            "JWT_ACCESS_TOKEN_EXPIRES",
            "3600",
        ),
    ),
)
jwt = JWTManager(app)

admin_username = os.environ.get("UNBOUNDAPI_ADMIN_USERNAME", "admin")
admin_password_hash = os.environ["UNBOUNDAPI_ADMIN_PASSWORD_HASH"]


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    # Input validation
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    # Authentication
    if username == admin_username and sha512_crypt.verify(
        password,
        admin_password_hash,
    ):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


@app.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    token_data = get_jwt()
    username = token_data["sub"]
    expires_in = int(token_data["exp"] - datetime.now().timestamp())
    return jsonify(username=username, token_expires_in=expires_in), 200


@app.route(
    "/config/<clause>/<attribute>/<value_id>",
    methods=["GET", "POST", "PUT", "DELETE"],
)
@jwt_required()
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
    load_dotenv(find_dotenv())
    load_dotenv(find_dotenv(".env.local"))
    app.run(host="127.0.0.1", port=8080, debug=True)
