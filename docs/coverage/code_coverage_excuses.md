# Code Coverage Excuses

## Main
- events_management/wsgi.py
    - This file contains django-generated code that exposes the WSGI callable as a module-level variable named "application." We did not add any code to this file and therefore are not testing it.
    
- manage.py
    - This file is django's executable file. The code that is not covered is checking for an import error. We did not write this code. Furthermore, we know django and all necessary packages will be installed. Therefore, we can reasonably expect that an import error will not occur.

## Python/C 
- events/views.py
    - 6 or so lines here are not covered in our tests because they involve out scheduler which was written in C. The function is called "start_scheduler" and involves the initialization of the scheduler. This involves scanning the local directory to see if the scheduler has already been made, and it not, compiling the scheduler. Error handling in this function is what is untested since it would require us to force a compilation error upon the scheduler, intentionally mess with our database so the scheduler has a database miss, or cause some other unknown scheduler error. Because none of these circumstances would ever reasonably come about, we did not/were not able to test them in the limits of the python testing environment. All other functions are fully tested.
