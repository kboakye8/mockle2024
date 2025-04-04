# Flask Starter Template fo REPLit
A template for simple flask projects. For production projects with testing and deployment it is recommended to use [flaskmvc](https://gitpod.io/#https://github.com/uwidcit/flaskmvc).

# Installing Dependencies
```
$ pip install -r requirements.txt 
```
For repl just click on the RUN button instead.


# Flask Commands

wsgi.py is a utility script for performing various tasks related to the project. You can use it to import and test any code in the project. 
You just need create a manager command function, for example:

```
# inside wsgi.py

@app.cli.command("create-user")
@click.argument("username")
@click.argument("password")
def create_user_command(username, password):
    newuser = User(username=username, password=password)
    db.session.add(newuser)
    db.session.commit()
    print(f'{username} created!')
```

Then execute the command invoking with flask cli with command name and the relevant parameters

```
$ flask create-user bob bobpass
```


# Running the Project

_Replit is configured to execute the following command to run the project:_
```
$ flask run
```

# Initializing the Database
When connecting the project to a fresh empty database ensure the appropriate configuration is set then file then run the following command. This must aslo be executed once when running the app on heroku by opening the heroku console, executing bash and running the command in the dyno.

```
$ flask init
```