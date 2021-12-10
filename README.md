# Python Application for Vaccine Scheduler

This project is the 6th homework assignment for 
[CSE 414: Databases (Autumn 2021)](https://sites.google.com/cs.washington.edu/cse-414-21au/) led 
by Professor [Ryan Maas](https://homes.cs.washington.edu/~maas/) at the University of Washington.
Source code for the project can be found on this 
[Github repo](https://github.com/aaditya1004/vaccine-scheduler-python). Modifications beyond the
source code are of my own work.

## To Run the Project (Locally)

### Setting up the Environment

First clone the repository or download the files for this project. You will then need to install the
necessary Python packages (by running `pip install -r requirements.txt`). This project uses a custom
package specified in the `requirements.txt` as `-e .` to specify file routing (more details can be 
found [here](https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944)).

Note: if you have a **M1 Mac**, you may run into this error while running the application:
```shell
ImportError: dlopen(/file-directory/venv/lib/python3.7/site-packages/pymssql.cpython-37m-darwin.so, 0x0002): Library not loaded: /usr/local/opt/freetds/lib/libsybdb.5.dylib
  Referenced from: /file-directory/venv/lib/python3.7/site-packages/pymssql.cpython-37m-darwin.so
  Reason: tried: '/usr/local/opt/freetds/lib/libsybdb.5.dylib' (no such file), '/usr/local/lib/libsybdb.5.dylib' (no such file), '/usr/lib/libsybdb.5.dylib' (no such file)
```

To fix it, first install Rosetta 2 if you haven't already 
`/usr/sbin/softwareupdate --install-rosetta --agree-to-license`. Then install `freetds` through 
[Brew](https://brew.sh/) with `arch -x86_64 brew install freetds`.

### Running the Application

Before you can run the application, you must add your database details to your local environment. 
Open up terminal and input the following:
```shell
export Server=server.database.windows.net
export DBName=dbname
export UserID=username
export Password=password
```
You can verify that these details are added to your local environment by running `printenv` in 
terminal.

Note: you must add your database details to your local environment **every time** you run the 
application.

Once you have entered your database details, navigate to `src/main/scheduler` and run
`python3 Scheduler.py`.

## Acknowledgements
I would like to give a huge thanks to the CSE 414 21au Course Staff for the help they provided in
the course in my learning of everything databases. Special thanks to Aadi Jain, Stephanie Zhang, 
and Steve Ma, for all their support in getting this project up and running (and Professor Ryan 
Maas for issuing me additional Azure credits when I spent $18 over the $70 limit 🙃).