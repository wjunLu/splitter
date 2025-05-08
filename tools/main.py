import click
from tools.cmd.cut import cut


@click.group()
def entrance():
    pass

def _add_commands():
    # Unified interface for extension.
    entrance.add_command(cut)

def main():
    _add_commands()
    entrance()


if __name__ == "__main__":
    main()