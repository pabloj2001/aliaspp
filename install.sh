# !/bin/bash

CWD=$(pwd)

# If .aliaspp directory does not exist, create it
if [ ! -d ~/.aliaspp ]; then
    mkdir ~/.aliaspp
fi

# If aliaspp.py does not exist, download it
if [ ! -f ~/.aliaspp/aliaspp.py ]; then
    curl -o ~/.aliaspp/aliaspp.py https://raw.githubusercontent.com/pabloj2001/aliaspp/main/aliaspp.py
fi

# If aliaspp file provided in argument
if [ -n "$1" ]; then
    # Copy to .aliaspp directory
    cp "$1" ~/.aliaspp/

    cd ~/.aliaspp || exit

    # Run install-aliases
    python3 ~/.aliaspp/$(basename "$1") --install-aliases
fi

cd $CWD
echo "Installation complete. You can now create aliases using aliaspp."