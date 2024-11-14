# independent-mc
A tool to download and run minecraft fully portable on all Windows computers. Uses portablemc for python as basis.

## Basic "How to use"
*First of all: You need to have python installed!*  
*If your python executable is on path and the script still does not work, consider upgrading python and/or pip.*  

Download the repo to the directory you want to install Minecraft to. That might also be a removable drive.  
If you want, adjust the settings at the top of the `download.bat` file.  
Then execute it by double-clicking. The script now does everything for you.  

Once finished, you should have a `start.bat` file to start the game.  

**Happy gaming!**

## Install mods, resourcepacks etc.
In the "additional-content-downloader" there are two folders, "project-templates" and "projects-txt-generator".  
If you would like to install mods, resourcepacks, shaders or datapacks automatically, there are currently three options:  
1. You can add them to the `projects.txt` yourself (further instructions in the example file).
2. You can take a pre-made template from the "project-templates" folder.
3. You can copy an exported modpack from Modrinth into "projects-txt-generator" and execute the `generate.py` script. This will generate a projects file for you.  

<!-- end of the list -->


Note that the file you want to use has to be called `projects.txt` and be in the same folder as the `download.bat` file.  
Also, the "install_mods" option in `download.bat` has to be set to "true".  

## Issues
If you encounter any issues, try to fix them on their own first.  
Then open an issue here and if you have, describe the solution.

## Contributing
Contributing is not wanted. This program is meant to work as-is.  
I only published it to not gatekeep the idea and structure of the code.  
If you want alpha and beta versions to be included, missing dependency versions to be handled in a better way etc. you can of course style the script to your needs.
