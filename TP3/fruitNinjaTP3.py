from cmu_graphics import *
from PIL import Image
import random
import math
import os, pathlib

# CITATION: Taken from sound demo posted on Piazza @2147
def loadSound(relativePath):
    # Convert to absolute path (because pathlib.Path only takes absolute paths)
    absolutePath = os.path.abspath(relativePath)
    # Get local file URL
    url = pathlib.Path(absolutePath).as_uri()
    # Load Sound file from local URL
    return Sound(url)

# ------------------------------------------------------------------------------
# CITATION: https://www.cs.cmu.edu/~112-f22/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

contentsRead = readFile("highScore.txt")
splitLine = contentsRead.splitlines()


# ------------------------------------------------------------------------------
def onAppStart(app):
    app.gameStartSound = loadSound("Game-start.wav")
    app.gameStartSound.play()
    reset(app)

def reset(app):
    
    # IMAGE1 CITATION: https://www.debongo.com/fruit-ninja-review/
    app.image1 = Image.open("background.jpg")
    app.image1 = CMUImage(app.image1)
    
    # IMAGE2 CITATION: https://uhudshop.blogspot.com/2011/12/fruit-ninja-game-cute-hd-wallpapers.html
    app.image2 = Image.open('fruitNinjaTitle.webp')
    app.image2 = CMUImage(app.image2)
    
    #IMAGE3 CITATION: https://fruitninja.fandom.com/wiki/Zen_Mode
    app.image3 = Image.open('Icon_zen.webp')
    app.image3 = CMUImage(app.image3)

    #IMAGE4 CITATION: https://fruitninja.fandom.com/wiki/Classic_Mode
    app.image4 = Image.open('Icon_classic.webp')
    app.image4 = CMUImage(app.image4)

    #IMAGE5 CITATION: https://www.pocketgamer.com/fruit-ninja/halfbrick-shares-10-tips-tricks-and-secrets-for-fruit-ninja-on-ios/
    app.image5 = Image.open('gameOver.jpg')
    app.image5 = CMUImage(app.image5)

    # CITATION SOUNDS: https://www.sounds-resource.com/mobile/fruitninja/sound/6076/
    app.bombSound = loadSound("Bomb-explode.wav")
    app.sliceSound = loadSound("Clean-Slice-1.wav")
    app.clearBombSound = loadSound("Bonus-Firework-Explode.wav")
    app.levelUpSound = loadSound("New-best-score.wav")
    app.pauseSound = loadSound('Pause.wav')
    app.buttonPressSound = loadSound("Next-screen-button.wav")
    app.gameOverSound = loadSound("Game-over.wav")
    
    
    app.width = 800
    app.height = 500
    app.stepsPerSecond = 60
    app.isGameOver = False
    app.lives = 10
    app.scoreValue = 0
    app.mouseTrack = []
    app.blade = Blade()
    app.drawStartScreen = True
    app.isZenMode = False
    app.isOriginalMode = False
    app.timer = 60 # for zen mode
    app.drawScoreScreen = False # for zen mode
    app.fruitsUpdated = False
    app.levelUp = False
    app.levelUpDisplayTime = 0.5 
    app.lastLevelUpScore = 0
    app.clearEffectTimer = 0
    app.highScore = int(splitLine[0])
    app.isPaused = False
    app.drawInstructionsScreen = False
    createFruits(app)


# Creating my classes
class Blade:
    def __init__(self):
        self.power = 1
        self.isBlueBlade = False
        self.freezeDuration = 0

    
    def attack(self, target, app):
        if not target.sliced:
            angle = random.uniform(0, math.pi * 2)
            target.slice(angle)
            target.falling = True
            if isinstance(target, IceCube):
                self.isBlueBlade = True
                self.freezeDuration = 800  # Sets blue blade duration
            elif self.isBlueBlade:
                target.frozen = True  # Freeze effect for fruits  

class Fruit:
    def __init__(self):
        self.size = random.randint(30, 45)
        self.x = random.randint(0, 400 - self.size)
        self.y = 500 - self.size/2
        self.sliced = False
        self.falling = False
        self.fallSpeed = random.randint(4, 8)
        self.sliceAngle = 0
        self.half1Offset = 0
        self.half2Offset = 0
        self.launchSpeed = random.uniform(8, 11)
        self.launchAngle = random.uniform(math.pi / 3, 3 * math.pi / 6)
        self.time = 0
        self.isActive = True
        self.frozen = False
        self.shape = random.choice(['watermelon', 'pineapple', 'dragonFruit', 'banana', 'pomegranate'])
        self.rotationAngle = random.uniform(0, 360)

    # CITATION: https://stackoverflow.com/questions/21368210/how-to-make-an-object-move-in-the-path-of-an-arc
    # Used similar physics so fruits would move in parabolic shape
    def update(self, timeStep, app):
        if self.isActive and not self.frozen:
            self.time += timeStep
            self.x += self.launchSpeed * math.cos(self.launchAngle) * self.time
            self.y -= (self.launchSpeed * math.sin(self.launchAngle) * self.time - 0.5 * 9.8 * self.time ** 2)
            # when fruit leaves the screen reinitialize
            if self.y >= 500:   
                if not self.sliced:
                    if app.isOriginalMode and not app.blade.isBlueBlade and not app.levelUp:
                        app.lives -= 1   
                self.__init__()
            self.rotationAngle += 5  # Adjust this value to control rotation speed
            self.rotationAngle %= 360

        if self.frozen:
            self.time *= 5

        if self.sliced:
            # used later when drawing the sliced fruit via arcs
            self.half1Offset += 1
            self.half2Offset += 1

        if self.falling:
            self.y += self.fallSpeed

    def slice(self, startPoint, endPoint):
        self.sliced = True
        self.falling = True

        #intersection point of the blade with the fruit
        dx = endPoint[0] - startPoint[0]
        dy = endPoint[1] - startPoint[1]
        bladeAngle = math.atan2(dy, dx)

        # Calculate the angle between the blade and the horizontal axis
        horizontalAngle = math.atan2(dy, dx)

        self.sliceAngle = bladeAngle
        self.sliceParams = [(self.sliceAngle, self.size)]

class Bomb:
    def __init__(self):
        self.size = random.randint(30, 50)
        self.x = random.randint(0, 400 - self.size)
        self.y = 500 - self.size/2
        self.fallSpeed = random.randint(4, 8)
        self.launchSpeed = random.uniform(10, 15)
        self.launchAngle = random.uniform(math.pi / 3, 4 * math.pi / 9)
        self.time = 0
        self.isActive = True
    
    # CITATION: https://stackoverflow.com/questions/21368210/how-to-make-an-object-move-in-the-path-of-an-arc
    # Used similar physics so bomb would move in parabolic shape
    def update(self, timeStep):
        if self.isActive:
            self.time += timeStep
            self.x += self.launchSpeed * math.cos(self.launchAngle) * self.time
            self.y -= (self.launchSpeed * math.sin(self.launchAngle) * self.time - 0.5 * 9.8 * self.time ** 2)
            
            # when bomb leaves the screen reinitialize
            if self.y >= 500:  
                self.__init__()
class ClearBomb:
    def __init__(self):
        self.size = random.randint(30, 50)
        self.x = random.randint(0, 400 - self.size)
        self.y = 500 - self.size / 2
        self.fallSpeed = random.randint(4, 8)
        self.launchSpeed = random.uniform(10, 15)
        self.launchAngle = random.uniform(math.pi / 3, 4 * math.pi / 9)
        self.time = 0
        self.isActive = True

    # CITATION: https://stackoverflow.com/questions/21368210/how-to-make-an-object-move-in-the-path-of-an-arc
    # Used similar physics so clear bomb would move in parabolic shape
    def update(self, timeStep):
        if self.isActive:
            self.time += timeStep
            self.x += self.launchSpeed * math.cos(self.launchAngle) * self.time
            self.y -= (self.launchSpeed * math.sin(self.launchAngle) * self.time - 0.5 * 9.8 * self.time ** 2)
            # when clear bomb leaves the screen reinitialize
            if self.y >= 500:  
                self.__init__()

class IceCube:
    def __init__(self):
        self.size = random.randint(30, 50)
        self.x = random.randint(0, 400 - self.size)
        self.y = 500 - self.size/2
        self.launchSpeed = random.uniform(10, 20)
        self.launchAngle = random.uniform(math.pi / 3, 4 * math.pi / 9)
        self.time = 0
        self.isActive = True
        self.sliced = False
        self.falling = False
        self.fallSpeed = random.randint(4, 8)
        self.sliceAngle = 0
        self.half1Offset = 0
        self.half2Offset = 0

    # CITATION: https://stackoverflow.com/questions/21368210/how-to-make-an-object-move-in-the-path-of-an-arc
    # Used similar physics so ice cubes would move in parabolic shape
    def update(self, timeStep):
        if self.isActive and not self.falling:
            self.time += timeStep
            self.x += self.launchSpeed * math.cos(self.launchAngle) * self.time
            self.y -= (self.launchSpeed * math.sin(self.launchAngle) * self.time - 0.5 * 9.8 * self.time ** 2)
            # when ice cubes leaves the screen reinitialize
            if self.y >= 500:  
                self.__init__()

        if self.sliced:
            self.half1Offset += 1
            self.half2Offset += 1

        if self.falling:
            self.y += self.fallSpeed

    def slice(self, startPoint, endPoint):
        self.sliced = True
        self.falling = True

        # intersection point of the blade with the ice
        dx = endPoint[0] - startPoint[0]
        dy = endPoint[1] - startPoint[1]
        bladeAngle = math.atan2(dy, dx)

        # Calculate the angle between the blade and the horizontal axis
        horizontalAngle = math.atan2(dy, dx)

        self.sliceAngle = bladeAngle
        self.sliceParams = [(self.sliceAngle, self.size)]
 

def createFruits(app):
    # as score increases, game metrics get harder and harder, while the number
    # of fruits and bombs are still randomized, they go up higher and higher
    # in order to increase difficulty of the game
        if app.scoreValue <= 200:
            numFruits = random.randint(3, 5)
            numBombs = random.randint(0, 3)
        elif 200 < app.scoreValue <= 400:
            numFruits = random.randint(4, 7)
            numBombs = random.randint(0, 3)
        elif 400 < app.scoreValue <= 600:
            numFruits = random.randint(6, 8)
            numBombs = random.randint(0, 3)
        elif 600 < app.scoreValue <= 800:
            numFruits = random.randint(8, 10)
            numBombs = random.randint(1, 3)
        elif 800 < app.scoreValue <= 1000:
            numFruits = random.randint(9, 11)
            numBombs = random.randint(1, 3)
        else:
            numFruits = random.randint(10, 12)
            numBombs = random.randint(1, 3)
            

        app.fruits = [Fruit() for _ in range(numFruits)]
        app.bombs = [Bomb() for _ in range(numBombs)]
        
        numIceCubes = random.randint(0, 2)
        app.iceCubes = [IceCube() for _ in range(numIceCubes)]
        
        numClearBombs = random.randint(1, 2)
        app.clearBombs = [ClearBomb() for _ in range(numClearBombs)]

# drawing out my different screens
def drawStartScreen(app):
    drawImage(app.image2, 30, 20, width = app.width-60, height = (app.height/1.5)-40)
    drawImage(app.image4, 250, 400, width = 150, height = 150, align = 'center')
    drawImage(app.image3, 500, 400, width = 150, height = 150, align = 'center')
    drawCircle(20 ,20, 10)
    drawLabel('?', 20, 20, size = 20, fill = 'white')
   
def drawInstructionsScreen(app):
    drawRect(0, 0, app.width, app.height, fill = 'maroon')
    drawRect(20, 20, app.width - 40, app.height - 40, fill = 'saddleBrown')
    drawLabel('X', 760, 40, size = 30, bold = True)
    drawLabel('Instructions',app.width/2, 60, size = 50)
    drawLabel('In ORIGINAL mode click and drag your mouse to slice the fruit making sure to', app.width/2, 150, size = 20)
    drawLabel('avoid bombs and slice all the fruit. For every missed fruit a life is lost', app.width/2, 180, size = 20)
    drawLabel('and if you slice a bomb it is Game Over, If you slice an ice cube the', app.width/2, 210, size = 20)
    drawLabel('fruits slow down and no bombs will appear.', app.width/ 2, 240, size = 20)

    drawLabel('In ZEN mode use your mouse to slice the fruit making sure to avoid', app.width/2, 300, size = 20)
    drawLabel('the clear bombs. For every clear bomb hit, 2 seconds of you time is wasted.', app.width/2, 330, size = 20)
    drawLabel('The goal is to slice as many fruit as possible in 60 seconds.', app.width/2, 360, size = 20)
    drawLabel('Good Luck!',app.width/2, 430, size = 50)
   

def drawLevelUpScreen(app):
    app.levelUpSound.play()
    drawRect(0, 0, app.width, app.height, fill='green', opacity = 70)  # Semi-transparent overlay
    drawLabel('Level Up!', app.width/2, app.height/2, size=40, fill='white', align='center')

def drawScoreScreen(app):
    app.gameOverSound.play()
    drawImage(app.image1, 0, 0, width = app.width, height = app.height)
    drawLabel(f'Score: {app.scoreValue}', 400, 100, size = 50, fill = 'white')
    drawRect(400, 300, 200, 150, fill = 'saddleBrown', align = 'center', border = 'black')
    drawLabel('Retry', 400, 300, size = 30)

def drawGameOverScreen(app):
    app.gameOverSound.play()
    drawRect(0,0, app.width, app.height, fill = 'maroon')
    drawImage(app.image5, 0, 0, width = app.width, height = app.height/2)
    drawLabel("Click Anywhere To Retry", 400, 300, size = 30, font = 'orbitron')
    drawLabel(f'Score: {app.scoreValue}', 400, 350, size = 30, font = 'orbitron')
    drawLabel(f'High Score: {app.highScore}', 400, 400, size = 30, font = 'orbitron')

def drawGamePlayScreen(app):
    drawImage(app.image1, 0, 0, width = app.width, height = app.height)
    drawLabel(f'Score: {app.scoreValue}', 50, 20, size= 20, fill='white')
    
    # drawing out fruit
    if app.clearEffectTimer <= 0:
        for fruit in app.fruits:
            if fruit.sliced:
                half1X = fruit.x + fruit.half1Offset
                half2X = fruit.x - fruit.half2Offset
                for angle, size in fruit.sliceParams:
                    # sliced fruit drawings
                    if fruit.shape == 'watermelon':
                        drawArc(half1X, fruit.y, size, size, math.degrees(angle), 180, fill = 'green', border='black')
                        drawArc(half2X, fruit.y, size, size, math.degrees(angle) + 180, 180, fill= 'green', border='black')
                        drawArc(half1X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle), 180, fill = 'red', border = 'black')
                        drawArc(half2X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle) + 180, 180, fill= 'red', border = 'black')
                    if fruit.shape == 'pineapple':
                        drawArc(half1X, fruit.y, fruit.size, 2 * fruit.size, math.degrees(angle), 180, fill='yellow', border='orange')
                        drawArc(half2X, fruit.y, fruit.size, 2 * fruit.size, math.degrees(angle) + 180, 180, fill='yellow', border='orange')
                        # drawing out the pineapple spikes
                        for i in range(-3, 1):
                            drawLine(half1X, fruit.y - fruit.size, half1X + i * 10, fruit.y - fruit.size - 15, fill='green', lineWidth=3)
                        for i in range(0, 4):
                            drawLine(half1X, fruit.y - fruit.size, half1X + i * 10, fruit.y - fruit.size - 15, fill='green', lineWidth=3)
                    if fruit.shape == 'dragonFruit':  
                        drawArc(half1X, fruit.y, size, size, math.degrees(angle), 180, fill='deepPink', border='green')
                        drawArc(half2X, fruit.y, size, size, math.degrees(angle) + 180, 180, fill='deepPink', border='green')
                        drawArc(half1X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle), 180, fill='white', border = 'black')
                        drawArc(half2X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle) + 180, 180, fill='white', border = 'black')
                    if fruit.shape == 'banana':
                        drawArc(half1X, fruit.y, math.floor(1.5 *(fruit.size/4)), math.floor(1.5 *(fruit.size/2)), math.degrees(angle), 180, fill='yellow', border='black')
                        drawArc(half2X, fruit.y, math.floor(1.5 * (fruit.size/4)), math.floor(1.5 * (fruit.size/2)), math.degrees(angle) + 180, 180, fill='yellow', border='black')
                    if fruit.shape == 'pomegranate':
                        drawArc(half1X, fruit.y, size, size, math.degrees(angle), 180, fill='white', border='red')
                        drawArc(half2X, fruit.y, size, size, math.degrees(angle) + 180, 180, fill='white', border='red')
                        drawArc(half1X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle), 180, fill='red', border='black')
                        drawArc(half2X, fruit.y, 0.7 * size, 0.7 * size, math.degrees(angle) + 180, 180,fill='red', border='black')
                        
            else:
                # unsliced fruit drawings
                if fruit.shape == 'watermelon':
                    drawOval(fruit.x, fruit.y, fruit.size, fruit.size*1.2, fill= 'green', border='black', rotateAngle = fruit.rotationAngle)
                    drawOval(fruit.x, fruit.y, 0.7 * fruit.size, 0.7 * fruit.size * 1.2, fill= 'lightGreen', rotateAngle = fruit.rotationAngle)
                
                if fruit.shape == 'pineapple':
                    drawOval(fruit.x, fruit.y, fruit.size, 2 * fruit.size, fill='yellow', border='orange')
                    # drawing out pinapple spikes
                    for i in range(-3, 4):
                            drawLine(fruit.x, fruit.y - fruit.size, fruit.x + i * 10, fruit.y - fruit.size - 15, fill='green', lineWidth=3)
                
                if fruit.shape == 'dragonFruit':
                    # drawing spikes around the entire fruit
                    numSpikes = 20  
                    for i in range(numSpikes):
                        angle = (2 * math.pi / numSpikes) * i
                        spikeLength = fruit.size / 10  
                        spikeX = fruit.x + math.cos(angle) * (fruit.size/2)
                        spikeY = fruit.y + math.sin(angle) * (fruit.size/2)
                        drawLine(spikeX, spikeY, spikeX + math.cos(angle) * spikeLength, spikeY + math.sin(angle) * spikeLength, fill='lightGreen', lineWidth=2, rotateAngle = fruit.rotationAngle)
                                
                    drawOval(fruit.x, fruit.y, fruit.size, fruit.size, fill= 'deepPink', border='green', rotateAngle = fruit.rotationAngle)
                    drawOval(fruit.x, fruit.y, 0.7 * fruit.size, 0.7 * fruit.size, fill= 'white', rotateAngle = fruit.rotationAngle)
                
                if fruit.shape == 'banana':
                    # brown part on top of stem
                    stemWidth = fruit.size / 8
                    stemHeight = fruit.size / 5
                    stemX = fruit.x + fruit.size/4 - stemWidth/2
                    stemY = fruit.y - stemHeight/2
                    drawRect(stemX- fruit.size/4, stemY - 1.5* (fruit.size/2) , stemWidth, stemHeight, fill='brown', border = 'black')
                    
                    # body of banana
                    bananaAngle = 45
                    drawArc(fruit.x, fruit.y, 1.5 * (fruit.size/2), 1.5* (fruit.size), bananaAngle, 180, fill='yellow', border='black')

                if fruit.shape == 'pomegranate':
                    drawOval(fruit.x, fruit.y, fruit.size, fruit.size, fill='red', border='darkRed')
                    
                    # spikes on top of pomegranate
                    for i in range(-1, 2):
                            drawLine(fruit.x, fruit.y - fruit.size/2 , fruit.x + i * 10, math.floor(fruit.y - (fruit.size/1.5)), fill='darkRed', lineWidth=3)  
    
    if app.timer > 0:
        # drawing out blade movement, if not on a splash screen
        for i in range(len(app.mouseTrack) - 1):
            drawLine(app.mouseTrack[i][0], app.mouseTrack[i][1], app.mouseTrack[i + 1][0], app.mouseTrack[i + 1][1], fill='grey')
            drawLine(app.mouseTrack[i][0], app.mouseTrack[i][1], app.mouseTrack[i + 1][0], app.mouseTrack[i + 1][1], lineWidth = 5, opacity = 50, fill='grey')
    
    if app.isOriginalMode:
        drawLabel(f'Lives: {app.lives}', 700, 20, size=16, fill='white')
        
        # drawing out blue blade power up
        if app.blade.isBlueBlade and app.blade.freezeDuration > 0:
            drawRect(0, 0, app.width, app.height, fill='blue', opacity=30)
            app.blade.freezeDuration -= 1
            if app.blade.freezeDuration == 0:
                app.blade.isBlueBlade = False
                for fruit in app.fruits:
                    fruit.frozen = False 
        
        if not app.blade.isBlueBlade:
            # drawing out bombs
            for bomb in app.bombs:
                drawOval(bomb.x, bomb.y, bomb.size, bomb.size, fill='black', border='red')
                drawLabel("X", bomb.x, bomb.y, fill = 'red', size = bomb.size/1.5)
            
            # drawing out ice cubes
            for iceCube in app.iceCubes:
                if iceCube.sliced:
                    half1X = iceCube.x + iceCube.half1Offset
                    half2X = iceCube.x - iceCube.half2Offset
                    for angle, size in iceCube.sliceParams:
                        drawArc(half1X, iceCube.y, size, size, math.degrees(angle), 180, fill='lightblue', border='white')
                        drawArc(half2X, iceCube.y, size, size, math.degrees(angle) + 180, 180, fill='lightblue', border='white')
                elif iceCube.isActive:
                    drawOval(iceCube.x, iceCube.y, iceCube.size, iceCube.size, fill='lightblue', border = 'white')
             
            
            
    if app.isZenMode:
        drawLabel(f'Timer: {pythonRound(app.timer,1)}', 730, 20, size=20, fill='white')
        # drawing out clear Bombs
        for clearBomb in app.clearBombs:
                drawOval(clearBomb.x, clearBomb.y, clearBomb.size, clearBomb.size, fill='brown', border='red')
                drawLabel("X", clearBomb.x, clearBomb.y, fill = 'red', size = clearBomb.size/1.5)
        

def clearScreen(app):
    # gets rid of everything on the screen, wasting 2 seconds
    app.fruits = []
    app.bombs = []
    app.clearBombs = []
    app.clearEffectTimer = 2 

def processSlicing(app):
    # checks if any part of the fruit is intersecting the blade
    for fruit in app.fruits:
        if not fruit.sliced:
            for i in range(len(app.mouseTrack) - 1):
                if lineIntersectsCircle(app.mouseTrack[i], app.mouseTrack[i + 1], (fruit.x, fruit.y, fruit.size)):
                    app.sliceSound.play()
                    fruit.slice(app.mouseTrack[i], app.mouseTrack[i + 1])
                    app.blade.attack(fruit, app)
                    if not app.levelUp:
                        # if fruit is sliced add 10 to the score
                        app.scoreValue += 10
                        if app.scoreValue > app.highScore:
                            app.highScore = app.scoreValue
                            writeFile('highScore.txt', str(app.highScore)) 
        
                    break

    if app.isOriginalMode:
        for bomb in app.bombs:
            if not bomb.isActive:
                continue
            for i in range(len(app.mouseTrack) - 1):
                # if the blade intersects a bomb it is game over
                if lineIntersectsCircle(app.mouseTrack[i], app.mouseTrack[i + 1], (bomb.x, bomb.y, bomb.size)):
                    app.bombSound.play()
                    app.isGameOver = True
                    return
    
                    
        for iceCube in app.iceCubes:
            if not iceCube.sliced and iceCube.isActive:
                for i in range(len(app.mouseTrack) - 1):
                    # if the blade intersects an ice cube, enable frozen mode and the blue blde
                    if lineIntersectsCircle(app.mouseTrack[i], app.mouseTrack[i + 1], (iceCube.x, iceCube.y, iceCube.size)):
                        iceCube.slice(app.mouseTrack[i], app.mouseTrack[i + 1])
                        app.blade.attack(iceCube, app)
                        app.blade.isBlueBlade = True
                        app.blade.freezeDuration = 800
                        break 
    if app.isZenMode:
          for clearBomb in app.clearBombs:
            if not clearBomb.isActive:
                continue
            for i in range(len(app.mouseTrack) - 1):
                if lineIntersectsCircle(app.mouseTrack[i], app.mouseTrack[i + 1], (clearBomb.x, clearBomb.y, clearBomb.size)):
                    app.clearBombSound.play()
                    clearScreen(app)
                    return
        
                        
    
# CITATION: https://stackoverflow.com/questions/30844482/what-is-most-efficient-way-to-find-the-intersection-of-a-line-and-a-circle-in-py
# CITATION: https://codereview.stackexchange.com/questions/86421/line-segment-to-circle-collision-algorithm
# Code was inspired but not copied from these sources, mainly used for math
def lineIntersectsCircle(lineStart, lineEnd, circle):
    circleX, circleY, circleSize = circle
    radius = circleSize / 2
    circleCenter = (circleX + radius, circleY + radius)

    lineVec = (lineEnd[0] - lineStart[0], lineEnd[1] - lineStart[1])
    lineLenSquared = lineVec[0] ** 2 + lineVec[1] ** 2

    if lineLenSquared == 0:
        return False

    toCircleVec = (circleCenter[0] - lineStart[0], circleCenter[1] - lineStart[1])
    t = (toCircleVec[0] * lineVec[0] + toCircleVec[1] * lineVec[1]) / lineLenSquared
    t = max(0, min(1, t))
    closest = (lineStart[0] + t * lineVec[0], lineStart[1] + t * lineVec[1])
    distX = closest[0] - circleCenter[0]
    distY = closest[1] - circleCenter[1]
    distanceSquared = distX ** 2 + distY ** 2

    return distanceSquared <= radius ** 2

def redrawAll(app):
    if app.drawStartScreen:
        drawStartScreen(app)
    elif not app.drawStartScreen and not app.drawScoreScreen and not app.isGameOver and app.isPaused:
        drawImage(app.image1, 0, 0, width = app.width, height = app.height)
        drawLabel("Paused", app.width/2, app.height/2, size=50, fill = 'white', bold = True)
        return
    elif app.drawInstructionsScreen:
        drawInstructionsScreen(app)
    else:
        if app.timer <= 0:    
            drawScoreScreen(app)
        elif app.isGameOver or app.lives <= 0:
            drawGameOverScreen(app)
        else:
            drawGamePlayScreen(app)
    
    if app.levelUp and not app.isGameOver:
        drawLevelUpScreen(app)

            
def onMousePress(app, mouseX, mouseY):
    app.mouseTrack = [(mouseX, mouseY)]
    if app.drawStartScreen:
        if (0 <= mouseX <= 40) and (0 <= mouseY <= 40):
            app.buttonPressSound.play()
            app.drawInstructionsScreen = True
            app.drawStartScreen = False
        if (175 <= mouseX <= 325) and (325 <= mouseY <= 475):
            app.buttonPressSound.play()
            app.drawStartScreen = False
            app.isOriginalMode = True
        if (425 <= mouseX <= 575) and (325 <= mouseY <= 475):
            app.buttonPressSound.play()
            app.drawStartScreen = False
            app.isZenMode = True
       
    if app.drawInstructionsScreen:
        if (740 <= mouseX <= 780) and (20 <= mouseY <= 60):
            app.buttonPressSound.play()
            app.drawInstructionsScreen = False
            app.drawStartScreen = True
    
    if app.drawScoreScreen:
        if (300 <= mouseX <= 500) and (225 <= mouseY <= 375):
            app.buttonPressSound.play()
            reset(app)
    
    if app.isGameOver:
        reset(app)
    

def onMouseDrag(app, mouseX, mouseY):
    app.mouseTrack.append((mouseX, mouseY))
    processSlicing(app)

def onMouseRelease(app, mouseX, mouseY):
    app.mouseTrack = []

def onKeyPress(app, key):
    if key == 'space' and not app.drawStartScreen and not app.isGameOver and not app.drawScoreScreen:
         app.pauseSound.play()
         app.isPaused = not app.isPaused
    if key == 'r':
        reset(app)

def onStep(app):
    if app.isPaused:
        return 
    timeStep = 1 / app.stepsPerSecond
    # end of round conditions
    if app.lives <= 0:
        app.isGameOver = True
        
    if app.isZenMode and app.timer <= 0:
        app.drawScoreScreen = True

    # updating fruits and obstacles
    for fruit in app.fruits:
        fruit.update(timeStep, app)
    
    if app.isOriginalMode:
        for bomb in app.bombs:
            bomb.update(timeStep)
        for iceCube in app.iceCubes:
            iceCube.update(timeStep)
    
    if app.isZenMode:
        app.timer -= timeStep
        for clearBomb in app.clearBombs:
                clearBomb.update(timeStep)
        
    # clear affect when clear bomb is hit in zen mode
    if app.clearEffectTimer > 0:
        app.clearEffectTimer -= 1 / app.stepsPerSecond
        if app.clearEffectTimer <= 0:
            createFruits(app)  
   
    # leveling up calls createFruits, where more fruits are created the higher
    # your score gets
    if app.scoreValue % 200 == 0 and not app.fruitsUpdated and not app.levelUp:
        createFruits(app)
        app.fruitsUpdated = True
    
    elif app.scoreValue % 200 != 0:
        app.fruitsUpdated = False
    
    if app.scoreValue // 200 > app.lastLevelUpScore // 200:
        app.levelUp = True
        app.lastLevelUpScore = app.scoreValue

    # makes sure level up screen flashes
    if app.levelUp:
        app.levelUpDisplayTime -= 1 / app.stepsPerSecond
        if app.levelUpDisplayTime <= 0:
            app.levelUp = False
            app.levelUpDisplayTime = 0.5 

      

def main():
    runApp()

main()
