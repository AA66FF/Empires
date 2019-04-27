from random import *
from time import *
from graphics import *
from math import *

# You can change these
SCREEN_HEIGHT = 900
SCREEN_WIDTH = 900

STAR_DEFAULT_COLOR = "#FFFFFF"
ORIGIN_STAR_COLOR = "#FFFF55"
LINK_DEFAULT_COLOR = "#555555"

NUMBER_OF_STARS = 700
STAR_MINIMUM_SEPARATION = 10
STAR_MINIMUM_LINKS = 2
STAR_MAXIMUM_LINKS = 3
NUMBER_OF_EMPIRES = 30

STAR_GROWTH_BASE = 10

STAR_DISPLAY_RADIUS_EXP = 6/12
STAR_DISPLAY_RADIUS_MOD = 0.8
STAR_DISPLAY_RADIUS_BASE = 3
STAR_DISPLAY_MAX_RADIUS = 15

ISOLATED_CHECK_DRAW = True
DRAW_LINKS = True
UPDATE_LINKS = False
PRINT_EMPIRE_STATUS = True

TURN_DELAY = 0.04 # In seconds

# Don't change these
fps = 60

win = GraphWin("Empires", SCREEN_WIDTH, SCREEN_HEIGHT)
win.setBackground(color_rgb(0,0,0))
win.autoflush = False

graph = GraphWin("Graph", 500, 500)
graph.setBackground("#000000")
graph.autoflush = False

t = time.time()
t3 = time.time()
frame = 0
timer = 0
open = True

alltimeEmpires = 0

def add(v1,v2):
    return [v1[0]+v2[0],v1[1]+v2[1]]

def sub(v1,v2):
    return [v1[0]-v2[0],v1[1]-v2[1]]

def mult(v1,mult):
    return [v1[0]*mult,v1[1]*mult]

def div(v1,div):
    return [v1[0]/div,v1[1]/div]

def dist(p1,p2):
    return sqrt((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)

def mag(vector):
    return sqrt(vector[0]**2+vector[1]**2)

def normalize(vector):
    ang = 0
    if vector[0] >= 0 and vector[1] < 0:
        ang = atan(vector[0]/-vector[1])
    if vector[0] > 0 and vector[1] >= 0:
        ang = atan(-vector[1]/-vector[0])+radians(90)
    if vector[0] <= 0 and vector[1] > 0:
        ang = atan(vector[0]/-vector[1])+radians(180)
    if vector[0] < 0 and vector[1] <= 0:
        ang = atan(-vector[1]/-vector[0])+radians(270)
    return [sin(ang),-cos(ang)]

def angle(vector):
    ang = 0
    if vector[0] >= 0 and vector[1] < 0:
        ang = atan(vector[0]/-vector[1])
    if vector[0] > 0 and vector[1] >= 0:
        ang = atan(-vector[1]/-vector[0])+radians(90)
    if vector[0] <= 0 and vector[1] > 0:
        ang = atan(vector[0]/-vector[1])+radians(180)
    if vector[0] < 0 and vector[1] <= 0:
        ang = atan(-vector[1]/-vector[0])+radians(270)
    return ang

def inside(pos,rectPos1,rectPos2):
    if (pos[0] > rectPos1[0] and pos[0] < rectPos2[0] and pos[1] > rectPos1[1]\
    and pos[1] < rectPos2[1]):
        return True
    else:
        return False

def rotate(vector, angle):
    return [vector[0]*cos(angle)-vector[1]*sin(angle),vector[0]*sin(angle)\
    +vector[1]*cos(angle)]

def vecToPt(vector):
    return Point(vector[0],vector[1])

def sign(number):
    if number < 0:
        return -1
    elif number > 0:
        return 1
    else:
        return 0

def randomByte():
    return randint(0,255)

stars = []
links = []
points = []
empires = []

class Star:
    # These are the only things that actually change on the screen. Empires
    # don't draw themselves; only stars and links do.
    def __init__(self, pos, id):
        self.id = id
        self.pos = pos
        self.homeStar = False
        self.power = 10
        self.links = 0
        self.connectedTo = []
        self.empirePrev = -1
        self.radius = floor(min(self.power**(STAR_DISPLAY_RADIUS_EXP)*STAR_DISPLAY_RADIUS_MOD,\
        STAR_DISPLAY_MAX_RADIUS)+STAR_DISPLAY_RADIUS_BASE)
        self.oldRadius = self.radius
        # A value of -1 indicates that this star is not controlled by any
        # empire.
        self.empire = -1
        self.changed = False
        self.empireColor = [255,255,255]
        self.color = STAR_DEFAULT_COLOR
        self.point = Point(self.pos[0],self.pos[1])
        self.point.setOutline(self.color)
        self.point.setFill(self.color)
        self.circle = Circle(vecToPt(self.pos),min(sqrt(self.power),50))
        self.turnsPassed = 0
        self.revoltTimer = 0
        self.revolt = False

    def draw(self):
        # Draws the star and its corresponding empire circle. Note: the empire
        # circle may be separated into its own object in order to make the
        # borders between empires more elegant.
        self.point.undraw()
        self.circle.undraw()
        if self.revoltTimer > 0 and self.revolt:
            self.empireColor = [255,255,255]
        if self.empire != -1:
            self.circle = Circle(vecToPt(self.pos),self.radius)
            self.circle.setOutline(color_rgb(\
            self.empireColor[0],\
            self.empireColor[1],\
            self.empireColor[2]))
            self.circle.setFill(color_rgb(\
            self.empireColor[0],\
            self.empireColor[1],\
            self.empireColor[2]))
            self.circle.draw(win)
        self.point = Point(self.pos[0],self.pos[1])
        self.point.setOutline(self.color)
        self.point.setFill(self.color)
        self.point.draw(win)
        self.changed = False

    def update(self):
        # Stars under control of the same empire for long periods of time will
        # occasionally develop themselves.
        self.color = STAR_DEFAULT_COLOR
        self.radius = floor(min(self.power**(STAR_DISPLAY_RADIUS_EXP)*STAR_DISPLAY_RADIUS_MOD,\
        STAR_DISPLAY_MAX_RADIUS)+STAR_DISPLAY_RADIUS_BASE)
        self.homeStar = False
        if self.radius != self.oldRadius:
            self.changed = True
            self.oldRadius = self.radius
        if self.empire != -1:
            if self.empire in list(range(len(empires))):
                if empires[self.empire].originStar == self.id:
                    self.homeStar = True
            self.turnsPassed += 1
        self.revoltTimer -= 1
        if self.revoltTimer < 0 and self.revolt:
            self.revolt = False
            self.changed = True
        if self.homeStar:
            self.turnsPassed += 3
            self.color = ORIGIN_STAR_COLOR
        if self.empirePrev != self.empire:
            self.turnsPassed = 0
            self.empirePrev = self.empire
            self.changed = True
        if self.turnsPassed >= STAR_GROWTH_BASE+self.power:
            self.power += 1
            self.turnsPassed = 0

    def determineConnections(self):
        # Determine the stars that this star is connected to, so that the star
        # does not have to do it every time linkedStars() is called.
        for i in range(len(links)):
            if links[i].star1 == self.id:
                self.connectedTo.append(links[i].star2)
            if links[i].star2 == self.id:
                self.connectedTo.append(links[i].star1)

    def find(self):
        found = []
        for i,empire in enumerate(empires):
            for star in empire.controlledStars:
                if self.id == star:
                    found.append(i)
                    break
        return found

    def linkedStars(self):
        # Returns a list of the stars that are linked to this one.
        linked = []
        for index in self.connectedTo:
            linked.append(stars[index])
        return linked

    def linkedEmptyStars(self):
        # Returns a list of the empty stars that are linked to this one.
        emptyStars = []
        linked = self.linkedStars()
        for link in linked:
            if link.empire == -1:
                emptyStars.append(link)
        return emptyStars

    def linkedEmpireStars(self):
        # Return a list of the controlled stars that are linked to this one.
        empireStars = []
        linked = self.linkedStars()
        for link in linked:
            if link.empire != -1 and link.empire != self.empire:
                empireStars.append(link)
        return empireStars

    def findIsolated(self, distance=0, ignoreList=[]):
        isolated = []
        if distance == 0:
            ignoreList.append(self.id)
        if ISOLATED_CHECK_DRAW:
            self.color = "#FFFF00"
            self.draw()
            win.update()
            self.color = "#FF0000"
            self.draw()
            win.update()
            self.changed = True
        for star in self.linkedStars():
            if star.id not in ignoreList:
                ignoreList.append(star.id)
                star.findIsolated(distance+1, ignoreList)
        for star in stars:
            if star.id not in ignoreList:
                isolated.append(star.id)
        return isolated

    def linksToStar(self, starToFind, distance=0, ignoreList=[]):
        if distance == 0:
            ignoreList.append(self.id)
        for star in self.linkedStars():
            if star.id not in ignoreList:
                ignoreList.append(star.id)
                result = star.linksToStar(starToFind, distance+1, list(ignoreList))

    def starsWithinDistance(self, recursionsToDo, listOfStars=[]):
        if self.id not in listOfStars:
            listOfStars.append(self.id)
        #print(recursionsToDo)
        #self.color = "#FFFF00"
        #self.draw()
        #win.update()
        #if self.id == listOfStars[0]:
        #    self.color = "#00FF00"
        #else:
        #    self.color = "#FF0000"
        #self.draw()
        #win.update()
        #self.changed = True
        if recursionsToDo > 0:
            for star in self.linkedStars():
                star.starsWithinDistance(recursionsToDo-1, listOfStars)
        return listOfStars

class Link:
    # These connect stars together, and don't really do anything other than that.
    def __init__(self, pos1, pos2, star1, star2):
        self.pos1 = pos1
        self.pos2 = pos2
        self.star1 = star1
        self.star2 = star2
        self.empire = -1
        self.color = LINK_DEFAULT_COLOR
        self.line = Line(vecToPt(self.pos1),vecToPt(self.pos2))
        self.line.setOutline(self.color)
        self.line.setFill(self.color)
        self.draw()

    def draw(self):
        self.line.undraw()
        self.line = Line(vecToPt(self.pos1),vecToPt(self.pos2))
        self.line.setOutline(self.color)
        self.line.setFill(self.color)
        self.line.draw(win)

class DataPoint:
    def __init__(self, x, y, color):
        self.point = Point(x,y)
        self.color = color
        self.point.setFill(color_rgb(self.color[0],self.color[1],self.color[2]))
        self.point.setOutline(color_rgb(self.color[0],self.color[1],self.color[2]))
        self.point.draw(graph)

    def update(self):
        self.point.move(-1,0)
        if self.point.getX() < 0:
            self.point.undraw()

class Empire:
    # These expand into stars and fight each other for control of them.
    def __init__(self, id, originStar, strength):
        self.id = id
        self.originStar = originStar
        self.strength = strength
        self.resource = 0
        self.revoltRisk = 0
        self.controlledPower = strength
        self.controlledStars = [originStar]
        self.colonizeStars = [originStar]
        self.empireBorderStars = []
        self.developmentTendency = 0.3
        self.colonizeTendency = 0.2
        self.conquerTendency = 0.5
        self.nextAction = ""
        self.influenceColor = [\
        max(randomByte(),50),\
        max(randomByte(),50),\
        max(randomByte(),50)\
        ]
        stars[originStar].empire = self.id
        stars[originStar].empireColor = self.influenceColor
        self.determineNextAction()

    def determineNextAction(self):
        # Weight system for determining what the empire will do next.
        total = self.colonizeTendency+self.conquerTendency+self.developmentTendency
        nextAction = uniform(0,total)
        currentWeight = 0
        if nextAction > currentWeight and nextAction < currentWeight+self.colonizeTendency:
            self.nextAction = "colonize"
        currentWeight += self.colonizeTendency
        if nextAction > currentWeight and nextAction < currentWeight+self.conquerTendency:
            self.nextAction = "conquer"
        currentWeight += self.conquerTendency
        if nextAction > currentWeight and nextAction < currentWeight+self.developmentTendency:
            self.nextAction = "develop"

    def colonizeFrom(self, star):
        # Colonizes a random empty star that is linked to star.
        emptyStars = stars[star].linkedEmptyStars()
        self.controlledStars.append(emptyStars[randrange(0,len(emptyStars))].id)
        stars[self.controlledStars[len(self.controlledStars)-1]].power = 1
        stars[self.controlledStars[len(self.controlledStars)-1]].empire = self.id
        stars[self.controlledStars[len(self.controlledStars)-1]].empireColor = [255,255,255]
        stars[self.controlledStars[len(self.controlledStars)-1]].changed = True

    def organizeStars(self):
        # Determines which stars are able to call colonizeFrom(), and which
        # stars can be targeted by conquer().
        self.colonizeStars = []
        self.empireBorderStars = []
        for i in range(len(self.controlledStars)):
            linkedES = stars[self.controlledStars[i]].linkedEmptyStars()
            # If the star has an empty star linked to it, add it to
            # self.colonizeStars
            if linkedES != []:
                self.colonizeStars.append(self.controlledStars[i])
            # Add all stars that another empire controls and that also border
            # this star to self.empireBorderStars
            linkedEmS = stars[self.controlledStars[i]].linkedEmpireStars()
            for j in range(len(linkedEmS)):
                self.empireBorderStars.append(linkedEmS[j])

    def conquer(self,star):
        # Takes a star away from another empire and converts it to this empire.
        if max((log(empires[stars[star].empire].resource+1)+1),3)\
        *(stars[star].power/50+25) < self.strength:
            # Take away some of this empire's strength.
            self.strength -= max((log(empires[stars[star].empire].resource+1)+1),3)\
            *(stars[star].power/50+25)
            #print(star)
            #print(self.id)
            #print(stars[star].find())
            #print(stars[star].empire)
            #print(self.controlledStars)
            #print(empires[stars[star].empire].controlledStars)
            # Add the star to this empire's controlledStars.
            self.controlledStars.append(star)
            # Take the star away from the target's controlledStars.
            empires[stars[star].empire].controlledStars.remove(star)
            # Check to see if the target now has 0 stars. If so, delete that
            # empire and change the empire ids of all empires.
            if len(empires[stars[star].empire].controlledStars) == 0:
                del empires[stars[star].empire]
                for i,empire in enumerate(empires):
                    empire.id = i
                    for controlledStar in empire.controlledStars:
                        stars[controlledStar].empire = empire.id
            # Set the star's empire id to this empire's id.
            stars[star].empire = self.id
            # Set the star's color to white for one turn.
            stars[star].empireColor = [255,255,255]
            stars[star].changed = True
            # Halve the star's power, then round it up.
            stars[star].power = ceil(stars[star].power/2)

    def revolt(self):
        # Causes another empire to fragment from this one.
        randomStar = self.controlledStars[randint(0,len(self.controlledStars)-1)]
        revoltSize = 0
        if len(self.controlledStars) <= 100:
            revoltSize = 1
        elif len(self.controlledStars) > 100 and len(self.controlledStars) <= 200:
            revoltSize = 2
        elif len(self.controlledStars) > 200 and len(self.controlledStars) <= 400:
            revoltSize = 3
        elif len(self.controlledStars) > 400:
            revoltSize = 4
        newEmpireStrength = len(self.controlledStars)**1.3*3+500*revoltSize
        revoltingStars = stars[randomStar].starsWithinDistance(revoltSize,[])
        if self.originStar not in revoltingStars:
            newEmpire = Empire(len(empires),randomStar,newEmpireStrength)
            for star in revoltingStars:
                if star in self.controlledStars:
                    newEmpire.controlledStars.append(star)
                    self.controlledStars.remove(star)
                    stars[star].empire = newEmpire.id
                    stars[star].revoltTimer = 2
                    stars[star].revolt = True
                    stars[star].changed = True
            empires.append(newEmpire)

    def update(self):
        # This is called on every turn.
        # Calculate the controlledPower that an empire has.
        self.controlledPower = 0
        for i in range(len(self.controlledStars)):
            self.controlledPower += stars[self.controlledStars[i]].power
        for i in range(len(self.controlledStars)):
            # Updates all the stars to make sure that they have the correct ids.
            # Also ticks up the strength and resource of this empire.
            stars[self.controlledStars[i]].empire = self.id
            stars[self.controlledStars[i]].empireColor = self.influenceColor
        self.strength += 0.01*self.controlledPower
        self.resource += 0.15*self.controlledPower**0.8
        self.revoltRisk = max((log10(len(self.controlledStars))-1.5)/80,0)
        # Determine which stars can call which function.
        self.organizeStars()
        if len(self.controlledStars) > 0:
            if self.nextAction == "develop" and self.resource > 40:
                # Add 2 power to a random star.
                if len(self.controlledStars) == 1:
                    r = 0
                else:
                    r = randrange(0,len(self.controlledStars)-1)
                stars[self.controlledStars[r]].power += 2
                self.resource -= 40
                self.determineNextAction()
            if self.nextAction == "colonize" and self.resource > 100:
                # If there are stars left to colonize, do so. Otherwise,
                # determine another action. Only determines another action if
                # resource is above 100.
                if len(self.colonizeStars) != 0:
                    self.colonizeFrom(self.colonizeStars[randint(0,len(self.colonizeStars)-1)])
                    self.resource -= 100
                    self.determineNextAction()
                else:
                    self.determineNextAction()
            if self.nextAction == "conquer":
                # If there are stars left to conquer, do so. Otherwise,
                # if there is more than 100 resource, increment strength by 100.
                # Otherwise, determine another action.
                if len(self.empireBorderStars) != 0:
                    self.conquer(self.empireBorderStars[randint(0,len(self.empireBorderStars)-1)].id)
                    self.determineNextAction()
                elif self.resource > 100:
                    self.resource -= 100
                    self.strength += 100
                    self.determineNextAction()
                else:
                    self.determineNextAction()
            if random() < self.revoltRisk:
                self.revolt()
            for i in range(len(self.controlledStars)):
                stars[self.controlledStars[i]].empire = self.id
        # Print the status of the empire to the console.
        if PRINT_EMPIRE_STATUS:
            print(str(self.id)+" has "+str(round(self.resource,3))+" resource, "\
            +str(round(self.strength,3))+" strength, "+str(len(self.controlledStars))\
            +" stars, and "+str(self.controlledPower)+" power")

# Generate the stars
for i in range(NUMBER_OF_STARS):
    while True:
        respawn = False
        starToAdd = Star([randint(10,SCREEN_WIDTH-10),randint(10,SCREEN_HEIGHT-10)],i)
        if len(stars) > 0:
            for otherStar in stars:
                if dist(starToAdd.pos,otherStar.pos) < STAR_MINIMUM_SEPARATION:
                    respawn = True
        if not respawn:
            starToAdd.draw()
            stars.append(starToAdd)
            break
    win.update()

# If the stars are too close to one another, delete one of them
# This is now just a failsafe - the star generation algorithm removes close
# stars by itself now
for i,star1 in reversed(list(enumerate(stars))):
    for j,star2 in reversed(list(enumerate(stars))):
        if i != j and dist(star1.pos,star2.pos) < STAR_MINIMUM_SEPARATION:
            star1.point.undraw()
            del stars[i]
            win.update()
            break

# Reset star ids
for i,star in enumerate(stars):
    star.id = i

# Generate the links between stars
for i,star1 in enumerate(stars):
    # Find the shortest distance between each star
    distList = []
    for j,star2 in enumerate(stars):
        if i != j:
            distList.append([dist(star1.pos,star2.pos),j])
    distList = sorted(distList, key=lambda dist: dist[0])
    # Create a random amount of links between each star
    for j in range(randint(STAR_MINIMUM_LINKS,STAR_MAXIMUM_LINKS)):
        # If the link already exists, do not create it
        alreadyExists = False
        for link in links:
            if link.star1 == i and link.star2 == distList[j][1]\
            or link.star2 == i and link.star1 == distList[j][1]:
                alreadyExists = True
        if not alreadyExists:
            links.append(Link(star1.pos,stars[distList[j][1]].pos,i,distList[j][1]))
        star1.links += 1
        win.update()

for star in stars:
    star.determineConnections()

while True:
    tryingStar = 0
    isolatedStars = []
    while True:
        print("trying "+str(tryingStar))
        isolatedStars = stars[tryingStar].findIsolated(0,[])
        if len(isolatedStars) > len(stars)*0.9:
            tryingStar += 1
        else:
            break

    print(isolatedStars)
    if len(isolatedStars) == 0:
        break

    for i,index in list(enumerate(isolatedStars)):
        isolatedStars[i] = stars[index]

    groups = []

    for star in isolatedStars:
        starIsolatedGroup = star.findIsolated(0, [])
        if starIsolatedGroup not in groups:
            groups.append(starIsolatedGroup)

    for group in groups:
        starsToConnect = []
        for star in stars:
            if star.id not in group:
                starsToConnect.append(star.id)
        distList = []
        for i1 in starsToConnect:
            for i2 in group:
                distList.append([dist(stars[i1].pos,stars[i2].pos),i1,i2])
        distList = sorted(distList, key=lambda dist: dist[0])
        links.append(Link(stars[distList[0][1]].pos,stars[distList[0][2]].pos,\
        distList[0][1],distList[0][2]))

    for star in stars:
        star.color = "#FFFFFF"
        star.draw()
        star.changed = True

    for star in stars:
        star.determineConnections()

def spawnEmpire(empireId):
    global alltimeEmpires
    r = randint(0,len(stars)-1)
    print(r,alltimeEmpires,stars[r].empire)
    if stars[r].empire == -1 and len(stars[r].find()) == 0:
        empires.append(Empire(empireId,r,1))
        alltimeEmpires += 1
    else:
        print("respawn")
        spawnEmpire(empireId)

for i in range(NUMBER_OF_EMPIRES):
    spawnEmpire(alltimeEmpires)

timer = 0

while open:
    # Turn loop
    if (time.time() > t3+TURN_DELAY):
        print(timer)
        if (timer % 10 == 0):
            for empire in empires:
                points.append(DataPoint(\
                499,\
                500-empire.controlledPower/40,\
                empire.influenceColor))
            for i,point in enumerate(points):
                point.update()
                if point.point.getX() < 0:
                    del points[i]
        if timer % 20 == 0:
            # Make sure a star can only be controlled by one empire.
            for star in stars:
                for i,empireId in enumerate(star.find()):
                    if star.empire != empireId:
                        empires[empireId].controlledStars.remove(star.id)
            # Delete empires with 0 stars.
            for empire in empires:
                if len(empire.controlledStars) == 0:
                    del empires[empire.id]
        # Iterate through all stars, and update all of them.
        for star in stars:
            star.update()
        # Verify that the empire ids are equal to their indexes.
        for i,empire in enumerate(empires):
            empire.id = i
            for index in empire.controlledStars:
                stars[index].empire = empire.id
        # Iterate through all empires, and update all of them. If the length of
        # empires changes through conquest, the loop may break itself in order
        # to avoid a crash.
        for i,empire in enumerate(empires):
            if i >= len(empires):
                break
            empire.update()
        timer += 1
        t3 = time.time()
    # Draw loop
    if (time.time() > t+1/fps):
        for star in stars:
            if star.changed:
                star.draw()
        if UPDATE_LINKS:
            for link in links:
                link.draw()
        t = time.time()
        win.update()
        frame += 1
