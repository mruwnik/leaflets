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
`python setup.py install`

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

* To run tests, call:

`pip install -e  '.[tests]'` to initially set everything up, after which `py.test` will run all tests

# Fake data

To make it easier to get up and running, it is possible to recreate the database with a single command:
`python leaflets/dev.py recreate`
This command will drop the existing database and recreate it, filling it with fake data. The default credentials are:

* username: user
* password: password

To make it easier to view the database, there is a preconfigured IPython instance that can be started via `python leaflets/dev.py shell`

# i18n

The basics are outlined in [the gettext documentation](https://docs.python.org/3/library/gettext.html). The general idea is for each language to have their own entry in `leaflets/locale` where each string in the program has its own entry. This has to be manually maintained, which is a hassle, but there you are. After updating a translations file (`messages.pot`), it has to be compiled to a machine readable form. This is done by executing `msgfmt messages.pot` in the folder with the translations. Once that is done, it should suffice to restart the application for the new translations to be used.
To compile all locales at once, call `python leaflets/dev.py translate`

# Users structure

There are 2 kinds of users:
* normal users can view campaigns that are assigned to them and mark addresses as done
* administrators can add new users, create campaigns and do everything normal users can do

Users are hierarchical. The highest level users are organisations. Organisations don't see each other. Each organisation can create users that belong to it. Admin users can create other users that are either equal or subjected to them. Subjected users create a sort of sub-organisation and can only see campaigns and users belonging to the parent user.
