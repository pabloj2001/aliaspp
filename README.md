# alias++
This library/CLI allows you to create advanced bash aliases with minimal code. 

Created by Pablo AC

## Installation
Must have Python 3 installed.

Run the following one-liner to install aliaspp to `~/.aliaspp`:
```bash
sh -c "$(wget -O- https://raw.githubusercontent.com/pabloac/aliaspp/main/install.sh)"
```

You can install it with your custom aliases by providing your script path:
```bash
sh -c "$(wget -O- https://raw.githubusercontent.com/pabloac/aliaspp/main/install.sh)" -- /path/to/your_script.py
```

You can also install your aliases later by coping your script to `~/.aliaspp/` and running:
```bash
python3 ~/.aliaspp/your_script.py --install-aliases
```

## Usage
See `sample.py` for how to set up your aliaspp script to define your aliases.