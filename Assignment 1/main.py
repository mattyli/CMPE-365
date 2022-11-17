# Convex hull - Modified by Matthew Li (20217346)
#
# Usage: python main.py [-d] file_of_points
#
# You can press ESC in the window to exit.
#   PyOpenGL, GLFW


import sys, os, math

try: # PyOpenGL
  from OpenGL.GL import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(1)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(1)

# Globals

garbagePoints = set()

window = None

windowWidth  = 800 # window dimensions
windowHeight = 800

minX = None # range of points
maxX = None
minY = None
maxY = None

r  = 0.01 # point radius as fraction of window size

numAngles = 32
thetas = [ i/float(numAngles)*2*3.14159 for i in range(numAngles) ] # used for circle drawing

allPoints = [] # list of points

lastKey = None  # last key pressed

discardPoints = False

# Point
#
# A Point stores its coordinates and pointers to the two points beside
# it (CW and CCW) on its hull.  The CW and CCW pointers are None if
# the point is not on any hull.
#
# For debugging, you can set the 'highlight' flag of a point.  This
# will cause the point to be highlighted when it's drawn.

class Point(object):

    def __init__( self, coords ):

      self.x = float( coords[0] ) # coordinates
      self.y = float( coords[1] )

      self.ccwPoint = None # point CCW of this on hull
      self.cwPoint  = None # point CW of this on hull

      self.highlight = False # to cause drawing to highlight this point


    def __repr__(self):
      return 'pt(%g,%g)' % (self.x, self.y)

    def drawPoint(self):

      # Highlight with yellow fill
      
        if self.highlight:
            glColor3f( 0.9, 0.9, 0.4 )
            glBegin( GL_POLYGON )
            for theta in thetas:
                glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
            glEnd()
    

      # Outline the point
      
        glColor3f( 0, 0, 0 )
        glBegin( GL_LINE_LOOP )
        for theta in thetas:
            glVertex2f( self.x+r*math.cos(theta), self.y+r*math.sin(theta) )
        glEnd()

      # Draw edges to next CCW and CW points.

        if self.ccwPoint:
            glColor3f( 0, 0, 1 )
            drawArrow( self.x, self.y, self.ccwPoint.x, self.ccwPoint.y )

        if self.cwPoint:
            glColor3f( 1, 0, 0 )
            drawArrow( self.x, self.y, self.cwPoint.x, self.cwPoint.y )

# Draw an arrow between two points, offset a bit to the right

def drawArrow( x0,y0, x1,y1 ):

    d = math.sqrt( (x1-x0)*(x1-x0) + (y1-y0)*(y1-y0) )

    vx = (x1-x0) / d      # unit direction (x0,y0) -> (x1,y1)
    vy = (y1-y0) / d

    vpx = -vy             # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 1.5*r*vx - 0.4*r*vpx # arrow tail
    ya = y0 + 1.5*r*vy - 0.4*r*vpy

    xb = x1 - 1.5*r*vx - 0.4*r*vpx # arrow head
    yb = y1 - 1.5*r*vy - 0.4*r*vpy

    xc = xb - 2*r*vx + 0.5*r*vpx # arrow outside left
    yc = yb - 2*r*vy + 0.5*r*vpy

    xd = xb - 2*r*vx - 0.5*r*vpx # arrow outside right
    yd = yb - 2*r*vy - 0.5*r*vpy

    glBegin( GL_LINES )
    glVertex2f( xa, ya )
    glVertex2f( xb, yb )
    glEnd()

    glBegin( GL_POLYGON )
    glVertex2f( xb, yb )
    glVertex2f( xc, yc )
    glVertex2f( xd, yd )
    glEnd()
      
# Determine whether three points make a left or right turn

LEFT_TURN  = 1
RIGHT_TURN = 2
COLLINEAR  = 3

def turn(a: Point, b: Point, c: Point)->int:            # a, b, c --> points

    det = (a.x-c.x) * (b.y-c.y) - (b.x-c.x) * (a.y-c.y)             # det = determinant

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR

# turn() returns whether the next point on the line is either left, right or collinear

# Build a convex hull from a set of point
# Use the method described in class

def buildHull(points: list[Point]):               # points is a list of points
    n = len(points)
    # BASE CASE (n <= 3), this would be the end of recursion, we have less than 3 points
    if n <= 3:
        #print("BASE CASE REACHED CONSTRUCTING MINIMUM HULL")

        for idx in range(n):            # accessing elements by index num so i can do modular arithmetic
            points[idx].cwPoint  = points[(idx+1) % n]          # need the modulo to bring back value within array range
            points[idx].ccwPoint = points[(idx+n-1) % n]        # these expressions only hold true for len(points) <= 3

            # print("THE CW POINT of " + repr(points[idx]) + repr(points[idx].cwPoint) + "\n")
            # print("THE CCW POINT of " + repr(points[idx]) + repr(points[idx].ccwPoint) + "\n")
        return                                       # return to the calling statement (this is recursion)
        
            
    else:
        # partition the input into two sets, those above and below the median
        # this MAY NOT work, I chose to divide the list into two from the middle of the list
        middex = len(points)//2         # BIG PROBLEM HERE      
        print(str(middex) + "MIDDLE INDEX\n")     
        left = points[:middex]
        print("LEFT HULL" +str(left) + "\n")
        
        right = points[middex:]
        buildHull(right)                 # input arrays should be modified (Point class is mutable)
        display(True)
        print("BUILDING RIGHT HULL\n")
        buildHull(left)
        display(True)
        print("NOW MERGE HULLS\n")
        mergeHulls(left, right)
        display(True)
    



    """
        Try to combine walkUp() and walkDown() into a single walk(l, r, direction)
        This function (given two points), should walk and join the vertically
        extreme points on each convex hull
    """
def merge(leftHull: list[Point], rightHull: list[Point])->None:
    LUP = max(leftHull, key = lambda x: x.x)
    RUP = min(rightHull, key = lambda x: x.x)

    LD = LUP
    RD = RUP

    while turn(LUP.ccwPoint, LUP, RUP) == LEFT_TURN or turn(LUP, RUP, RUP.cwPoint) == LEFT_TURN:
        if turn(LUP.ccwPoint, LUP, RUP) == LEFT_TURN:
            LUP = LUP.ccwPoint
        else:
            RUP = RUP.cwPoint
    
    while turn(LD.ccwPoint, LD, RD) == RIGHT_TURN or turn(LD, RD, RD.cwPoint) == RIGHT_TURN:
        if turn(LD.ccwPoint, LD, RD) == RIGHT_TURN:
            LD = LD.cwPoint
        else:
            RD = RD.ccwPoint
    
    LUP.cwPoint = RUP
    RUP.ccwPoint = LUP
    LD.ccwPoint = RD
    RD.cwPoint = LD
    return
    

def mergeHulls(leftHull: list[Point], rightHull: list[Point])->None:
    left = max(leftHull, key = lambda x: x.x)
    right = min(rightHull, key = lambda x: x.x)
    
    leftDown = left
    rightDown = right
    # print("WALKUP LEFT: " + repr(left))
    # print("LEFT CURRENT CW: " + repr(left.cwPoint))
    walkUpAndJoin(left, right)              # rightmost point of the left hull and leftmost point of the right hull
    display(True)

    # print("WALKDOWN LEFT: " + repr(left))          # these might not be the same, even though they should be
    # print("LEFT CURRENT CW: " + repr(left.cwPoint))
    # print("RIGHT = " + repr(right))
    walkDownAndJoin(leftDown, rightDown)
    display(True)
    return


def walkUpAndJoin(left: Point, right: Point)->list[Point]: # ret the topmost value of each HULL respectively
    # FIRST WHILE LOOP IS WALK UP
    while turn(left.ccwPoint, left, right) == LEFT_TURN or turn(left, right, right.cwPoint) == LEFT_TURN:
        if turn(left.ccwPoint, left, right) == LEFT_TURN:
            if left not in garbagePoints:
                garbagePoints.add(left)
            left = left.ccwPoint
        else:
            if right not in garbagePoints:
                garbagePoints.add(right)
            right = right.cwPoint

    left.cwPoint = right
    right.ccwPoint = left
    #print("LEFT CCW = " +repr(left.ccwPoint) + ", RIGHT CW = " + repr(right.cwPoint))
    return

def walkDownAndJoin(left: Point, right: Point)->None:
    #print("WALKING DOWN\n")
    # WALKING DOWN 

    # ORIGINAL : 
    while turn(left.ccwPoint, left, right) == RIGHT_TURN or turn(left, right, right.cwPoint) == RIGHT_TURN:
        right.highlight = True
        if turn(left.ccwPoint, left, right) == RIGHT_TURN:
            if left not in garbagePoints:
                garbagePoints.add(left)
            left = left.ccwPoint
        else:
            right.highlight = False
            if right not in garbagePoints:
                garbagePoints.add(right)
            right = right.cwPoint
    
    # while turn(left.ccwPoint, left, right) == RIGHT_TURN or turn(left, right, right.cwPoint) == RIGHT_TURN:
    #     if turn(left.ccwPoint, left, right) == RIGHT_TURN:
    #         left = left.cwPoint
    #     else:
    #         right = right.ccwPoint
    
    right.cwPoint = left
    left.ccwPoint = right
    return
    

    # Handle recursive case.S
    #
    # After you get the hull-merge working, do the following: For each
    # point that was removed from the convex hull in a merge, set that
    # point's CCW and CW pointers to None.  You'll see that the arrows
    # from interior points disappear after you do this.
    #
    # [YOUR CODE HERE]

    # You can do the following to help in debugging.  This highlights
    # all the points, then shows them, then pauses until you press
    # 'p'.  While paused, you can click on a point and its coordinates
    # will be printed in the console window.  If you are using an IDE
    # in which you can inspect your variables, this will help you to
    # identify which point on the screen is which point in your data
    # structure.
    #
    # This is good to do, for example, after you have recursively
    # built two hulls, to see that the two hulls look right.
    #
    # This can also be done immediately after you have merged to hulls
    # ... again, to see that the merged hull looks right.
    #
    # Always after you have inspected things, you should remove the
    # highlighting from the points that you previously highlighted.

    for p in points:
        p.highlight = True
    display(wait=True)

    # At the very end of buildHull(), you should display the result
    # after every merge, as shown below.  This call to display() does
    # not pause.
    
    display()

windowLeft   = None
windowRight  = None
windowTop    = None
windowBottom = None

# Set up the display and draw the current image

def display( wait=False ):

    global lastKey, windowLeft, windowRight, windowBottom, windowTop
    
    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor( 1,1,1,0 )
    glClear( GL_COLOR_BUFFER_BIT )
    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()

    glMatrixMode( GL_MODELVIEW )
    glLoadIdentity()

    windowLeft   = -0.1*(maxX-minX)+minX
    windowRight  =  1.1*(maxX-minX)+minX
    windowTop    =  1.1*(maxY-minY)+minY
    windowBottom = -0.1*(maxY-minY)+minY

    glOrtho( windowLeft, windowRight, windowBottom, windowTop, 0, 1 )

    # Draw points and hull

    for p in allPoints:
        p.drawPoint()

    # Show window

    glfw.swap_buffers( window )

    # Maybe wait until the user presses 'p' to proceed
    
    if wait:

        sys.stderr.write( 'Press "p" to proceed ' )
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80: # wait for 'p'
            glfw.wait_events()
            if glfw.window_should_close( window ):
              sys.exit(0)
            display()

        sys.stderr.write( '\r                     \r' )
        sys.stderr.flush()

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

    global lastKey
    
    if action == glfw.PRESS:
    
        if key == glfw.KEY_ESCAPE:      # quit upon ESC
            glfw.set_window_should_close( window, GL_TRUE )
        else:
            lastKey = key

# Handle window reshape
def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight

# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    if action == glfw.PRESS:

        # Find point under mouse

        x,y = glfw.get_cursor_pos( window ) # mouse position

        wx = (x-0)/float(windowWidth)  * (windowRight-windowLeft) + windowLeft
        wy = (windowHeight-y)/float(windowHeight) * (windowTop-windowBottom) + windowBottom

        minDist = windowRight-windowLeft
        minPoint = None
        for p in allPoints:
            dist = math.sqrt( (p.x-wx)*(p.x-wx) + (p.y-wy)*(p.y-wy) )
            if dist < r and dist < minDist:
                minDist = dist
                minPoint = p

        # print point and toggle its highlight

        if minPoint:
            minPoint.highlight = not minPoint.highlight
            print( minPoint )

# Initialize GLFW and run the main event loop
# to run --> python3 main.py points1.txt

def main():

    global window, allPoints, minX, maxX, minY, maxY, r, discardPoints
    
    # Check command-line args

    if len(sys.argv) < 2:
        print( 'Usage: %s filename' % sys.argv[0] )
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        print( args )
        if args[0] == '-d':
            discardPoints = not discardPoints
        args = args[1:]

    # Set up window
  
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )
    glfw.swap_interval( 1 )
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # Read the points

    with open( args[0], 'rb' ) as f:
      allPoints = [ Point( line.split(b' ') ) for line in f.readlines() ]

    # FOR DEBUGGING
    print(len(allPoints))
    print(type(allPoints[0]))
    print(allPoints)

    # Get bounding box of points

    minX = min( p.x for p in allPoints )
    maxX = max( p.x for p in allPoints )
    minY = min( p.y for p in allPoints )
    maxY = max( p.y for p in allPoints )

    # Adjust point radius in proportion to bounding box
    
    if maxX-minX > maxY-minY:
        r *= maxX-minX
    else:
        r *= maxY-minY

    # Sort by increasing x.  For equal x, sort by increasing y.
    # Left --> Right (Increasing X)
    
    allPoints.sort( key=lambda p: (p.x,p.y) )
    # for debugging

    # Run the code
    
    buildHull(allPoints)

    # Wait to exit

    while not glfw.window_should_close( window ):
        glfw.wait_events()

    glfw.destroy_window( window )
    glfw.terminate()
    


if __name__ == '__main__':
    main()
