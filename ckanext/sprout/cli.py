import click

from ckan import model

from ckanext.sprout import model

def get_commands():

    @click.group()
    def sprout():
        """Generates sprout commands"""
        pass

    @sprout.command()
    def initdb():
        model.setup()
        click.secho(u'Questions table is set up', fg=u"green")

    @sprout.command()
    def dropdb():
        model.drop()
        click.secho(u'Questions table is removed', fg=u'yellow')

    return [sprout]