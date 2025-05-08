__package__ = "aliaspp"
__version__ = "0.1.0"

import sys
import os

aliases = {}

def alias(alias = None):
    """
    Decorator to define an alias for a command.
    """
    def decorator(func):
        if not callable(func):
            raise ValueError("Function is not callable")
        
        alias_name = alias.strip()
        if alias_name in aliases:
            raise ValueError(f"Alias '{alias_name}' already exists")
        aliases[alias_name] = func
        return func

    if isinstance(alias, str):
        return decorator
    elif callable(alias):
        alias_name = alias.__name__
        if alias_name in aliases:
            raise ValueError(f"Alias '{alias_name}' already exists")
        aliases[alias_name] = alias
        return alias
    else:
        raise ValueError("Alias must be a string or a callable function")

def execute(env=None, dry_run=False):
    """
    Execute the command with the given environment.
    """
    if len(sys.argv) < 2:
        print("No command provided")
        return

    args = sys.argv[2:]
    cb = OngoingCommandBuilder(args, env)

    for alias_name, func in aliases.items():
        if sys.argv[1] == alias_name:
            func(cb)
            cb.execute(dry_run)
            break
    else:
        print(f"Alias '{sys.argv[1]}' not found")

def _exit_with_error(message: str):
    """
    Print an error message to stderr and exit the program.
    """
    print(message, file=sys.stderr)
    exit(1)

def _clean_value(value: str) -> str:
    if value is None:
        return None
    value = value.strip()
    if ' ' in value:
        value = f'"{value}"'
    return value


class Environment:
    """
    Class to represent an environment.
    """
    def __init__(self, env_file_path):
        if env_file_path is None or env_file_path == '':
            raise ValueError("Environment file path cannot be empty")

        self.vars = {}
        self.env_file_path = env_file_path
        
        # Read existing environment variables from the file
        try:
            with open(self.env_file_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        self.vars[key] = value
        except FileNotFoundError:
            # If the file does not exist, create it
            with open(self.env_file_path, 'w') as f:
                pass
            print(f"Environment file {self.env_file_path} not found. Creating a new one.")
        except Exception as e:
            print(f"Error reading environment file: {e}")
    
    def getVar(self, var_name: str, default=None):
        if var_name in self.vars:
            return self.vars[var_name]
        return default
    
    def saveVar(self, var_name: str, value: str):
        self.vars[var_name] = value
        # Write all variables to the file
        try:
            with open(self.env_file_path, 'w') as f:
                for key, value in self.vars.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Error writing to environment file: {e}")


class ArgValue:
    def __init__(self, index: int, value: str, consume: bool = True):
        self.index = index
        self.value = value
        self.consume = consume


class CommandBuilder:

    def base(self, command: str) -> 'CommandBuilder':
        """
        Set the base command.
        """
        pass

    def getArg(self, index: int, default=None, error: str = None) -> 'ArgValue':
        """
        Get an argument by index.
        """
        pass

    def getFlag(self, flag: str, default=None, error: str = None) -> str:
        """
        Get a flag value.
        """
        pass

    def getFromEnv(self, var_name: str, default=None, error: str = None) -> str:
        """
        Get a variable from the environment.
        """
        pass

    def setFlag(self, flag: str, value: str, overwrite: bool = False) -> 'CommandBuilder':
        """
        Set a flag value.
        """
        pass

    def updateArg(self, index: int, func: callable) -> 'CommandBuilder':
        """
        Update an argument value.
        """
        pass

    def appendArg(self, arg: str) -> 'CommandBuilder':
        """
        Append an argument to the command.
        """
        pass

    def isSet(self, flag: str, requires_value: bool = False) -> bool:
        """
        Check if a flag is set.
        """
        return flag in self.flags
    
    def isNotSet(self, flag: str) -> bool:
        """
        Check if a flag is not set.
        """
        return flag not in self.flags
    
    def hasArg(self, index: int) -> bool:
        """
        Check if an argument exists at the given index.
        """
        return index > -1 and index < len(self.args)
    
    def notHasArg(self, index: int) -> bool:
        """
        Check if an argument does not exist at the given index.
        """
        return index < 0 or index >= len(self.args)

    def ifSet(self, flag: str, requires_value: bool = False) -> 'CommandBuilder':
        """
        Check if a flag is set.
        """
        pass

    def ifNotSet(self, flag: str) -> 'CommandBuilder':
        """
        Check if a flag is not set.
        """
        pass

    def ifHasArg(self, index: int) -> 'CommandBuilder':
        """
        Check if an argument exists at the given index.
        """
        pass

    def ifNotHasArg(self, index: int) -> 'CommandBuilder':
        """
        Check if an argument does not exist at the given index.
        """
        pass

    def saveToEnv(self, flag: str, env_var: str) -> 'CommandBuilder':
        """
        Save a flag to the environment.
        """
        pass

    def execute(self):
        """
        Execute the command.
        """
        pass


class EmptyCommandBuilder(CommandBuilder):
    
    def __bool__(self):
        return False

class OngoingCommandBuilder(CommandBuilder):
    """
    Class to build commands.
    """
    def __init__(self, args: list, env: Environment = None):
        self.base_command = ''
        self.flags = {}
        self.args = []
        self.env = env if env else Environment('~/.aliaspp/env')
        self.consumed_args = []

        # Parse incoming arguments
        i = 0
        while i < len(args):
            if args[i].startswith('-'):
                if args[i] == '--':
                    i += 1
                    continue
                if args[i][1] == '-':
                    flag = args[i][2:]
                else:
                    flag = args[i][1:]

                if '=' in flag:
                    flag, value = flag.split('=')
                    self.flags[flag] = value
                elif i + 1 < len(args) and not args[i + 1].startswith('-'):
                    self.flags[flag] = args[i + 1]
                    i += 1
                else:
                    self.flags[flag] = None
            else:
                self.args.append(args[i])
            i += 1

    def __bool__(self):
        return True
    
    def base(self, command: str) -> CommandBuilder:
        self.base_command = command
        return self
    
    def getArg(self, index: int, default=None, error: str = None, consume: bool = True) -> ArgValue:
        if index > -1 and index < len(self.args):
            return ArgValue(index, self.args[index], consume)
        
        if default is not None:
            return ArgValue(-1, default)
        
        _exit_with_error(error if error is not None else f"Argument at index {index} not found")
    
    def getFlag(self, flag: str, default=None, error: str = None) -> str:
        if flag in self.flags:
            return self.flags[flag]
        
        if default is not None:
            return default
        
        _exit_with_error(error if error is not None else f"Flag '{flag}' not set")
    
    def getFromEnv(self, var_name: str, default=None) -> str:
        return self.env.getVar(var_name, default)
    
    def setFlag(self, flag: str, value: str | ArgValue = None, overwrite: bool = False) -> CommandBuilder:
        if flag in self.flags and not overwrite:
            return self
        
        if isinstance(value, ArgValue):
            if value.consume:
                self.consumed_args.append(value.index)
            value = value.value

        self.flags[flag] = _clean_value(value)
        return self
    
    def updateArg(self, index: int, func: callable) -> CommandBuilder:
        if index > -1 and index < len(self.args):
            self.args[index] = _clean_value(func(self.args[index]))
            return self
        
        _exit_with_error(f"Argument at index {index} not found")
    
    def appendArg(self, arg: str) -> CommandBuilder:
        if arg is not None:
            self.args.append(_clean_value(arg))
        return self
    
    def isSet(self, flag: str, requires_value: bool = False) -> bool:
        return flag in self.flags and (not requires_value or self.flags[flag] is not None)
    
    def isNotSet(self, flag: str) -> bool:
        return flag not in self.flags
    
    def hasArg(self, index: int) -> bool:
        return index > -1 and index < len(self.args)
    
    def notHasArg(self, index: int) -> bool:
        return index < 0 or index >= len(self.args)

    def ifSet(self, flag: str, requires_value: bool = False) -> CommandBuilder:
        return self if self.isSet(flag, requires_value) else EmptyCommandBuilder()

    def ifNotSet(self, flag: str) -> CommandBuilder:
        return self if self.isNotSet(flag) else EmptyCommandBuilder()
    
    def ifHasArg(self, index: int) -> CommandBuilder:
        return self if self.hasArg(index) else EmptyCommandBuilder()
    
    def ifNotHasArg(self, index: int) -> CommandBuilder:
        return self if self.notHasArg(index) else EmptyCommandBuilder()
    
    def saveToEnv(self, flag: str, env_var: str) -> CommandBuilder:
        # Placeholder for saving to environment logic
        if flag not in self.flags:
            _exit_with_error(f"Cannot save {flag} to environment variable because it is not set")

        value = self.flags[flag]
        self.env.saveVar(env_var, value)
        return self

    def execute(self, dry_run=False):
        command = self.base_command.strip()
        if not command:
            raise ValueError("Base command is not set")
        
        if len(self.args) > 0:
            for i in self.consumed_args:
                if i < len(self.args):
                    self.args[i] = None
            self.args = [arg for arg in self.args if arg is not None]
            command += (' ' if len(self.args) > 0 else '') + ' '.join(self.args)

        for flag, value in self.flags.items():
            if len(flag) == 1:
                command += f' -{flag}'
            else:
                command += f' --{flag}'

            if value is not None:
                command += f' {value}'

        # Run the command
        if dry_run:
            print(command)
        else:
            os.system(command)

        # Reset command builder state
        self.base_command = ''
        self.flags = {}
        self.args = []
        self.consumed_args = []
        self.env = None