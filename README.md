# Python DDD Skeleton
This is a simple skeleton to build DDD projects in Python. The project is build on top of Flask framework and written in Python version 3.9

## Installation

### Software requirements
To run the project you need the following:
* Pip: https://pip.pypa.io/en/stable/installation/
* Docker: https://docs.docker.com/engine/install/
* Docker Compose: https://docs.docker.com/compose/install/ 

Once the dependencies specified above are installed, follow the steps below.

Clone the project:
```
$ git clone git@github.com:fdelgados/python-ddd-skeleton.git my-python-ddd-project
```

Or you can fork the repository to one of your own.

Set up the project:

```
$ cd my-python-ddd-project
$ chmod a+x setup-project.sh
$ ./setup-project.sh
```

To run the Docker containers

```
$ make all
```
