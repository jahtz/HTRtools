import click

from modules.pagexml import regionstats_cli, pagesearch_cli, pagefix_cli
from modules.parser import csv2txt_cli, ods2json_cli


@click.group()
@click.help_option("--help", "-h")
@click.version_option(
    "0.1",
    "-v", "--version",
    prog_name="HTRtools",
    message="%(prog)s v%(version)s - Developed at Centre for Philology and Digitality (ZPD), University of Würzburg"
)
def cli(**kwargs):
    """
    HTRtools main entry point.

    Developed at Centre for Philology and Digitality (ZPD), University of Würzburg.
    """


# pagexml module
cli.add_command(regionstats_cli)
cli.add_command(pagesearch_cli)
cli.add_command(pagefix_cli)

# parser module
cli.add_command(csv2txt_cli)
cli.add_command(ods2json_cli)

if __name__ == '__main__':
    cli()
