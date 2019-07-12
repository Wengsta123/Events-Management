Events Management                                                                            Spring 2019
Installation Instructions
Assumptions:
For the purposes of this document, it will be assumed that the reader has an available server with the following characteristics:
* Operating System: Ubuntu 16.04 or later
* User has root (sudo) access
* The computer has an internet connection
Installing Necessary Programs
Once the server is turned on and a terminal window has been opened, the following commands should be executed to set up the environment that the application needs in order to run. 


All of these are programs and tools that will be necessary for the application to run. Please run the following commands one by one to install them. 
If you are prompted to authorize the programs to occupy memory while the installation is ongoing, please answer yes by typing "y" into the terminal when prompted.


sudo apt-get update

sudo apt-get install python3-pip git screen gcc make

pip3 install --upgrade pip virtualenv

virtualenv events-env

source events-env/bin/activate
	

Downloading the Code
For your convenience, a .zip file has been put at your disposal, which contains the entire contents of the Github repository where the code for the application is found. To download this file, click this link:
https://drive.google.com/file/d/1v2aQG5UXw-zKarf0HZrGuyGkpivhTLZu/view?usp=sharing 
And download the file at that location.


You must then extract the file so that it can be treated as a regular folder in your system. Then, execute the following command from your terminal to change your current directory to the correct one for running the app.


cd Events-Management/src/events_management/
	

Installing Modules and Other Tools
In order to run correctly, the application needs a set of python modules and tools that will enable certain functionalities in the website. Execute the following commands one by one from your terminal window.
If you are prompted to authorize the programs to occupy memory while the installation is ongoing, please answer yes by typing "y" into the terminal when prompted.


pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib reportlab django oauth2client
	

Allowing Host Address
In order for the app to run without errors, it must be able to recognize the current server as one of the "allowed hosts". To do this, navigate to the following path:


Events-Management/src/events_management/events_management/
	

Then, open the settings.py file using the text editor of your choice. Scroll down to find the list titled "ALLOWED_HOSTS"  and modify it to add the Public DNS address of your server. The resulting code should look like this:


ALLOWED_HOSTS = ["10.1.1.165", 
               "128.143.71.210", 
               '127.0.0.1',
               "localhost",
               "your-public-dns-address"]
	

Starting the Server
You have now installed all the required tools and programs, and completed the setup that will allow the app to run. Now, let's start the server. To do so, navigate to:

Events_Management/src/events_management/
	

Now, we must migrate the database. Run the following commands one at a time:


python manage.py makemigrations

python manage.py migrate
	

Once we have done this, we can run the following command. Please note that this command will run inside a SSH session.


screen python3 manage.py runserver
	

* Please, make a note of the URL that will appear on the screen once the server starts running. You will need to give this URL to those who wish to use the website. 


The tool named "screen" will allow you move away from this process which is running on your terminal by pressing the keys Ctrl + A and then Ctrl + D. This will leave the server running in the background, and allow you to continue using your terminal window for other tasks.


Setting Up the Application
Now that the server is running, it is necessary to complete a few steps to allow users to log into the site. Begin by creating a superuser. To do so, run the following command:


python3 manage.py createsuperuser
	

You will then be prompted for a username, an email address, and a password. We recommend that you use generic values for these, since you are likely to be sharing it with other site administrators. 


Once you have a superuser account, go to the URL where the site is running (you made a note of it when the server started running). Once you are at the login screen, enter the username and password of the superuser account you just created.


Note: due to the fact that the account tied to a superuser is not explicitly a site administrator, once you click the login button, you will remain in that page instead of being redirected to the homepage. To continue the setup process, once you click the login button, you must change the URL to "/admin_profile" instead of "/login".


From the page at the admin_profile URL, you will be able to create a site administrator account. We recommend that you make this account generic but secure, since you will likely share it with other site administrators.


After doing so, anyone with the credentials for the site administrator that you just created (not the superuser), will have full administrator access to the site. You have now completed the installation process!