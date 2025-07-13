#!/usr/bin/env python
# -*- coding: utf-8 -*-
import click
import json
from uuid import uuid4
from unboundapi.config.UnboundConfig import UnboundConfig

config = None


def get_config(config_file: str = "/etc/unbound/unbound.conf"):
    try:
        global config
        del config
        config = UnboundConfig(config_file)
    except NameError:
        config = UnboundConfig(config_file)
    return config


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
    default="/etc/unbound/unbound.conf",
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
def value(operation, attribute, clause, value, value_id, config_file):
    """
    CRUD operations on values (create, read, update, delete)
    """
    config = get_config(config_file)
    session_id = uuid4()
    tmp_file = f"/tmp/unbound_{session_id}.conf"
    if operation == "create":
        if value:
            response = config.create_value(clause, attribute, value, value_id)
            config.apply(config_file, tmp_file)
            click.echo(response)
        else:
            msg = "Missing value argument for create operation"
            click.echo(msg, err=True)

    elif operation == "read":
        if value_id:
            click.echo(config.get_value(clause, attribute, value_id))
        else:
            click.echo(json.dumps(config.get_attribute(clause, attribute)))

    elif operation == "update":
        if value:
            response = config.update_value(clause, attribute, value, value_id)
            config.apply(config_file, tmp_file)
            click.echo(response)
        else:
            msg = "Missing value argument for update operation"
            click.echo(msg, err=True)

    elif operation == "delete":
        response = config.delete_value(clause, attribute, value_id)
        config.apply(config_file, tmp_file)
        click.echo(response)

    else:
        msg = f"{operation} : Unsupported CRUD operation (create, read, update, delete)"
        click.echo(msg, err=True)


if __name__ == "__main__":
    cli()
