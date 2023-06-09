'rhythmonics' is a portmanteau of rhythm and harmonics and, true to its name, is a music toy meant to show the relationship between polyrhythms and harmony.

This project is an interactive GUI that visualizes polyrhythms and allows a sliding scale of speed to auditorily and visually show how harmony is just really fast polyrhthms!

An understanding of overtones/harmonics and of polyrhythms is useful but not required.  This interactive toy is meant to make the concepts intuitive and palatable just by graphically playing with it!

## Warning
This application has fast and strobing movement and may trigger photo-sensitive epilepsy.  Future versions will have an option to minimize movement but this is not available now.

## Installation
Clone the project

Have python3

In the directory you've placed rhythmonics, it is recommended you create and activate a virtual environment to make sure rhythmonics uses the right versions of the libraries it was built with:

`python3 -m venv .venv`

`source .venv/bin/activate`

With an active virtual environment, use the `requirements.txt` file here to install all the libraries that rhythmonics depends on:

`pip install -r requirements.txt`

The main event loop that powers rhythmonics should be ready to run now:

`python3 main.py`