#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import json
import os
from uuid import uuid4
from unboundapi.config.UnboundConfig import UnboundConfig, UnboundConfigError


class MissingValueError(UnboundConfigError):
    """Raised when an input value should have been provided"""

    def __init__(self, operation=""):
        self.operation = operation
        if self.operation:
            msg = f"Missing value argument for {self.operation} operation"
        else:
            msg = "Missing value argument for operation"
        super().__init__(msg)


class UnsupportedOperationError(UnboundConfigError):
    """Raised when trying to use unsupported CRUD operation"""

    def __init__(self, operation="unspecified"):
        self.operation = operation
        msg = f"{self.operation} : Unsupported CRUD operation (create, read, update, delete)"
        super().__init__(msg)


def main(
    operation: str,
    clause: str,
    attribute: str,
    value: str = "",
    value_id: str = "",
    config_file: str = "",
) -> dict:
    """
    CRUD operations on values (create, read, update, delete)
    """
    if config_file == "":
        config_file = os.environ.get(
            "UNBOUNDAPI_UNBOUND_CONF",
            "/etc/unbound/unbound.conf",
        )
    response = dict()
    session_id = uuid4()
    tmp_file = f"/tmp/unbound_{session_id}.conf"
    try:
        with UnboundConfig(config_file) as config:
            if operation == "create":
                if value:
                    response = config.create_value(clause, attribute, value, value_id)
                    config.apply(tmp_file)
                    config.reload_unbound()
                else:
                    raise MissingValueError(operation)

            elif operation == "read":
                if value_id:
                    response[value_id] = config.get_value(clause, attribute, value_id)
                else:
                    response = config.get_attribute(clause, attribute)

            elif operation == "update":
                if value:
                    response = config.update_value(clause, attribute, value, value_id)
                    config.apply(tmp_file)
                    config.reload_unbound()
                else:
                    raise MissingValueError(operation)

            elif operation == "delete":
                response = config.delete_value(clause, attribute, value_id)
                config.apply(tmp_file)
                config.reload_unbound()

            else:
                raise UnsupportedOperationError(operation)

    except UnboundConfigError:
        raise

    return response


@click.group()
def cli():
    """
    Interacting with unbound server
    """
    pass


@cli.command()
@click.argument("operation")
@click.argument("attribute")
@click.argument("value", default="", required=False)
@click.option(
    "-f",
    "--config-file",
    default="",
    help="Unbound config file (default: /etc/unbound/unbound.conf)",
)
@click.option(
    "-i",
    "--value-id",
    default="",
    help='ID for the attribute/value (default: "")',
)
@click.option(
    "-c",
    "--clause",
    default="server",
    help="Name of the clause for the attribute (default: server)",
)
def value(operation, clause, attribute, value, value_id, config_file):
    """
    CRUD operations on values (create, read, update, delete)
    """
    if config_file == "":
        config_file = os.environ.get(
            "UNBOUNDAPI_UNBOUND_CONF",
            "/etc/unbound/unbound.conf",
        )

    try:
        click.echo(
            json.dumps(
                main(operation, clause, attribute, value, value_id, config_file),
            ),
        )
    except (MissingValueError, UnsupportedOperationError) as e:
        click.echo(e, err=True)


@cli.command()
@click.option(
    "-f",
    "--config-file",
    default="",
    help="Unbound config file (default: /etc/unbound/unbound.conf)",
)
def reload(config_file):
    """
    Reloading the unbound service with new config if the config is valid
    /!\\ Only works if unbound is running as a service on same host /!\\
    """
    if config_file == "":
        config_file = os.environ.get(
            "UNBOUNDAPI_UNBOUND_CONF",
            "/etc/unbound/unbound.conf",
        )
    with UnboundConfig(config_file) as config:
        result = config.validate()
        if result.returncode == 0:
            click.echo("Valid config, reloading service...")
            config.reload_unbound()
            click.echo("Success !")
            return {"status": "success"}
        else:
            click.echo(f"Invalid config :\n{result.stderr}", err=True)
            return {"status": "invalid config"}


if __name__ == "__main__":
    cli()
