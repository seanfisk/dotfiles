"""Detect and configure devpi."""


from os.path import join, splitext

DEVPI_PYPI_URL = 'http://localhost:4040/root/pypi/+simple/'


def configure(ctx):
    ctx.find_program('devpi-ctl', var='DEVPI_CTL', mandatory=False)


def build(ctx):
    if not ctx.env.DEVPI_CTL:
        return

    # Ugh... this is ugly. Unfortunately double extensions are not fun.
    for relpath_list in [['pip', 'pip.conf'], ['pydistutils.cfg']]:
        relpath_list = ['dotfiles'] + relpath_list
        out_node = ctx.path.find_or_declare(relpath_list)
        relpath_list[-1] += '.in'
        in_node = ctx.path.find_resource(relpath_list)
        ctx(features='subst',
            source=in_node,
            target=out_node,
            DEVPI_PYPI_URL=DEVPI_PYPI_URL)

        ctx.install_dotfile(out_node)
