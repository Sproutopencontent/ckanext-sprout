import click

from ckanext.sprout import model


PROMPT_MESAGE = u'This will delete all of your questionnaire data!\
 Do you want to continue?'


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
    @click.confirmation_option(prompt=PROMPT_MESAGE)
    def dropdb():
        model.drop()
        click.secho(u'Questions table is removed', fg=u'yellow')

    return [sprout]
