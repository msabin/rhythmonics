# rhythmonics
'rhythmonics' is a portmanteau of rhythm and harmonics and, true to its name, is a music toy meant to show the relationship between polyrhythms and harmony.

This project is an interactive GUI that visualizes polyrhythms and allows a sliding scale of speed to auditorily and visually show how harmony is just really fast polyrhthms!

An understanding of overtones/harmonics and of polyrhythms is useful but not required.  This interactive toy is meant to make the concepts intuitive and palatable just by graphically playing with it!

## Warning
This application has fast and strobing movement and may trigger epilepsy for those with photo-sensitive epilepsy.  Future versions will have an option to minimize movement but this is not available now.

## Installation
This is a Python project and requires Python 3 to run.  These installation instructions should work for MacOS with the default shell.

Open a directory on your computer that you want to download this repository to and clone it from GitHub from the command line with:

`git clone https://github.com/msabin/rhythmonics.git`

In the directory you've placed rhythmonics, it is recommended you create and activate a virtual environment to make sure rhythmonics uses the right versions of the libraries it was created with:

`python3 -m venv .venv`

`source .venv/bin/activate`

With an active virtual environment, use the `requirements.txt` file here to install all the libraries that rhythmonics depends on:

`pip install -r requirements.txt`

The main event loop that powers rhythmonics should be ready to run now:

`python3 main.py`

## File Structure

There are four files of Python code that organize the code's components as follows:

**main.py**
Run the main event loop for the rhythmonics program.

**harmonics.py**
Module for simulating all harmonic components: sound, polygons, balls.

**interface.py**
Module for the GUI of rhythmonics, wrapped in a console aesthetic.

**config.py**
Global constants (mostly colors) for the program to use.

