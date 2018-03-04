# Clean old folder
rm -Rf ../win_tmpbuild

# Create new folder
mkdir ../win_tmpbuild

# Copy GUI
cp -R ./* ../win_tmpbuild/

# Remove symlinks
rm ../win_tmpbuild/chemhelper
rm ../win_tmpbuild/pyfileselect

# Add libraries
cp -R ../algo/chemhelper/ ../win_tmpbuild/
cp -R ../win_tmpbuild/pyfileselect-git/pyfileselect/ ../win_tmpbuild/

# Add Dependency script
pip freeze | grep -v "peng3d" > ../win_tmpbuild/req_winbuild.txt

# Cleanup
rm -R ../win_tmpbuild/build ../win_tmpbuild/dist ../win_tmpbuild/pyfileselect-git
