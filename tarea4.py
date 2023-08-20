import pyglet
import random
from OpenGL.GL import *
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import libs.grafica.transformations as tr
import libs.grafica.basic_shapes as bs
from libs.grafica.basic_shapes import Shape
import libs.grafica.scene_graph as sg
import libs.grafica.easy_shaders as es
import libs.grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath
from libs.obj_handler import read_OBJ
from pyglet import image,font

def getAssetPath(filename):
    """Convenience function to access assets files regardless from where you run the example script."""

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "assets")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"CARROT STICK GLOBAL OFENSIVE"):
        super().__init__(width, height, title,resizable = True)
        self.width = width
        self.height = height
        self.at = np.array([-12,5,0])
        self.viewPos = np.array([-15,5,0])
        self.camUp = np.array([0, 1, 0])
        self.x = 0
        self.y = 0
        self.z = 0
        self.totang = 0
        self.totaltime = 0.0
        self.texPipeline = es.SimpleTextureModelViewProjectionShaderProgram()
        self.lightPipeline = ls.SimpleGouraudShaderProgram()
        self.avanza = 0
        self.gira = 0
        self.angz = 0
        self.puntos = []
        self.tangentes = []
        self.altura = 0
        self.totangz = np.pi/2
        self.rtongo = np.array([0.0,0.0,0.0])
        self.vista = "Perspective"
        self.vista_bool = False
        self.totangY = 0
        self.totangZ = np.pi/2
        self.totaltime = 0
        self.balas = []
        self.score = 0
        self.hitbox = 0.4
        self.hitboxcarrot = 0.4
        self.gameover = False
        self.load = True
        self.replay = False
        self.maxscore = 0

    def naveupdate(self,squad,carrot):
        self.totang += self.gira
        #self.angz = np.pi/30*self.cursor[1]
        self.totangz -= self.angz
        self.x = np.sin(self.totangz)*np.cos(self.totang)
        self.y = round(np.cos(self.totangz),15)
        self.z = -np.sin(self.totangz)*np.sin(self.totang)
        self.rtongo = np.array([[self.x,self.y,self.z]])
        squad.transform = tr.matmul([squad.transform,tr.rotationY(self.gira),tr.rotationZ(self.angz)])
        borde = 9.8
        if abs(squad.transform[0][3])<borde and abs(squad.transform[2][3])<borde:
            squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
        else:
            if squad.transform[0][3] > borde:
                if self.rtongo[0][0]<0:
                    if self.avanza > 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
                    elif self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(-self.avanza,0,0)])
                elif self.rtongo[0][0]>0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
            elif squad.transform[0][3] < -borde:
                if self.rtongo[0][0]<0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
                elif self.rtongo[0][0]>0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(-self.avanza,0,0)])
                    elif self.avanza>0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
            if squad.transform[2][3] > borde:
                if self.rtongo[0][2]<0:
                    if self.avanza > 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
                    elif self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(-self.avanza,0,0)])
                elif self.rtongo[0][2]>0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
            elif squad.transform[2][3] < -borde:
                if self.rtongo[0][2]<0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
                elif self.rtongo[0][2]>0:
                    if self.avanza < 0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(-self.avanza,0,0)])
                    elif self.avanza>0:
                        squad.transform = tr.matmul([squad.transform,tr.translate(self.avanza,0,0)])
        if self.vista == "Ortho":
            self.at = 2*np.array([squad.transform[0][3],squad.transform[1][3],squad.transform[2][3]])
            self.viewPos = self.at + np.array([-0.1,5.0,0.0])
        elif self.vista == "Perspective":
            cam = sg.findPosition(squad,"camara")
            self.at = 2*np.array([squad.transform[0][3],squad.transform[1][3],squad.transform[2][3]])
            self.viewPos = 2*np.array([cam[0,0],cam[1,0],cam[2,0]])

    def balasUpdate(self,squad,carrot):
        if self.totaltime > 10:
            carrot.transform = tr.matmul([tr.uniformScale(1),tr.translate(random.randint(-9,9),-0.85,random.randint(-9,9))])
            self.totaltime = 0
        
        for bala in self.balas:
            bala[0].transform = tr.matmul([bala[0].transform,tr.translate(bala[1],bala[2],bala[3])])
        for bala in self.balas:
            balapos = sg.findPosition(bala[0],"bala")
            if abs(balapos[0][0])>20:
                bala[1] = -bala[1]
            if abs(balapos[2][0])>20:
                bala[3] = -bala[3]
            if abs(balapos[0][0]-2*carrot.transform[0][3])<self.hitboxcarrot and abs(balapos[2][0]-2*carrot.transform[2][3])<self.hitboxcarrot:
                carrot.transform = tr.matmul([tr.uniformScale(1),tr.translate(random.randint(-9,9),-0.85,random.randint(-9,9))])
                self.totaltime = 0
                self.score += 1
            if abs(balapos[0][0]-2*squad.transform[0][3])<self.hitbox and abs(balapos[2][0]-2*squad.transform[2][3])<self.hitbox:
                self.gameover = True
        score = pyglet.text.Label("PUNTAJE: "+str(self.score),font_name='Arial',
                          font_size=24,color=(255,130,0,255),
                          x=50, y=600)
        score.draw()
    
    def end(self):
        controller.vista = "Perspective"
        label = pyglet.text.Label("GAME OVER",font_name='Arial',
                          font_size=36,color=(255,130,0,255),
                          x=200, y=600)
        label.draw()
        score = pyglet.text.Label("PUNTAJE: "+str(self.score),font_name='Arial',
                          font_size=24,color=(255,130,0,255),
                          x=240, y=250)
        score.draw()
        if self.score > self.maxscore:
            self.maxscore = self.score
        maxscore = pyglet.text.Label("PUNTAJE MÁXIMO: "+str(self.maxscore),font_name='Arial',
                          font_size=24,color=(255,130,0,255),
                          x=220, y=200)
        maxscore.draw()
        replay = pyglet.text.Label("VOLVER A JUGAR: ENTER",font_name='Arial',
                          font_size=24,color=(255,130,0,255),
                          x=180, y=150)
        replay.draw()

    def loadscreen(self):
        self.at = np.array([-12,5,0])
        self.viewPos = np.array([-15,5,0])
        label = pyglet.text.Label("CSGO",font_name='Arial',
                          font_size=36,color=(255,130,0,255),
                          x=260, y=550)
        label.draw()
        label2 = pyglet.text.Label("Carrot Stick Global Offensive",font_name='Arial',
                          font_size=24,color=(255,130,0,255),
                          x=140, y=500)
        label2.draw()
        desc = pyglet.text.Label("CANSADO DE LAS ZANAHORIAS",font_name='Arial',
                                 font_size=20,color=(255,130,0,255),
                                 x=150,y=400)
        desc.draw()
        desc2 = pyglet.text.Label("ADICTO A LAS BALAS >:|",font_name='Arial',
                                 font_size=20,color=(255,130,0,255),
                                 x=190,y=350)
        desc2.draw()
        score = pyglet.text.Label("PRESIONA ENTER PARA COMENZAR ",font_name='Arial',
                          font_size=20,color=(255,130,0,255),
                          x=110, y=200)
        score.draw()    
                  
controller = Controller(700,700)

def setPlot(texPipeline, lightPipeline):
    global controller
    if controller.vista == "Perspective":
        projection = tr.perspective(60, 1, 0.1, 100)

    elif controller.vista == "Ortho":
        projection = tr.ortho(-7, 7, -7, 7, 0.001, 100)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ka"), 0.7, 0.7, 0.7)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "lightPosition"), controller.at[0], controller.at[1], controller.at[2])
    
    glUniform1ui(glGetUniformLocation(lightPipeline.shaderProgram, "shininess"), 10000)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "constantAttenuation"), 1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "linearAttenuation"), 0.00001)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "quadraticAttenuation"), 0.0001)

def setView(texPipeline, lightPipeline):
    view = tr.lookAt(
            controller.viewPos,
            controller.at,
            controller.camUp
        )

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "viewPosition"), controller.viewPos[0], controller.viewPos[1], controller.viewPos[2])
    
def crearPiso(ancho,largo):
    vert = np.array([[-0.5,0.5,0.5,-0.5],[-0.5,-0.5,0.5,0.5],[0.0,0.0,0.0,0.0],[1.0,1.0,1.0,1.0]], np.float32)
    rot = tr.rotationX(-np.pi/2)
    vert = rot.dot(vert)

    indices = [
         0, 1, 2,
         2, 3, 0]

    vertFinal = []
    indexFinal = []
    cont = 0

    for i in range(-largo,largo,1):
        for j in range(-ancho,ancho,1):
            tra = tr.translate(i,0.0,j)
            newVert = tra.dot(vert)

            v = newVert[:,0][:-1]
            vertFinal.extend([v[0], v[1], v[2], 0, 1])
            v = newVert[:,1][:-1]
            vertFinal.extend([v[0], v[1], v[2], 1, 1])
            v = newVert[:,2][:-1]
            vertFinal.extend([v[0], v[1], v[2], 1, 0])
            v = newVert[:,3][:-1]
            vertFinal.extend([v[0], v[1], v[2], 0, 0])
            
            ind = [elem + cont for elem in indices]
            indexFinal.extend(ind)
            cont = cont + 4

    return bs.Shape(vertFinal, indexFinal)

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

def Squad(pipeline):
    obj_color = (1.0, 0.0, 0.0)
    obj_color_bunny = (1.0,1.0,1.0)
    nave = createGPUShape(pipeline,read_OBJ(getAssetPath('minave.obj'), obj_color))
    bunny = createGPUShape(pipeline,read_OBJ(getAssetPath('bunny.obj'), obj_color_bunny))
    cube = createGPUShape(pipeline,bs.createColorCubeTarea2(0,1,1))
    carrotShape = createGPUShape(pipeline, read_OBJ(getAssetPath('carrot.obj'),(1,0.5,0)))

    carrot = sg.SceneGraphNode('carrot')
    carrot.transform = tr.matmul([tr.uniformScale(1),tr.translate(9,-0.85,0)])
    carrot.childs += [carrotShape]
    
    #squad
    lider = sg.SceneGraphNode("nave1")
    lider.transform = tr.matmul([tr.rotationY(np.pi)])
    lider.childs +=[bunny]

    camara = sg.SceneGraphNode("camara")
    camara.transform = tr.matmul([tr.translate(-16.0,8.0,0.0)])

    squad = sg.SceneGraphNode("squad")
    squad.transform = tr.matmul([tr.uniformScale(0.1)])
    squad.childs += [lider]
    squad.childs += [camara]

    cubo = sg.SceneGraphNode("cubo")
    cubo.transform = tr.matmul([tr.scale(10,5,10)])
    cubo.childs += [cube]

    #escena
    scene = sg.SceneGraphNode('starfox')
    scene.transform += tr.identity()
    scene.childs += [squad]
    scene.childs += [cubo]
    scene.childs += [carrot]
    #scene.childs += [sol]
    
    return scene 

def createpiso(pipeline):
    pisoShape = createGPUShape(pipeline, crearPiso(20,20))
    pisoShape.texture = es.textureSimpleSetup(
        getAssetPath("./grass.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR_MIPMAP_LINEAR, GL_NEAREST)
    glGenerateMipmap(GL_TEXTURE_2D)
    
    pisoNode = sg.SceneGraphNode('piso')
    pisoNode.transform = tr.translate(0,0.0,0.0)
    pisoNode.childs += [pisoShape]


    scene = sg.SceneGraphNode('system')
    scene.childs += [pisoNode]

    return scene

escuadron = Squad(controller.lightPipeline)
dibujo = createpiso(controller.texPipeline)
squad = sg.findNode(escuadron, "squad")
carrot = sg.findNode(escuadron,"carrot")
camara = sg.findNode(escuadron, "camara")
axisPipeline = controller.texPipeline
balaShape = createGPUShape(controller.lightPipeline, bs.createColorSphereTarea2(102/256, 63/256, 12/256))
        
velNave = 1.5
angulo = np.pi/80

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.avanza += velNave
        
    if symbol == pyglet.window.key.S:
        controller.avanza -= velNave
    
    if symbol == pyglet.window.key.A:
        controller.gira += angulo
        
    if symbol == pyglet.window.key.D:
        controller.gira -= angulo     

    if symbol == pyglet.window.key.SPACE:
        if controller.load != True:
            bala = sg.SceneGraphNode("bala")
            pos = 2*np.array([squad.transform[0][3],squad.transform[1][3],squad.transform[2][3]])
            bala.transform = tr.matmul([tr.translate(pos[0]+1.5*controller.hitbox*controller.rtongo[0][0],pos[1]+0.35,pos[2]+1.5*controller.hitbox*controller.rtongo[0][2]),tr.uniformScale(0.1)]) #rotamos la bala 
            bala.childs += [balaShape]
            #controller.balas = []
            controller.balas.append([bala,3*controller.rtongo[0][0],0,3*controller.rtongo[0][2]])

    if symbol == pyglet.window.key.C:
        if controller.load == False and controller.gameover == False:
            if controller.vista_bool == False:
                controller.vista = "Ortho"
                controller.vista_bool = not(controller.vista_bool)
            elif controller.vista_bool == True:
                controller.vista = "Perspective"
                controller.vista_bool = not(controller.vista_bool)
        
    if symbol == pyglet.window.key.ENTER:
        controller.load = False
        if controller.gameover == True:
            controller.at = np.array([-12,5,0])
            controller.viewPos = np.array([-15,5,0])
            controller.camUp = np.array([0, 1, 0])
            controller.x = 0
            controller.y = 0
            controller.z = 0
            controller.totang = 0
            controller.totaltime = 0.0
            controller.avanza = 0
            controller.gira = 0
            controller.angz = 0
            controller.puntos = []
            controller.tangentes = []
            controller.altura = 0
            controller.totangz = np.pi/2
            controller.rtongo = np.array([0.0,0.0,0.0])
            controller.vista = "Perspective"
            controller.vista_bool = False
            controller.totangY = 0
            controller.totangZ = np.pi/2
            controller.totaltime = 0
            controller.balas = []
            controller.score = 0
            controller.gameover = False
            controller.load = True
            controller.replay = False
            carrot.transform = tr.matmul([tr.uniformScale(1),tr.translate(9,-0.85,0)])
            squad.transform = tr.matmul([tr.uniformScale(0.1)])

@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.W:
        controller.avanza -= velNave
        
    if symbol == pyglet.window.key.S:
        controller.avanza += velNave
    
    if symbol == pyglet.window.key.A:
        controller.gira -= angulo
        
        
    if symbol == pyglet.window.key.D:
        controller.gira += angulo 

    if symbol == pyglet.window.key.UP:
        controller.altura = 0

    if symbol == pyglet.window.key.DOWN:
        controller.altura = 0

    if symbol == pyglet.window.key.V:
        controller.ruta = False

@controller.event
def on_draw():
    controller.clear()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    setPlot(controller.texPipeline,controller.lightPipeline)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
    #Filling the shapes
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    setView(controller.texPipeline, controller.lightPipeline)

    if controller.gameover == False and controller.load == False:
        glUseProgram(controller.texPipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, controller.texPipeline, "model")

        glUseProgram(controller.lightPipeline.shaderProgram)
        sg.drawSceneGraphNode(escuadron, controller.lightPipeline, "model")
        for bala in controller.balas:
            glUseProgram(controller.lightPipeline.shaderProgram)
            sg.drawSceneGraphNode(bala[0], controller.lightPipeline, "model")
        controller.naveupdate(squad,carrot)
        controller.balasUpdate(squad,carrot)

    elif controller.load == True:
        glUseProgram(controller.texPipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, controller.texPipeline, "model")

        glUseProgram(controller.lightPipeline.shaderProgram)
        sg.drawSceneGraphNode(escuadron, controller.lightPipeline, "model")
        controller.loadscreen()
    elif controller.gameover == True:
        glUseProgram(controller.texPipeline.shaderProgram)
        sg.drawSceneGraphNode(dibujo, controller.texPipeline, "model")

        glUseProgram(controller.lightPipeline.shaderProgram)
        sg.drawSceneGraphNode(escuadron, controller.lightPipeline, "model")
        controller.end()

def update(dt,controller):
    controller.totaltime += dt

if __name__ == '__main__':
    print('ACHUNTALE A LA ZANAHORIA!!! ESQUIVA LAS BALAS!')
    pyglet.clock.schedule_interval(update,1/60, controller)
    pyglet.app.run()