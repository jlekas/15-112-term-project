from tkinter import *
import string
from bs4 import BeautifulSoup
import requests
import html5lib
from mapstuff import map_of_points, point_locations, search

def rgbString(red, green, blue):
    return "#%02x%02x%02x" % (red, green, blue)

#################
####calls the different functions based on the modes
#################
def init(data, canvas):
    data.map_of_points = map_of_points
    data.point_locations = point_locations
    data.mode = 'home'
    data.search_locations = search
    data.move = 15
    data.scrollY = 0
    homeInit(data, canvas)
    foodInit(data, canvas)
    mapInit(data, canvas)
       
def mousePressed(event, data):
    #calls the page's mouse pressed
    if data.mode == 'home':
        homeMousePressed(event, data)
    elif data.mode == "food":
        foodMousePressed(event, data)
    elif data.mode == 'map':
        mapMousePressed(event, data)

def keyPressed(event, data):
    #calls the page's keypressed
    if data.mode == "home":
        homeKeyPressed(event, data)
    elif data.mode == "food":
        foodKeyPressed(event, data)
    elif data.mode == 'map':
        mapKeyPressed(event, data)

def timerFired(data):
    #calls the page's timer fired
    if data.mode == "map":
        mapTimerFired(data)
    elif data.mode == 'food':
        foodTimerFired(data)
    elif data.mode == 'home':
        homeTimerFired(data)

def redrawAll(canvas, data):
    #draw page depending on the mode
    if data.mode == 'map':
        mapRedrawAll(canvas, data)
    elif data.mode == "food":
        foodRedrawAll(canvas, data)
    elif data.mode == "home":
        homeRedrawAll(canvas, data)

#############################
# scroll
#############################
def homeScroll(event, data):
    if data.homeScreen == 'key':
        #if the user presses the up key, the page moves up
        if (event.keysym == "Up"):
            #makes sure user can't scroll to infinity
            if data.sy>=0:
                data.sy-=data.homeMove
        #if the user presses the down key, the page moves down
        elif event.keysym == 'Down':
            #makes sure user can't scroll to infinity
            if data.sy<=data.homeMin:
                data.sy+=data.homeMove

def mapScroll(event, data):
    if event.keysym == "Up":
        #makes sure user can't scroll to infinity
        if data.scrollY<(-data.map_max):
            data.scrollY+=data.move
    #if the user presses the down key, the page moves down
    elif event.keysym == "Down":
        #makes sure user can't scroll to infinity
        if data.scrollY>data.map_max:
            data.scrollY -=data.map_move

def foodScroll(event, data):
    if (event.keysym == "Up"):
        #makes sure user can't scroll to infinity
        if data.scrollY>0:
            data.scrollY-=data.offset
    #if the user presses the down key, the page moves down
    elif event.keysym == 'Down':
        #makes sure user can't scroll to infinity
        if data.scrollY<data.min:
            data.scrollY+=data.offset

def scroll(event, data):
    if event.keysym == 'Up' or event.keysym == 'Down':
        if data.mode == 'home':
            homeScroll(event, data)
        elif data.mode == 'map':
            mapScroll(event, data)
        elif data.mode == 'food':
            foodScroll(event, data)
#########################
## screen change page
#########################
#from notes
def ignoreKey(event):
    # Helper function to return the key from the given event
    ignoreSyms = [ "Control_L", "Control_R"]
    return (event.keysym in ignoreSyms)

def pointsEDIT(eventName, char, keysym, ctrl, shift, data):
    if data.pointsEdit:
        data.pointsEdit = False
    elif data.pointsEdit == None:
        addMapPoints(data)
    elif not data.pointsEdit:
        data.pointsEdit = True

def pathwayFind(eventName, char, keysym, ctrl, shift, data):
    #makes sure length of point list is two
    if len(data.map_selected)==2:
    	if data.map_selected[0] == data.map_selected[1]:
            data.points_error = True
            data.map_selected.pop()
    	else:
	        data.s_to_end = True
    elif len(data.map_selected)<2:
        data.points_error = True

def eventInfo(eventName, char, keysym, ctrl, shift, data):
#changes the page based on what key is pressed
    if ctrl:
        data.sy = 0
        data.scrollY = 0
        if data.mode != 'food' and keysym == 'f':
            data.mode = 'food'
        if keysym == 'h': data.homeScreen = 'help'
        if keysym == 'k': data.homeScreen = 'key'
        if keysym == 'i': data.homeScreen = 'instructions'
        if keysym == 'w': 
            data.homeScreen = 'welcome'
        if keysym == 'm' or keysym == 'M':
            data.mode = 'map'
        if data.mode == 'map':
            if keysym == 'p':
                pathwayFind(eventName, char, keysym, ctrl, shift, data)
            elif keysym == 'e':
                pointsEDIT(eventName, char, keysym, ctrl, shift, data)
                    #if you hit control r, it'll restart the page
            elif keysym == 'r':
                mapInit(data)

def homeScreenChange(event, data):
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)
    if (ignoreKey(event) == False):
        eventInfo("keyPressed", event.char, event.keysym, ctrl, shift, data)

def mapScreenChange(event, data):
    #changes the screen if a certain key is selected
    #changes page to food screen
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)
    if (ignoreKey(event) == False):
        eventInfo("keyPressed", event.char, event.keysym, ctrl, shift, data)
    if data.FoodClicked:
        data.scrollY = 0
        data.mode = 'food'
        data.FoodClicked = False
    #changes page to home screen
    elif data.homeClicked:
        data.scrollY = 0
        data.mode = 'home'
        data.homeScreen = 'welcome'
        data.homeClicked = False
    elif data.InstructionsClicked:
        data.scrollY = 0
        data.homeScreen = 'instructions'
        data.mode = 'home'
        data.InstructionsClicked = False
    elif data.keyClicked:
        data.scrollY = 0
        data.homeScreen = 'key'
        data.mode = 'home'
        data.keyClicked = False
    elif data.helpClicked:
        data.scrollY = 0
        data.mode = 'home'
        data.homeScreen = 'help'
        data.helpClicked = False

def foodScreenChange(event, data):
    #changes the screen if a certain key is selected
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)
    if (ignoreKey(event) == False):
        eventInfo("keyPressed", event.char, event.keysym, ctrl, shift, data)

def screenChange(event, data):
    #changes the screen based on key and data.mode
    if data.mode == 'home':
        homeScreenChange(event, data)
    elif data.mode == 'map':
        mapScreenChange(event, data)
    elif data.mode == 'food':
        foodScreenChange(event, data)
###################
##draw image
###################
class drawImage(object):
    def __init__(self, xco, yco, anchor):
        self.xco = xco
        self.yco = yco
        self.anchor = anchor

    def draw(self, image, canvas):
        canvas.data[str(image)] = image
        canvas.create_image(self.xco, self.yco, anchor = self.anchor,
            image = image)

#####################
## text box
#####################
class textbox(object):
    def __init__(self, text, type=None):
        self.text = text
        self.type = type

    def draw(self, canvas, x, y, boxwidth, boxheight, data):
        canvas.create_rectangle(x-boxwidth, y-boxheight, 
            x+boxwidth, y+boxheight, fill = 'white')
        canvas.create_text(x, y, text = self.text, 
            font = 'wingding 10', fill = 'black')
        if self.type == 'start':
            if data.Sblinking and data.typeStart:
                canvas.create_text(x, y, text = "|", 
                font = 'wingding 10', fill = 'black')
        if self.type == 'end':
            if data.Eblinking and data.typeEnd:
                canvas.create_text(x, y, text = "|", 
                font = 'wingding 10 bold', fill = 'black')
        if self.type == None:
            pass

##################
## button
##################
class button(object):
    def __init__(self, text, width = 60, height = 15):
        self.text = text
        self.width = width
        self.height = height
        self.color = 'maroon'

    def draw(self, canvas, x, y):
        canvas.create_rectangle(x-self.width, y-self.height, x+self.width,
            y+self.height, fill = self.color, activefill = 'red', 
            activewidth = 5)
        canvas.create_text(x, y, text = self.text, fill = 'white',
            font = 'wingding 10')
##############################
# home screen
##############################
def homeInit(data, canvas):
    data.homeScreen = 'welcome'
    data.sy = 0
    data.help = """
    To navigate to the food screen press cntrl f, to navigate to the
    maps page, hit cntrl m, and to navigate to the home screen, hit 
    cntrl m. If you need help navigating the maps page, then hit the 
    instructions button. In order to scroll up and down, hit the up 
    and down arrows. In order to add points to the map, hit cntrl e,
    type in the number of your point and then hit enter. You must 
    select the location of your point and click on the neighboring 
    points. Once you are finished, hit cntrl e and you will leave 
    edit mode. In order to type a start or end location, you must 
    first click on the respective text box, type your location, hit
    enter, and click outside the text box."""
    data.mapKey = """
    A: Baker Hall
    B: College of Fine Arts
    C: Wean Hall
    D: Porter Hall
    E: Doherty Hall
    F: Stever House
    G: Mudge House
    H: University Center
    I: Gates and Hillman Center
    J: Resnik Servery
    K: West Wing Dormitory
    L: Skibo Cafe
    M: Purnell Center
    N: Morewood Gardens
    O: Legacy Plaza
    P: Posner Hall (Tepper)
    Q: Hunt Library
    R: Hamburg Hall (Heinz)
    S: Newell-Simon Hall
    T: Skibo Gymnasium
    U: Soccer Field
    V: Gesling Stadium
    W: Margarette Morrison
    X: Donner House
    Y: Tennis Courts
    """
    data.homeMove = 15
    data.rectcolor = rgbString(155, 6, 6)
    data.outcolor = None
    data.homeMin = 120
    data.HomeImages = dict()
    loadHomeImages(data)

def loadHomeImages(data):
	images ={'instructions':'Images\instruction page.gif', 'welcome':
	"Images\welcome screen.gif", 'key':'Images\map key.gif', 
    'help': 'Images\help page.gif'
	}
	for image in images:
		data.HomeImages[image] = PhotoImage(file = images[image])

def drawInstructions(canvas, data):
    #image found at https://upload.wikimedia.org/wikipedia
    #/commons/1/19/Hamerschlag_Hall_at_Carnegie_Mellon_University.jpg
    drawImage(data.width//2, 0, N).draw(data.HomeImages['instructions'], canvas)
    canvas.create_text(data.width//2, data.height//20, text = 'Instructions',
        font= ('Comic Sans', 50), fill = 'white')

def drawHelp(canvas, data):
    #image from 
    #http://imageshack.com/f/2ioakland069j
    drawImage(data.width//2, 0, N).draw(data.HomeImages['help'], canvas)
    canvas.create_text(data.width//2, data.height//6, text = 'Help', 
        font = 'wingding 30 bold', fill = 'white')
    canvas.create_text(data.width//2, data.height//2, text = data.help,
        font= 'wingding 22', fill = 'white')

def drawKey(canvas, data):
    # found at https://www.cs.cmu.edu/sites/default/files/GHC2_b.jpg
    drawImage(data.width//2, 0, N).draw(data.HomeImages['key'], canvas)
    canvas.create_text(data.width//2, data.height//25-data.sy, text = 'Map Key', 
        font = 'wingding 30', fill = 'white')
    canvas.create_text(data.width//2,3*data.height//5-data.sy, text=data.mapKey,
        font= 'wingding 20', fill = 'white')

def homeRedrawAll(canvas, data):
    if data.homeScreen == 'welcome':
        drawImage(data.width//2, 0, N).draw(data.HomeImages['welcome'],canvas)
    elif data.homeScreen == 'key':
        drawKey(canvas, data)
    elif data.homeScreen == 'instructions':
        drawInstructions(canvas, data)
    elif data.homeScreen == 'help':
        drawHelp(canvas, data)


def homeTimerFired(data):
    pass

def homeMousePressed(event, data):
    pass

def homeKeyPressed(event, data):
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)
    screenChange(event, data)
    scroll(event, data) 

##############################
#maps screen
##############################
class restaurants(object):
    def __init__(self, place):
        #restaurants in locations
        self.names = {101: ["Gingers Express"], 
        100:["Tazzo D'Oro"],
        98:["Heniz Cafe"], 99: ["Asiana", 
        "Michell's Mainstreet"], 206: ["La Prima Espresso"], 
        204: ["Gingers Express"], 203:["Maggie Murph Cafe"],
        201:["The Zebra Lounge"],
        110:["The Exchange"], 107:["Nakama Express", 
        "Soup & Salad", "Spice It Up Grill", "Take Comfort","Breakfast Express",
        "Global Flavors", "Taste of India", "The Pomegranate", "Tartans Pizza", 
        "Carnegie Mellon Cafe"], 105:["Tartan Express"],
        103:["El Gallo de Oro", "Entropy", "Skibo Cafe", 
        "Schatz Dining Room", 'City Grill', "Creperie", 'Downtown Deli', 
        'Evgefstos', "Pasta Villagio", 'Rice Bowl', 'Spinning Salads'],
        102:['Skibo'],
        97:["The Undergroud"]}
        self.place = place

    def getRestaurantNames(self):
        restaurants = list()
        for location in self.place:
            for r in self.names:
                if location == r:
                    restaurants+=[self.names[r]]
        return restaurants
class path(object):
    #keeps a list of all locations of points of pathways
    path_points = []
    def __init__(self, data, start=None, end=None):
        self.start = start
        self.end = end
        self.points = data.point_locations

    def do_all(self, graph):
        path = self.heart(graph, self.start, self.end)
        converted = self.convert(path)
        distance = self.totalDistance(converted)
        return tuple((converted, distance))

    def distanceOfPoints(self, x1, y1, x2, y2):
        return ((x2-x1)**2 + (y2-y1)**2)**.5

    def totalDistance(self, points):
        distance = 0
        #iterate through all points starting at first and find the distance 
        #between current point and the previous point
        for p in range(1, len(points)):
            distance+=self.distanceOfPoints(points[p][0], points[p][1], 
                points[p-1][0], points[p-1][1])
        return distance

    def distance(self, p1, p2):
        corrected = []
        for key in point_locations:
            if p1 == key:
                corrected+= [point_locations[key]]
            if p2 == key:
                corrected+= [point_locations[key]]
        distance = 0
        distance+=((corrected[0][0] - corrected[1][0])**2 + (corrected[0][1] - 
            corrected[1][1])**2)**.5
        return distance

    def heart(self, graph, start, end):
        #set up queue and visited, and parents in order to print path
        queue, visited, parents = [start], list([start]), dict()
        #as long as there is a queue, iterate
        while len(queue)>=1:
            # dequeue the last element and then check
            #neighboring nodes
            next = queue.pop(0)
            dprime = dict()
            for node in graph[next]:
                if node not in visited:
                    #find distance of each node and then add them to the queue
                    #so that shortest distance is added first
                    d = self.distance(node, next)
                    dprime[node] = d
            #sort dprime by distance and then add shortest nodes into queuefirst
            #this way, the algorithm will check the shortest distances first
            sorted(dprime, key = dprime.get)
            for n in dprime:
                if n not in visited:
                    parents[n] = start
                    visited+=[n]
                    queue.append(n)
            #check if the first position in the queue is the end
            start = queue[0]
            if start == end:
                #create the solution
                solution = [end]
                x = end
                #if the value of x is in parents, add it to the solution
                while x in parents and parents[x]:
                    solution+=[(parents[x])]
                    x = parents[x]
                #return solution backwards so that it's from start to finish
                return solution[::-1]
        #will never reach an end, since all points are connected in some way
        #to all other points

    def convert(self, pathway):
        corrected = []
        for node in pathway:
            for key in self.points:
                if node == key:
                    corrected+=[self.points[key]]
                    break
        return corrected

class Road(object):
    def __init__(self):
        self.r = 2
        self.points = point_locations

    def drawPoints(self, canvas, data):
        sy = data.scrollY
        for node in ((self.points)):
            canvas.create_oval(self.points[node][0]-self.r,(self.points[node][1]
                -self.r+sy), self.points[node][0]+self.r, 
                self.points[node][1]+self.r+sy,)
            if data.pointsEdit == True:
                canvas.create_text(self.points[node][0],self.points[node][1]+sy, 
                text = self.points[node][2])

    def drawRoad(self, canvas, data):
        #takes canvas, list of points and draws lines between points
        for i in range(1, len(data.way)):
            canvas.create_line(data.way[i-1][0],data.way[i-1][1]+data.scrollY,
            	data.way[i][0], data.way[i][1]+data.scrollY, 
            	fill = data.selectColor)

class mainPoints(object):
    def __init__(self, points):
        self.points = points

    def draw(self, canvas, data):
        sy = data.scrollY
        r = 2 #radius of nodes
        #puts a square around the nodes
        if data.pointsEdit != None and not data.pointsEdit:
            for point in data.mainPoints:
                canvas.create_rectangle(point[0]-data.mapR, 
                    point[1]-data.mapR+sy, point[0]+data.mapR, 
                    point[1]+data.mapR+sy,fill=data.unselectColor)
            # #looks through selected points and colors them in red
            for spoint in data.map_selected:
                #make sure point isn't a main point first
                if spoint not in data.mainPoints:
                    canvas.create_rectangle(spoint[0]-r, spoint[1]-r+sy, 
                        spoint[0]+r, spoint[1]+r+sy, fill = data.selectColor)
                elif spoint in data.mainPoints:
                    canvas.create_rectangle(spoint[0]-data.mapR,spoint[1]-
                        data.mapR+sy, spoint[0]+data.mapR, 
                        spoint[1]+data.mapR+sy, fill = data.selectColor)
            #draw the points labels afterwards so they aren't colored over
            for point in range(len(data.mainPoints)):
                canvas.create_text(data.mainPoints[point][0], 
                data.mainPoints[point][1]+sy, text=string.ascii_letters[point],
                fill = "white")

def mapInit(data, canvas):
    #placed out so selected points aren't changed when init function is called
    data.map_selected = []
    #sets up scrolling
    data.s_to_end = False
    data.way = []
    data.distance = 0
    data.pointsEdit = False
    data.mapR = 8
    data.mainPoints = [[580, 640, 204], [703, 625, 201], [467, 533, 206], 
        [452, 597, 205], [621, 550, 202], [736, 130, 96], [730, 62, 95], 
        [776, 435, 103], [574, 426, 100], [966, 542, 107], [873, 513, 106], 
        [766, 373, 102], [660, 417, 101], [693, 194, 97], [828, 498, 105],
        [781, 642, 110], [646, 679, 203], [498, 339, 98], [487, 450, 99],
        [836, 713, 109], [1050, 504, 108],[928, 454, 104], [824, 554, 117],
        [903, 597, 125], [780, 542, 126]
        ]
    data.unselectColor = "black"
    data.selectColor = "red"
    data.map_move = 15
    data.map_max = -30
    data.showRoad = True
    data.points_error = False
    data.start = ''
    data.end = ''
    data.boxwidth = 80
    data.boxheight = 10
    data.typeStart = False
    data.typeEnd = False
    data.InstructionsClicked = False
    data.helpClicked = False
    data.homeClicked = False
    data.FoodClicked = False
    data.keyClicked = False
    data.Sblinking = False
    data.Eblinking = False
    data.type_error = False
    data.added = [0]
    data.moveGuy = False
    data.showInfo = False
    data.ratio = 3.4
    #used to convert time if biking or walking
    data.walk = 264
    data.bike = 880
    data.walking = False
    data.biking = False
    data.mapImages = dict()
    loadMapImages(data)

def loadMapImages(data):
	images = {'background':"Images/map page.gif", 'map':'Images/map3.gif'}
	for image in images:
		data.mapImages[image] = PhotoImage(file = images[image])	

def drawMapPage(canvas, data):
    #image from 
    #https://i.ytimg.com/vi/ok4UDA4uwiE/maxresdefault.jpg
    drawImage(data.width//2,0, N).draw(data.mapImages['background'], canvas)
    #image from 
    #google maps
    drawImage(data.width//2, data.height//20+data.scrollY, N).draw(
    	data.mapImages['map'], canvas)

def startBox(canvas, data):
    canvas.create_text(data.width//12, data.height//12, text = 'Start:', 
        fill = 'white', font =  'wingding 10 bold')
    textbox(data.start, 'start').draw(canvas, data.width//12, data.height//9, 
        data.boxwidth, data.boxheight, data)

def endBox(canvas, data):
    canvas.create_text(data.width//12, 3*data.height//12-data.boxheight*2, 
        text = 'End:', fill = 'white', font = "wingding 10 bold")
    textbox(data.end, 'end').draw(canvas, data.width//12, 3*data.height//12, 
        data.boxwidth, data.boxheight, data)

def drawSearchError(canvas, data):
    r = 60
    canvas.create_oval(data.width//20-r, data.height//2-r, data.width//20+r,
        data.height//2+r, fill = 'maroon')
    canvas.create_text(data.width//20, data.height//2, 
        text = '''I\'m sorry please enter
        a valid location :)''', 
    font = 'wingding 8 bold', fill = 'white')

def MapButtons(canvas, data):
    #make home, help, instrcutions, key, and food buttons
    button('Instructions').draw(canvas, data.width//10, data.height//40)
    button('Map Key').draw(canvas, 3*data.width//10, data.height//40)
    button('Food Page').draw(canvas, 5*data.width//10, data.height//40)
    button('Home Page').draw(canvas, 7*data.width//10, data.height//40)
    button('Help page').draw(canvas, 9*data.width//10, data.height//40)

def addPointsBox(canvas, data):
    if data.pointsEdit:
        #draws a text box that will take the number of the new point
        canvas.create_rectangle(data.width//6 - data.boxwidth,data.height//(4/3)
         - data.boxheight*3, data.width//6+data.boxwidth, data.height//(4/3)+
            data.boxheight*3, fill = 'maroon')
        canvas.create_text(data.width//6, data.height//(4/3), 
            text ='''Please give your point a \nnumber that is not 
            already taken.''', fill = 'white')
        textbox(str(data.added[0])).draw(canvas, data.width//6, 
                data.height*.9, data.boxwidth, data.boxheight*4, data)
    if data.pointsEdit == None:
        canvas.create_rectangle(data.width//6 - data.boxwidth*1.25,
            data.height//(4/3) - data.boxheight*6, 
            data.width//6+data.boxwidth*1.25, data.height//(4/3)+
            data.boxheight*6, fill = 'maroon')
        canvas.create_text(data.width//6, data.height//(4/3), 
            text ='''Please pick a location for your \npoint on the map. Then
            select neighboring points''', 
            fill = 'white')

def restaurantBox(canvas, data):
    #draws all restaurants or start and end on side of page
    canvas.create_text(11*data.width//12, 3*data.height//12,text='Restaurants:',
        font = 'wingding 12 bold', fill = 'white')
    if len(data.map_selected) == 2:
        restaurant1=restaurants([data.map_selected[0][2]]).getRestaurantNames(
            )
        restaurant2=restaurants([data.map_selected[1][2]]).getRestaurantNames(
            )
        rest = []
        rest+= [x for x in restaurant1]
        rest+=[y for y in restaurant2]
        if len(rest) == 2: values = (len(rest[0]) + len(rest[1]))
        elif len(rest) == 1: values = (len(rest[0]))
        elif len(rest) == 0: values = 0
        value = 0
        for ps in range(len(restaurant2)):
            for j in range(len(restaurant2[ps])):
                value+=1
                canvas.create_text(11*data.width//12, 
                3.25*data.height//12+(values - value)*25, 
                text=(restaurant2[ps][j]),
                font ='wingding 9',fill='white')
        for place in range(len(restaurant1)):
            for i in range(len(restaurant1[place])):
                value+=1
                canvas.create_text(11*data.width//12, 
                    (3.25*data.height//12+(values - value)*25), 
                text=(restaurant1[place][i]),
                font = 'wingding 9', fill='white')

## drawing the information after feedback from a peer
def drawInfo(canvas, data):
    #draws the distance and time in a box depending on mode of transport
    button('Information').draw(canvas, data.width//12, 8*data.height//13)
    if data.showInfo:
        canvas.create_rectangle(data.width//12 - data.boxwidth, 
            data.height//13*9 - data.boxheight*2, data.width//12 +data.boxwidth,
            data.height//13*9 + data.boxheight*3, fill = 'maroon')
        text = 'Distance: %d feet'%(data.distance * data.ratio)
        canvas.create_text(data.width//12, 9*data.height//13, 
            text=text, fill = 'white')
        button('Biking', 30).draw(canvas, data.width//9, 10*data.height//13)
        button('Walking', 30).draw(canvas, data.width//15, 10*data.height//13)
        canvas.create_rectangle(data.width//12 - data.boxwidth, 
            data.height//13*11 - data.boxheight*2, data.width//12+data.boxwidth,
            data.height//13*11 + data.boxheight*3, fill = 'maroon')
        if data.biking:
            #60 minutes in an hour
            text2 = 'Time: %d minutes %d seconds'%(data.distance * 
                data.ratio//data.bike, data.distance*data.ratio/data.bike%60)
            canvas.create_text(data.width//12, 11*data.height//13, 
                text=text2, fill = 'white')
        elif data.walking:
            text2 = 'Time: %d minutes %d seconds'%(data.distance*
                data.ratio//data.walk, data.distance * 
                data.ratio/data.walk%60)
            canvas.create_text(data.width//12, 11*data.height//13, 
                text=text2, fill = 'white')

def mapRedrawAll(canvas, data):
    drawMapPage(canvas, data)
    if data.showRoad: Road().drawPoints(canvas, data)
    mainPoints(data.map_selected).draw(canvas, data)
    if len(data.way)>0:
        Road().drawRoad(canvas, data)
    #check if error in search box
    if data.type_error: drawSearchError(canvas, data)
    if data.points_error == True:
        canvas.create_text(data.width//2, data.height//2, text = 
            "I'm sorry please select a starting and ending location", 
            font = 'wingding 30 bold')
    startBox(canvas, data)
    endBox(canvas,data)
    restaurantBox(canvas, data)
    MapButtons(canvas, data)
    drawInfo(canvas, data)
    if data.pointsEdit or data.pointsEdit == None:
        addPointsBox(canvas, data)

def addMapPoints(data):
    #adds point to the map of points
    data.map_of_points[data.added[2][0]] = data.added[2][1:]
    #adds the point to the map of points of neighbors
    for value in data.added[2]:
        if value != data.added[0]:
            data.map_of_points[value] += [data.added[0]]
    #sets data.added back to original so the user can add more points
    data.added = [0]
    data.pointsEdit = False

def mapTimerFired(data):
    #makes it so you can re-enter starting and ending points
    if len(data.map_selected)<2: data.way = []
    if data.s_to_end == True:
        data.showInfo = True
        things = None
        things = path(data, data.map_selected[0][2], 
            data.map_selected[1][2]).do_all(data.map_of_points)
        data.way, data.distance = things[0], things[1]
        data.s_to_end = False
    if data.typeStart and len(data.start) == 0:
        if (data.Sblinking): 
            data.Sblinking = False
        elif not (data.Sblinking and len(data.start == 0)): data.Sblinking =True
    if data.typeEnd and len(data.end) == 0:
        if (data.Eblinking): 
            data.Eblinking = False 
        elif not (data.Eblinking and len(data.start == 0)): data.Eblinking =True
    if len(data.end) != 0: data.Eblinking = False
    if len(data.start) != 0: data.Sblinking = False
    if len(data.map_selected)<2: 
        data.showInfo = False
        data.biking = False
        data.walking = False

def typeIntoSearch(event, data):
    #if user hits backspace, clear last key
    if event.keysym == 'BackSpace':
        if len(data.start)>0:
            data.start = data.start[:-1]
    #if user enters letter, white space or ampersand, enter it i
    if event.keysym == 'ampersand':
        data.start+='&'
    elif ((event.keysym in string.ascii_letters)):
        data.start+=event.keysym
    elif (event.keysym == 'space'):
        data.start+=' '
        #check if data.start is a valid location

def typeIntoEnd(event, data):
    #if user hits backspace, clear last key
    if event.keysym == 'BackSpace':
        if len(data.end)>0:
            data.end = data.end[:-1]
    #if user enters letter, white space or ampersand, enter it in
    if event.keysym == 'ampersand':
        data.end+='&'
    elif ((event.keysym in string.ascii_letters)):
        data.end+=event.keysym
    elif (event.keysym == 'space'):
        data.end+=' '

def typeNewP(event, data):
    ctrl  = ((event.state & 0x0004) != 0)
    shift = ((event.state & 0x0001) != 0)
    #if user hits backspace, clear last key
    if event.keysym == 'BackSpace':
        if (data.added[0])>0:
            data.added[0] = data.added[0]//10
    elif event.keysym in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        data.added[0]*=10
        data.added[0]+=int(event.keysym)
    elif event.keysym == 'Return':
        data.pointsEdit = None
    eventInfo('keyPressed', event.char, event.keysym, ctrl, shift, data)

def checkSelected(data, point, type):
	if type == 'start':
		if len(data.map_selected) == 2:
			data.map_selected = data.map_selected[1:]
			data.map_selected[0] = (point)
		elif len(data.map_selected)<2:
			data.map_selected.append(point)
	if type == 'end':
		if len(data.map_selected) == 2:
			data.map_selected = data.map_selected[0:1]
			data.map_selected.append(point)
		elif len(data.map_selected)<2:
			data.map_selected.append(point)

def checkValidLocat(event, data):
    #check if start place is a valid location and if so add it in
    if data.typeStart:
        if event.keysym == 'Return':
            error = True
            for locat in data.search_locations:
                for place in data.search_locations[locat]:
                    if data.start.upper() == place:
                        point = (path(data).convert([locat])[0])
                        checkSelected(data, point, "start")
                        error = False
            if error: data.type_error = True
    elif data.typeEnd:
        if event.keysym == 'Return':
            error = True
            for locat in data.search_locations:
                for place in data.search_locations[locat]:
                    if data.end.upper() == place:
                        point = (path(data).convert([locat])[0])
                        checkSelected(data, point, "end")
                        error = False
            if error: data.type_error = True
                        
def mapKeyPressed(event, data):
    #if user clicks get rid of the error message
    data.points_error = False
    data.type_error = False
    #if the search typing is on then all keys go into box, else check others
    if data.typeStart:
        typeIntoSearch(event, data)
        checkValidLocat(event, data)
    elif data.typeEnd:
        typeIntoEnd(event, data)
        checkValidLocat(event, data)
    elif data.pointsEdit:
        typeNewP(event, data)
    else:
        #check if the page is changed
        screenChange(event, data)
        #check if user scrolled up or down
        scroll(event, data)
        #gets the path from start to finish if user hits p

def checkNodes(event, data):
    #goes through all the nodes and checks if mouse is clicked in area
    r=2 #defined in the nodes
    for point in data.point_locations:
        if data.point_locations[point] in data.mainPoints:
            #if the node is a main point make sure to account for this
            if ((data.point_locations[point][0]-data.mapR<=event.x<=(
                data.point_locations[point][0]+data.mapR)) and
            (data.point_locations[point][1]-data.mapR+data.scrollY <= event.y<=(
                data.point_locations[point][1]+data.mapR+ data.scrollY))):
                #if the point was already selected, deselect it
                if data.point_locations[point] in data.map_selected:
                    data.map_selected.remove(data.point_locations[point])
            #if there are already two selected points, pop the first one out
                elif len(data.map_selected)== 2:
                    data.map_selected.pop()
                    data.map_selected+=[data.point_locations[point]]
            #otherwise, add the new point into selected points
                else:
                    data.map_selected+=([data.point_locations[point]])
        if ((data.point_locations[point][0]-r<=event.x<=(
            data.point_locations[point][0]+r)) and 
            (data.point_locations[point][1]-r+data.scrollY <= event.y <= 
            data.point_locations[point][1]+r+data.scrollY)):
        #if the point was already selected, deselect it
            if data.point_locations[point] in data.map_selected:
                data.map_selected.remove(data.point_locations[point])
        #if there are already two selected points, pop the first one out
            elif len(data.map_selected)== 2:
                data.map_selected.pop()
                data.map_selected+=[data.point_locations[point]]
        #otherwise, add the new point into selected points
            else:
                data.map_selected+=[data.point_locations[point]]

def checkStartBox(event, data):
    #if the user clicks in the box, the keys they type will be entered into the 
    #search box
    if (data.width//12-data.boxwidth<=event.x<=data.width//12+data.boxwidth and
        data.height//9-data.boxheight<=event.y<=data.height//9+data.boxheight):
        data.typeStart = True
    else:
        data.typeStart = False


def checkEndBox(event, data):
    #if the user clicks in the box, the keys they type will be entered into the 
    #search box
    if (data.width//12-data.boxwidth<=event.x<=data.width//12+data.boxwidth and
        3*data.height//12-data.boxheight<=event.y<=
        3*data.height//12+data.boxheight):
        data.typeEnd = True
    else:
        data.typeEnd = False

def checkButtonClick(event, data):
    buttonW, buttonH = 60, 15
    if (data.width//10-buttonW <=event.x<= data.width//10+buttonW and
        data.height//40-buttonH <= event.y<=data.height//40+buttonH):
        data.InstructionsClicked = True
    elif (3*data.width//10-buttonW <=event.x<= 3*data.width//10+buttonW and
        data.height//40-buttonH <= event.y<=data.height//40+buttonH):
        data.keyClicked = True
    elif (5*data.width//10-buttonW <=event.x<= 5*data.width//10+buttonW and
        data.height//40-buttonH <= event.y<=data.height//40+buttonH):
        data.FoodClicked = True
    elif (7*data.width//10-buttonW <=event.x<= 7*data.width//10+buttonW and
        data.height//40-buttonH <= event.y<=data.height//40+buttonH):
        data.homeClicked = True
    elif (9*data.width//10-buttonW <=event.x<= 9*data.width//10+buttonW and
        data.height//40-buttonH <= event.y<=data.height//40+buttonH):
        data.helpClicked = True
    elif (data.width//12-buttonW <= event.x<= data.width//12+buttonW and
        8*data.height//13 - buttonH <=event.y<=8*data.width//13+buttonH and 
        len(data.map_selected) == 2):
        data.showInfo = True
    #check if the page is changed
    screenChange(event, data)

def selectNeighbors(event, data):
    if len(data.added)==1:
        data.added.append([])
        data.added[1] = [event.x, event.y, data.added[0]]
        data.added.append([])
        data.added[2] = [data.added[0]]
        #adds point to the point locations
        data.point_locations[data.added[0]] = data.added[1]
    else:
        if len(data.added[2])==1:
            #goes through all the nodes and checks if mouse is clicked in area
            r=2 #defined in the nodes
            for point in data.point_locations:
                if ((data.point_locations[point][0]-r<=event.x<=
                    data.point_locations[point][0]+r) and 
                    (data.point_locations[point][1]-r+data.scrollY <= event.y <= 
                    data.point_locations[point][1]+r+data.scrollY)):
                #if the point was a node, add it to data.added[2]
                    data.added[2].append(int(point))

def checkMode(event, data):
    #the width and height of boxes and check if bike or walking clicked
    h, w = 15, 30
    xVal1, xVal2, yVal = data.width//9, data.width//15, 10*data.height//13
    if (xVal1-w <=event.x<=xVal1+w) and yVal-h<=event.y<=yVal+h:
        data.biking = True
    if (xVal2-w <=event.x<=xVal2+w) and yVal-h<=event.y<=yVal+h:
        data.walking = True
def mapMousePressed(event, data):
    #if user clicks get rid of the error message
    data.points_error = False
    data.type_error = False
    #see if the user is trying to type in
    checkStartBox(event, data)
    checkEndBox(event, data)
    #put nodes before so that if a point is clicked 
    #even if it is the node, the entire box will be colored in
    checkNodes(event, data)
    checkButtonClick(event, data)
    if data.pointsEdit == None:
        selectNeighbors(event, data)
    if data.showInfo: checkMode(event, data)
    
###############################
###food page
###############################
class webscrape(object):
    def __init__(self):
        #used as the url is longer than 80 characters
        self.url1 = 'http://webapps.studentaffairs.cmu.'
        self.url2 = "edu/dining/ConceptInfo/?page=listConcepts"
        self.url=self.url1+self.url2
        self.times = []
        self.locations = []
        #need to hardcode list due to weird letters in the html
        self.names = ['Asiana', 'Breakfast Express', 'El Burrito Grande', 
        'Carnegie Mellon Cafe', "Chef's Table", 'City Grill', 'Creperie', 
        'Downtown Deli', 'Entropy', 'Evgefstos', 'The Exchange', 
        'Fresh Select Soup & Salad', 'El Gallo de Oro', 
        'Gingers Express (Baker)', 'Gingers Express (Purnell)', 
        'Global Flavour', 'Heinz Cafe', 'The Maggie Murph Cafe', 
        "Mitchell's Mainstreet", 'Nakama', 'Pasta Villagio', 'The Pomegranate',
        'La Prima Espresso', 'Rice Bowl', 'Schatz Dining Room', 'Seiber Cafe',
        'Skibo Cafe', 'Spice It Up Grill', 'Spinning Salads', "Stephanie's",
        'Stir Crazy', 'Take Comfort', "Tartan's Express", 'Tartans Pizza', 
          'Taste of India', "Tazza D'oro", 'The Undergroud', 'The Zebra Lounge']
        self.all_info = []
        self.descipt = []

    def timeList(self, line):
        #takes in a line and adds it legiably to self.times
        if 'Closed' in str(line):
                self.times+=['Closed Today']
        else:
            #get text in soup split the lines
            s = str(line.get_text()).splitlines()
            #the fourth line is the line with times so add this to times
            self.times+=[s[4].strip()]

    def locationList(self, line):
        #takes in a line and adds it legiably to self.locations
        locat = str(line.get_text())
        self.locations+=[locat]

    def concatInfo(self):
        #iterate through one since they're all the same length
        #make a list that can be used to write out if iterated through
        for i in range(len(self.names)):
            self.all_info+=[self.names[i]+ ': Hours: '+self.times[i]+
            ', Location: '+self.locations[i]]

    def timeHours(self):
    	#adds a line in hours
        place_hours = dict()
        for i in range(len(self.names)):
            place_hours[self.names[i]] = self.times[i]
        return place_hours

    def getInfo(self):
        htmlFile = requests.get(self.url)
        htmlText = htmlFile.content
        soup = BeautifulSoup(htmlText, "html5lib")
        location = (soup.findAll('div', {'class': 'conceptLocation' }))
        time = (soup.findAll("div", {'class': 'conceptHours'}))
        name = (soup.findAll('div', {'class': 'conceptName'}))
        #makes list of times in order
        for i in range(len(time)):
            #if the place is closed, add in a nice thing way to say closed
            self.timeList(time[i])
            #add the name of the location to the list
            self.locationList(location[i])
        times = self.timeHours()
        #concatenate all info together and return a list of all restaurants
        self.concatInfo()
        return (self.all_info, times)

def foodInit(data, canvas):
    #gets all the information from the site
    #add back with wifi
    data.stuff = webscrape().getInfo()
    data.place = data.stuff[0]
    data.times_place = data.stuff[1]
    data.offset = 100
    data.food_min = 750
    data.min = 750
    data.foodImages = []
    loadFoodImages(data)

def loadFoodImages(data):
	image = 'Images\\food page.gif'
	data.foodImages.append(PhotoImage(file=image))

def foodTimerFired(data):
    pass

def foodMousePressed(event, data):
    pass

def foodKeyPressed(event, data):
    #changes the page depending on the button pressed
    screenChange(event, data)
    #check if the user scrolled page
    scroll(event, data)

def drawR_names(canvas, data):
    sy = data.scrollY
    for restaurant in range(len(data.place)):
        canvas.create_text(data.width//2, (data.height//12+(restaurant*2)*
            (data.height//(len(data.place)+2)))-sy, text=data.place[restaurant],
            font = 'wingding 10 bold', fill = 'white')
            
def foodRedrawAll(canvas, data):
    #website: http://imageshack.com/f/194/carnegiemellonu15.jpg
    drawImage(data.width//2, 0, N).draw(data.foodImages[0], canvas)
    canvas.create_text(data.width//2, 0-data.scrollY, text = "Food Directory", 
        font = ("wingding", 30, "bold"), anchor = N, fill = 'white')
    drawR_names(canvas, data)

####################################
# run function
####################################
def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        # if data.mode != 'home':
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 500 # milliseconds
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    canvas.data = {}
    init(data, canvas)
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1400, 750)
