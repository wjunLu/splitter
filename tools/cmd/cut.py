import click
from tools.splitter.splitter import Splitter

@click.command(
    name="cut",
    help="Split slices from openEuler packages."
)
@click.option(
    "-r",
    "--release",
    required=True,
    help="This decides which openEuler release you will use, such as `openEuler-24.03-LTS-SP1`."

)
@click.option(
    "-a",
    "--arch",
    required=True,
    help="The architecture you need."
)
@click.option(
    "-o",
    "--output",
    required=True,
    help="The path to output generated parts."
)
@click.argument("parts", nargs=-1)
def cut(release, arch, output, parts):
    splitter = Splitter(release, arch, output, parts)
    splitter.cut()
