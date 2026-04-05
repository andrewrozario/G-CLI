import click

@click.group()
@click.version_option()
def cli():
    """A sample CLI tool template."""
    pass

@cli.command()
@click.argument('name')
def hello(name):
    """Greet the user."""
    click.echo(f"Hello {name}!")

@cli.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.argument('name')
def repeat(count, name):
    """Repeat a greeting multiple times."""
    for _ in range(count):
        click.echo(f"Hello {name}!")

if __name__ == '__main__':
    cli()
