import click

from modules.pagestats import regionstats_cli
#from modules.pagesearch import pagesearch_cli


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


# pagestats module
cli.add_command(regionstats_cli)

# pagesearch_module
#cli.add_command(pagesearch_cli)

