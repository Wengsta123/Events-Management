# Product Deployment Instructions

- Login to the server via SSH

```bash
$ ssh ubuntu@paris.cs.virginia.edu -p22165
```

For security reasons, the password will not be provided here. You can email [lat9nq@virginia.edu](mailto:lat9nq@virginia.edu) for the password.

- Navigate to the `Events-Management` folder.

```bash
$ cd ~/Events-Management/
```

- Run `git pull` in the Events-Management directory

- Run `source virtualenv/bin/activate`

- Navigate to Events-Management/src/events\_management/

```bash
$ cd src/events\_management/
```

- Run `screen ./manage.py runserver 10.1.1.165:8000`

```bash
$ screen ./manage.py runserver 10.1.1.165:8000
```

- Press C^A, C^D to exit the `screen`

- Exit the ssh session. If the [server is running](http://128.143.71.210:28165/login/), then you are done.

