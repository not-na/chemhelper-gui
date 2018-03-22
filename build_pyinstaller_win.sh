# If you want to be able to use the virtualenv after running this script, use source
# Must be run from the gui/ folder

winpty python -mvenv chemhelper-py3.6
. chemhelper-py3.6/Scripts/activate

pip install -r req_winbuild.txt
pip install git+git://github.com/not-na/peng3d.git

pyinstaller --clean \
            --noconfirm \
            --onefile \
            --windowed \
            --name ChemHelper \
            --icon './assets/chemhelper/icon_256.ico' \
            --add-data './assets/;assets/' \
            main.py
