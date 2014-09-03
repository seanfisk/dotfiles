"""Detect and configure devpi."""


from os.path import join

DEVPI_PYPI_URL = 'http://localhost:4040/root/pypi/+simple/'


def configure(ctx):
    ctx.find_program('devpi-ctl', var='DEVPI_CTL', mandatory=False)


def build(ctx):
    if not ctx.env.DEVPI_CTL:
        return

    for relative_path in [join('pip', 'pip.conf'), 'pydistutils.cfg']:
        in_node = ctx.path.find_resource([
            'dotfiles', relative_path + '.in'])
        out_node = ctx.path.find_or_declare(relative_path)
        ctx(features='subst',
            source=in_node,
            target=out_node,
            DEVPI_PYPI_URL=DEVPI_PYPI_URL)

        # Make the path relative to the dotfiles/ directory so that it
        # matches the other elements.
        ctx.env.DOTFILE_NODES.append(out_node)
