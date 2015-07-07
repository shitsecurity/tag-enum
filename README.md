# Summary

Enumerate web application software versions based on hashed static content from localy parsed git repositories with as few requests to the server as possible.

# Installation

Install pip and virtualenv.

```
sudo apt-get install python-pip python-virtualenv
```

Create a virtual environment.

```
virtualenv env
```

Activate the virtual environment.

```
. env/bin/activate
```

Install the modules to the virtual environment.

```
pip install -r requirements.txt
```

Install git.

```
sudo apt-get install git
```

Install mysql.

```
sudo apt-get install mysql mysql-server libmysqlclient-dev
```

Create the database (`mysql -u <user> -p < mysql.sql`).

```
CREATE DATABASE enum_cms CHARACTER SET utf8 COLLATE utf8_bin;
```

Add the database credentials to the config.yaml db section.

Edit the config.yaml repos section to include the relevant repositories.

Clone and parse the git repositories.

```
./enum.py --setup --parse
```

Don't forget to check --help.

# Usage

List all available cms.

```
./enum.py --list
```

Try to identify an application's version using a specific cms.

```
./enum.py --identify --target 192.168.0.1/ --cms Drupal
```

Try to identify an application's version using all available cms.

```
./enum.py --identify --target 192.168.0.1/
```
