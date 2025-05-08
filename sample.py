from aliaspp import alias, execute, Environment, CommandBuilder

# gc = git checkout master
# gc -b new_branch = git checkout -b pablo/new_branch
# gc branch = git checkout pablo/branch
@alias
def gc(cb: CommandBuilder):
    cb.base('git checkout')
    if cb.hasArg(0):
        cb.updateArg(0, lambda prev_value: 'pablo/' + prev_value)
    else:
        if cb.isSet('b'):
            cb.setFlag('b', 'pablo/' + cb.getFlag('b'), overwrite=True)
        else:
            cb.appendArg('master')

# gb = git branch
# gb -D branch = git branch -D pablo/branch
@alias
def gb(cb: CommandBuilder):
    cb.base('git branch')
    cb.ifSet('D', requires_value=True).setFlag('D', f"pablo/{cb.getFlag('D')}", overwrite=True)

# gac "message" = git add . && git commit -m "message"
@alias
def gac(cb: CommandBuilder):
    cb.base('git add . && git commit')
    cb.ifNotSet('m').setFlag('m', cb.getArg(0, error='Please provide a commit message'))

# gs = git status
@alias
def gs(cb: CommandBuilder):
    cb.base('git status')

execute(env=Environment('env'), dry_run=True)

# alias gc="python3 ~/.aliaspp/sample.py gc"
# in the future "aliaspp setup sample.py -v python3" will add this alias for you