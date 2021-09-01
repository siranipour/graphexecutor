import inspect
import importlib.util
import pathlib

import click

from graphexecutor.runcard_parser import execute_runcard

@click.command()
@click.argument('providers', nargs=-1, type=click.Path(exists=True, path_type=pathlib.Path), required=True)
@click.argument('runcard', nargs=1, type=click.Path(exists=True, path_type=pathlib.Path), required=True)
@click.option('--parallel', is_flag=True, default=False, help='Execute the graph asynchronously')
def main(providers, runcard, parallel):
    ld = load_provider_functions(providers)

    sol = execute_runcard(runcard, ld, parallel)
    print(sol)
    return sol


def load_provider_functions(providers):
    functions = {}

    for provider in providers:
        spec = importlib.util.spec_from_file_location(f"prov.{provider.name}", provider)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        provider_mapping = dict(inspect.getmembers(module, inspect.isfunction))

        functions = {**functions, **provider_mapping}

    return functions


