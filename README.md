# 15-112-term-project
My project mostly a mapping program that finds a pathway between two selected points
and will display the distance, time taken, and any restaurants at both points. The program
also displays all of the restaurants at CMU and shows the locations of the restaurants
and at what time they are open. The commands for the page are as follows:

cntrl m: directs user to the map page
cntrl f: directs user to food page
cntrl h: directs user to home page
cntrl k, while on home page: redirects to map key
cntrl h, while on home page: redirects user to help screen
cntrl i, while on home page: redirects user to instructions page
cntrl e, while on map page: allows user to add points to the map
cntrl p, while on map page: allows user to find pathway between two points

In order to type locations into the textboxes, a user must click on the box, type in the
location, hit enter, and click anywhere outside the box. The user can either click on the 
smaller circles throughout the map or on the large box to place a point as a starting or
ending value. The user can use the arrow keys to move the page up or down if the screen is
too large for the window. In order to run the program, the file mapstuff.py must be saved
in the same location as final project.py. The user must also install beautiful soup 4, which
can be done by visiting the page 'http://www.crummy.com/software/BeautifulSoup/bs4/download/'
The module requests must also be downloaded and can by going to command prompt and 
typing 'python -m pip install html5lib'. The requests module can be installed by typing
'python -m pip install requests'. You must also make sure that the Images folder is saved
in the TP3 folder or else the images willl not load.
