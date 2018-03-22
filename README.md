# ChemHelper Graphical User Interface

[![Build Status](https://travis-ci.org/not-na/chem-helper.svg?branch=master)](https://travis-ci.org/not-na/chem-helper)

This repository contains the GUI part of the ChemHelper package.
For this reason, it is mandatory to also install the [`chemhelper`](https://github.com/not-na/chem-helper) module
when running directly from the source code.

## Installation from Pre-Compiled Binaries

The pre-compiled binaries found under the [Releases Tab](https://github.com/not-na/chemhelper-gui/releases) do not need to be installed nor do they require any dependencies.
They can simply be started by double-clicking on the executable file.

Note for older Windows versions:

Under certain older releases, the Universal C Runtime (UCRT) may be required if you receive a warning that it was not found.
The UCRT is available for download from [Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=48234).

## Installation from Source

This guide assumes that you have already installed [Python 3.6](https://www.python.org/downloads/release/python-364/) and
that you use Ubuntu or a similar Linux Distribution.

First, clone this repository, its submodules and [`chemhelper`](https://github.com/not-na/chem-helper).
    
    mkdir chemhelper
    cd chemhelper
    git clone git://github.com/not-na/chemhelper-gui.git
    cd chemhelper-gui
    git submodule update --init --recursive
    cd ..
    git clone git://github.com/not-na/chem-helper.git

Then, create a [virtualenv](https://virtualenv.pypa.io/en/stable/) to house all of the other dependencies:
   
    python3.6 -mvenv chemhelper-py3.6

To finalize the installation, activate the virtualenv and install all of the dependencies:
   
    source chemhelper-py3.6/bin/activate
    pip install -r chemhelper-gui/requirements.txt
    pip install -r chem-helper/requirements.txt
    pip install git+git://github.com/not-na/peng3d.git

Note that peng3d is currently installed from the repository because ChemHelper uses some features not yet released to PyPI.

`ChemHelper` is now installed, see the next section for instructions on starting the program.

## Running from Source

This section assumes that you have successfully completed all of the steps in the above section.

If you closed your terminal after installation, re-activate the virtualenv:
    
    source chemhelper-py3.6/bin/activate

To run the application, execute the following commands:
   
    cd chemhelper-gui
    python main.py [optional filename]

## Compiling Executables for Linux

If you want to create your own executable to distribute, you can simply use the `build_pyinstaller.sh` script.

Note that you will need to be "in" the virtualenv and the correct folder before running the script:
    
    source chemhelper-py3.6/bin/activate # Only run this if the virtualenv has not been activated
    cd chemhelper-gui # Only run this if you are not in the correct folder already
    ./build_pyinstaller.sh

The final executable file can be found under `chemhelper-gui/dist/ChemHelper`.

## Compiling Executables for Windows

Coming soon.
Some tips for now:
- Use the Virtual Machines provided by Microsoft here: [Microsoft Edge Development](https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/)
- Download Python 3.6 and Git Bash
- Create a shared folder
- Use the copy_for_winbuild.sh script to create a directory to copy to the VM
- Run `source build_pyinstaller_win.sh` using Git Bash running with Administrator Privileges
- Note: Script does not show output at the start, but is still active. Be patient.
