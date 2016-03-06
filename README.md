# leaflets
A website to handle door-to-door leaflets


# Environment setup

* Postgres

Start out by setting up postgres on your local machine. [this guide](https://wiki.postgresql.org/wiki/Detailed_installation_guides) seems to decribe how. [here](https://wiki.postgresql.org/wiki/First_steps) you can see how to access it from the command line.
Once you have postgres set up, create the leaflet's database and user:

```
CREATE SCHEMA leaflets;
CREATE USER leaflets PASSWORD 'leaflets';
GRANT ALL ON SCHEMA leaflets TO leaflets;
CREATE DATABASE leaflets;
```

* Get the code

Check out the code from the github repo:

`git clone https://github.com/mruwnik/leaflets`

* Set up python

The project uses Python 3.5, so make sure you have it installed. Once that is done, you can set up the development environment. The basic way is to simply execute the following (make sure that the python path is set correctly):

```
pip install virtualenv
virtualenv venv --python=/usr/local/bin/python3.5
```

which will create a virtual enviroment for this project, where you can install and remove packets however you like - it will have no effect on the rest of the system. To use it, execute:

`source venv/bin/activate`

A more friendly alternative is [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)

* Install dependancies

To install all the required packages, go to wherever the project is and execute the following for it all to be automatically downloaded and installed:
`pip install -r requirements.txt`

* Run the database migrations

For there to be any data in the database, you must run the migrations. Go to the project directory that you cloned from github, and do the following:

```
cd leaflets
alembic upgrade head
```

* Local settings

If you want to specify any personal settings, create a file called `leaflets/etc/local.py` and add them there. The settings must already be present in `leaflets/etc/__init__.py` to be actually seen by the project. This step is totally optional, as the defaults should be good enough. A good use of this file is to set debugging on. To do so, just add the following line to your `local.py` file:
`DEBUG = True`

* Run the project

Execute the following from the project directory:
`python leaflets/views.py`

* Check whether it works

Open `localhost:5000` in your browser to see if the webpage is working.

