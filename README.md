# Python-MvcCgi
A very simple framework for teaching the principles of MVC Web Applications.  This is not a fully featured, robust framework, but rather one that is designed to be easy to use.  It extends the CGI HttpRequestHandler built in to Python 3.6, and should never be used for a "real" web application.

## Installation ##
There are two distinct releases for the project - the MvcCgi release is the package that provides all of the functionality you need, and the 'demosite' release is an example of an application that is built with the McvCgi framework. The demosite is not necessary for the library to work, but it's a useful starting point.

### Installing the package ###

You need to know how to use a terminal (OSX, Linux) / Command Prompt (Windows) in order to install the package. If you're not comfortable with moving around the file-system, ask someone for help! Additionally, you will want to make sure that the version / environment you run python from in terminal is the same as the version you use to develop your code.  Finally, this package has only been tested in Python 3.6.3, and will definitely not work in Python 2.

1. Download the lastest release from the [releases](https://github.com/jintrone/Python-MvcCgi/releases) page
2. Unzip the folder somewhere convenient
3. Open up a terminal and navigate to that folder.
4. Type the command:

```bash
$ python setup.py install
```
5. Congratulations, you've installed the package!


### Installing the demosite ###

1. Download the latest demosite from the [releases](https://github.com/jintrone/Python-MvcCgi/releases) page
2. Unzip the file somewhere convenient (maybe somewhere where you like to edit code).

## Running the demo ##

You can run the demo from the command prompt, or using a script. It is important that your working directory is the same directory where the ```controller.py``` file is located.  Your working directory is usually where you execute the python command.

1.  Edit the [first line](https://github.com/jintrone/Python-MvcCgi/blob/5d95a53a27da4a7a37d7c38f85c75af14294be52/demosite/controller.py#L1) of the ```controller.py``` file to point to a path that resolves to your python command.  Be sure to include the ```#!``` - this tells the operating system to use the following program to execute this script (note that this line is not always necessary on Windows if your OS knows how to run .py files).
2.  If on linux / osx open a terminal and make the script executable by typing:
```bash
$ chmod 755 controller.py
```
3. *To run from the terminal / command prompt* - From the same directory, run:
```bash
$ python -m mvc.server controller.py
```
4. *To run from a script or python console* - execute the following:
```python
import mvc.server
mvc.server.main()
```
5. You should see some output indicating that the server is running; open a web browser to http://localhost:8080/home.html

Hope this is useful, and have fun!


