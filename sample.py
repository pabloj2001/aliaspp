from aliaspp import alias, aliases, execute, Environment, CommandBuilder, ValueRequirement

# gc = git checkout master
# gc -b new_branch = git checkout -b pablo/new_branch
# gc branch = git checkout pablo/branch
@alias
def gc(cb: CommandBuilder):
    cb.base('git checkout')
    if cb.has_arg(0):
        cb.update_arg(0, lambda prev_value: 'pablo/' + prev_value)
    else:
        cb.if_set('b', ValueRequirement.REQUIRE_VALUE).set_flag('b', f"pablo/{cb.get_flag('b')}")
        cb.if_not_set('b').append_arg('master')

# gb = git branch
# gb -D branch = git branch -D pablo/branch
@alias
def gb(cb: CommandBuilder):
    cb.base('git branch')
    cb.if_set('D', ValueRequirement.REQUIRE_VALUE).set_flag('D', f"pablo/{cb.get_flag('D')}")

# gac "message" = git add . && git commit -m "message"
@alias
def gac(cb: CommandBuilder):
    cb.base('git add . && git commit')
    cb.if_not_set('m').set_flag('m', cb.get_arg(0, error='Please provide a commit message'))

# mb = make build
# mb --alert = make build; terminal-notifier -message "Build Complete"
@alias
def mb(cb: CommandBuilder):
    cb.base('make build')
    if cb.is_set('alert'):
        cb.remove_flag('alert')
        alertCb = cb.append_command('terminal-notifier', ';')
        alertCb.set_flag('message', 'Build Complete', dashes=1)

aliases({
    'gs': 'git status',
    'cls': 'clear',
})

# You can also perform a dry run by adding the '--alias-dry-run' flag
execute(env=Environment('env'), dry_run=True)

# Add the following line to your shell configuration file (e.g., .bashrc, .zshrc) to use these aliases:
# alias <alias-name>="python3 ~/aliaspp/sample.py <alias-name>"
# Ex: alias gc="python3 ~/aliaspp/sample.py gc"
# in the future "aliaspp setup sample.py -v python3" will add this alias for you