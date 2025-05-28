__package__ = "aliaspp"
__version__ = "0.1.0"

import sys
import os
from typing import List, Tuple, Callable
from enum import Enum

_aliases = {}

def _add_alias(alias_name: str, func: Callable[['CommandBuilder'], None]):
    """
    Add an alias to the global aliases dictionary.
    """
    if alias_name in _aliases:
        raise ValueError(f"Alias '{alias_name}' already exists")
    _aliases[alias_name] = func

def _crate_alias_func(alias_base: str, func: Callable[['CommandBuilder'], None] = None) -> Callable[['CommandBuilder'], None]:
    """
    Create a function that sets the base command and calls the provided function.
    """
    def alias_func(cb: 'CommandBuilder'):
        cb.base(alias_base)
        if func is not None:
            func(cb)
    return alias_func

def alias(alias = None):
    """
    Decorator to define an alias for a command.
    """
    def decorator(func):
        if not callable(func):
            raise ValueError("Alias is not a function")
        
        if isinstance(alias, str):
            alias_name = alias.strip()
            _add_alias(alias_name, func)
            return func
        elif isinstance(alias, dict):
            # If alias is a dictionary, it means multiple aliases are defined
            funcs = {}
            for alias_name, base_command in alias.items():
                current_alias_func = _crate_alias_func(base_command, func)
                _add_alias(alias_name, current_alias_func)
                funcs[alias_name] = current_alias_func
            return funcs

    if isinstance(alias, str) or isinstance(alias, dict):
        # If alias is a string or dict, it's because the decorator is used with parentheses
        return decorator
    elif callable(alias):
        # If alias is a callable, it's because the decorator is used without parentheses
        alias_name = alias.__name__
        _add_alias(alias_name, alias)
        return alias
    else:
        raise ValueError("Alias must be a string, a dictionary, or a callable function")

def aliases(alias_dict: dict = None):
    """
    Function to define multiple simple aliases at once by passing a dictionary of alias names and their base commands.
    """
    if alias_dict is None:
        return

    for alias_name, alias_base in alias_dict.items():
        _add_alias(alias_name, _crate_alias_func(alias_base))

def execute(env=None, dry_run=False):
    """
    Execute the command with the given environment.
    """
    if len(sys.argv) < 2:
        print("No command provided")
        return

    args = sys.argv[2:]
    cb = OngoingCommandBuilder(args, env)

    for alias_name, func in _aliases.items():
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
        self.env_file_path = os.path.abspath(os.path.expanduser(env_file_path))

        dir_path = os.path.dirname(self.env_file_path)
        if dir_path and not os.path.isdir(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
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

    def _write_env_file(self):
        """
        Write the current environment variables to the file.
        """
        try:
            with open(self.env_file_path, 'w') as f:
                for key, value in self.vars.items():
                    f.write(f"{key}={value}\n")
        except Exception as e:
            print(f"Error writing to environment file: {e}")
    
    def get_var(self, var_name: str, default=None) -> str:
        if var_name in self.vars:
            return self.vars[var_name]
        return default
    
    def save_var(self, var_name: str, value: str):
        self.vars[var_name] = value
        self._write_env_file()

    def clear_var(self, var_name: str):
        if var_name in self.vars:
            del self.vars[var_name]
            self._write_env_file()


class ValueRequirement(Enum):
    """
    Enum to indicate whether a value is required for a flag.
    """
    NOT_REQUIRED = 0  # No value required, e.g., -f
    REQUIRE_VALUE = 1  # Value required, e.g., -f value
    REQUIRE_NO_VALUE = 2  # No value allowed, e.g., -f without a value
    

class CommandBuilder:

    def base(self, command: str) -> 'CommandBuilder':
        """
        Set the base command.
        """
        return self

    def get_arg(self, index: int, default=None, error: str = None, consume: bool = True) -> str:
        """
        Get an argument by index.
        """
        pass

    def get_flag(self, flag: str, default=None, error: str = None) -> str:
        """
        Get a flag value.
        """
        pass

    def set_flag(self, flag: str, value: str, overwrite: bool = True, dashes: int = 0) -> 'CommandBuilder':
        """
        Set a flag value.
        If `overwrite` is False, it will not overwrite an existing flag.
        If `value` is None, it will set the flag without a value.
        If `dashes` is provided, it determines the number of dashes:
        - 1: single dash (e.g., -f)
        - 2: double dash (e.g., --flag)
        - else: default behavior based on flag length
        """
        return self
    
    def remove_flag(self, flag: str) -> 'CommandBuilder':
        """
        Delete a flag.
        """
        return self

    def update_arg(self, index: int, func: callable) -> 'CommandBuilder':
        """
        Update an argument value.
        """
        return self

    def append_arg(self, arg: str) -> 'CommandBuilder':
        """
        Append an argument to the command.
        """
        return self

    def append_command(self, base: str, append_operand='&&') -> 'CommandBuilder':
        """
        Append a new command to the end of the current command.
        Return a new CommandBuilder for the appended command.
        """
        return self

    def is_set(self, flag: str, value_requirement: ValueRequirement = ValueRequirement.NOT_REQUIRED) -> bool:
        """
        Check if a flag is set.
        """
        return False
    
    def is_not_set(self, flag: str) -> bool:
        """
        Check if a flag is not set.
        """
        return False
    
    def has_arg(self, index: int) -> bool:
        """
        Check if an argument exists at the given index.
        """
        return False
    
    def not_has_arg(self, index: int) -> bool:
        """
        Check if an argument does not exist at the given index.
        """
        return False

    def if_set(self, flag: str, value_requirement: ValueRequirement = ValueRequirement.NOT_REQUIRED) -> 'CommandBuilder':
        """
        Check if a flag is set.
        """
        return self

    def if_not_set(self, flag: str) -> 'CommandBuilder':
        """
        Check if a flag is not set.
        """
        return self

    def if_has_arg(self, index: int) -> 'CommandBuilder':
        """
        Check if an argument exists at the given index.
        """
        return self

    def if_not_has_arg(self, index: int) -> 'CommandBuilder':
        """
        Check if an argument does not exist at the given index.
        """
        return self
    
    def get_from_env(self, var_name: str, default=None, error: str = None) -> str:
        """
        Get a variable from the environment.
        """
        pass

    def save_to_env(self, flag: str, env_var: str) -> 'CommandBuilder':
        """
        Save a flag to the environment.
        """
        return self

    def clear_from_env(self, env_var: str) -> 'CommandBuilder':
        """
        Clear a variable from the environment.
        """
        return self
    
    def build_command(self) -> str:
        """
        Build the command string.
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
        self.appended_commands: List[Tuple[CommandBuilder, str]] = []
        self.env = env if env else Environment('~/.aliaspp/env')
        self.consumed_args = []

        # Parse incoming arguments
        i = 0
        while i < len(args):
            if args[i].startswith('-'):
                if args[i] == '--':
                    self.args.append(args[i])
                    i += 1
                    continue

                double_dash = False
                if args[i][1] == '-':
                    flag = args[i][2:]
                    double_dash = True
                else:
                    flag = args[i][1:]

                if '=' in flag:
                    flag, value = flag.split('=')
                    self.flags[flag] = (value, double_dash)
                elif i + 1 < len(args) and not args[i + 1].startswith('-'):
                    self.flags[flag] = (args[i + 1], double_dash)
                    i += 1
                else:
                    self.flags[flag] = (None, double_dash)
            else:
                self.args.append(args[i])
            i += 1

    def __bool__(self):
        return True
    
    def base(self, command: str) -> CommandBuilder:
        self.base_command = command
        return self
    
    def get_arg(self, index: int, default=None, error: str = None, consume: bool = True) -> str:
        if index > -1 and index < len(self.args):
            if consume and index not in self.consumed_args:
                self.consumed_args.append(index)
            return self.args[index]
        
        if error is not None and default is None:
            _exit_with_error(error)

        return default
    
    def get_flag(self, flag: str, default=None, error: str = None) -> str:
        if flag in self.flags:
            return self.flags[flag][0]
        
        if error is not None and default is None:
            _exit_with_error(error)

        return default
    
    def set_flag(self, flag: str, value: str = None, overwrite: bool = True, dashes: int = 0) -> CommandBuilder:
        if flag in self.flags and not overwrite:
            return self

        double_dash = len(flag) > 1
        if dashes > 0:
            if dashes > 2:
                _exit_with_error("Dashes must be 0, 1, or 2")
            double_dash = dashes == 2
        
        self.flags[flag] = (_clean_value(value), double_dash)
        return self
    
    def remove_flag(self, flag: str) -> CommandBuilder:
        if flag in self.flags:
            del self.flags[flag]
        return self
    
    def update_arg(self, index: int, func: callable) -> CommandBuilder:
        if index > -1 and index < len(self.args):
            self.args[index] = _clean_value(func(self.args[index]))
            return self
        
        _exit_with_error(f"Argument at index {index} not found")
    
    def append_arg(self, arg: str) -> CommandBuilder:
        if arg is not None:
            self.args.append(_clean_value(arg))
        return self
    
    def append_command(self, base: str, append_operand='&&') -> CommandBuilder:
        if base is None:
            raise ValueError("Base command is not set")
        
        new_command = OngoingCommandBuilder([], self.env)
        new_command.base(base)
        self.appended_commands.append((new_command, append_operand))
        return new_command
    
    def is_set(self, flag: str, value_requirement: ValueRequirement = ValueRequirement.NOT_REQUIRED) -> bool:
        flag_exists = flag in self.flags
        if not flag_exists:
            return False
        
        has_value = self.flags[flag][0] is not None    
        if value_requirement == ValueRequirement.REQUIRE_VALUE:
            return has_value
        elif value_requirement == ValueRequirement.REQUIRE_NO_VALUE:
            return not has_value
        
        return True
    
    def is_not_set(self, flag: str) -> bool:
        return flag not in self.flags
    
    def has_arg(self, index: int) -> bool:
        return index > -1 and index < len(self.args)
    
    def not_has_arg(self, index: int) -> bool:
        return index < 0 or index >= len(self.args)

    def if_set(self, flag: str, value_requirement: ValueRequirement = ValueRequirement.NOT_REQUIRED) -> CommandBuilder:
        return self if self.is_set(flag, value_requirement) else EmptyCommandBuilder()

    def if_not_set(self, flag: str) -> CommandBuilder:
        return self if self.is_not_set(flag) else EmptyCommandBuilder()
    
    def if_has_arg(self, index: int) -> CommandBuilder:
        return self if self.has_arg(index) else EmptyCommandBuilder()
    
    def if_not_has_arg(self, index: int) -> CommandBuilder:
        return self if self.not_has_arg(index) else EmptyCommandBuilder()
    
    def get_from_env(self, var_name: str, default=None) -> str:
        return self.env.get_var(var_name, default)
    
    def save_to_env(self, flag: str, env_var: str) -> CommandBuilder:
        if flag not in self.flags:
            _exit_with_error(f"Cannot save {flag} to environment variable because it is not set")

        value = self.flags[flag][0]
        self.env.save_var(env_var, value)
        return self
    
    def clear_from_env(self, env_var: str) -> CommandBuilder:
        self.env.clear_var(env_var)
        return self
    
    def build_command(self) -> str:
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
            if flag == 'alias-dry-run':
                continue

            value, double_dash = value
            if double_dash:
                command += f' --{flag}'
            else:
                command += f' -{flag}'

            if value is not None:
                command += f' {value}'

        for appended_command, append_operand in self.appended_commands:
            appended_command_str = appended_command.build_command()
            if appended_command_str:
                command += f' {append_operand} {appended_command_str}'

        return command

    def execute(self, dry_run=False):
        command = self.build_command()

        if 'alias-dry-run' in self.flags:
            dry_run = True

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