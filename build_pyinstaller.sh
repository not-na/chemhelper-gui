rm dist/ChemHelper

pyinstaller --clean \
            --onefile \
            --windowed \
            --name ChemHelper \
            --add-data './assets/:assets/' \
            main.py
