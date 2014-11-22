"""Detect and configure fasd."""


def configure(ctx):
    ctx.find_program('fasd', mandatory=False)


def _make_fasd_cache(tsk):
    out_node = tsk.outputs[0]
    shell = out_node.suffix()[1:]
    init_args = ['posix-alias', shell + '-hook'] + [
        '{}-{}'.format(arg, shell) for arg in ['ccomp', 'ccomp-install']]
    if shell == 'zsh':
        init_args += ['{}-{}'.format(arg, shell)
                      for arg in ['wcomp', 'wcomp-install']]
    with open(out_node.abspath(), 'w') as output_file:
        ret = tsk.exec_command(
            tsk.env.FASD + ['--init'] + init_args,
            stdout=output_file)
    return ret


def build(ctx):
    if not ctx.env.FASD:
        return
    # See here for all the options: https://github.com/clvv/fasd#install
    for shell in ctx.env.SHELLS:
        out_node = ctx.path.find_or_declare('fasd.' + shell)
        ctx.env[shell.upper() + '_RC_NODES'].append(out_node)
        ctx(rule=_make_fasd_cache, target=out_node, vars=['FASD'])
