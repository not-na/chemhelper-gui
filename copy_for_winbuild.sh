# Clean old folder
rm -Rf ../win_tmpbuild/

# Create new folder
mkdir ../win_tmpbuild/
mkdir ../win_tmpbuild/ch/

# Copy GUI
cp -R ./* ../win_tmpbuild/ch/

# Remove symlinks
rm ../win_tmpbuild/ch/chemhelper
rm ../win_tmpbuild/ch/pyfileselect

# Add libraries
cp -R ../algo/chemhelper/ ../win_tmpbuild/ch/
cp -R ../win_tmpbuild/ch/pyfileselect-git/pyfileselect/ ../win_tmpbuild/ch/

# Add Dependency script
pip freeze | grep -v "peng3d" > ../win_tmpbuild/ch/req_winbuild.txt

# Cleanup
rm -R ../win_tmpbuild/ch/build ../win_tmpbuild/ch/dist ../win_tmpbuild/ch/pyfileselect-git
