# -*- coding: utf-8 -*-
import tkinter as tk
import numpy as np
import tkinter.colorchooser
import math as m
import pandas as pd
from PIL import Image, ImageTk 

ECHELLE_DIST = 150*10**9/300  # 1px <-> ECHELLE_DIST m
ECHELLE_TPS = (3.154e+7)/100  # 1 frame <-> ECHELLE_TPS s


class SpacialObject:
    def __init__(self, radius, mass, x, y, color, mvt):
        self.radius = radius
        self.mass = mass
        self.x = x
        self.y = y
        self.speed = 0
        self.deplacementVector = np.array(mvt, dtype='float64')
        self.color = color
        self.appliedForces = []
        self.lastPos = []
        self.objectFrame = 0

    def move(self):
        deltaV = self.getDeltaV()
        # OPTIMIZE:
        try:
            if not self.objectFrame.isSpeedPaused:
                self.objectFrame.speedVar.set(round(self.getSpeed(), 3))
        except AttributeError:
            pass
        self.deplacementVector = self.deplacementVector + deltaV
        self.x += self.deplacementVector[0]*ECHELLE_TPS/ECHELLE_DIST
        self.y += self.deplacementVector[1]*ECHELLE_TPS/ECHELLE_DIST
        self.lastPos.append((self.x,self.y))
        if len(self.lastPos) >= 200:
            self.lastPos = self.lastPos[-200:]
        self.appliedForces = []

    def applyForces(self, spacialObjects):
        for name, so in spacialObjects.items():
            if so != self:
                u = self.getUnitVector(so.x,so.y,self.x,self.y)
                u *= self.getGravity(self.mass, so.mass,self.norme((self.x-so.x,self.y-so.y))*ECHELLE_DIST)
                so.applied(u)

    def drawVectors(self,c):
        for v in self.appliedForces:
            c.create_line(self.x, self.y, self.x+v[0]/50, self.y+v[1]/50, fill='white')

        s = np.sum(self.appliedForces, axis=0)
        c.create_line(self.x, self.y, self.x+s[0], self.y+s[1], fill='yellow')
        c.create_line(self.x, self.y, self.x+self.getCarthesian()[0], self.y+self.getCarthesian()[1], fill='green')

    def drawLastPos(self,c):
        for i in range(1,len(self.lastPos)):
            c.create_line(self.lastPos[i][0], self.lastPos[i][1], self.lastPos[i-1][0], self.lastPos[i-1][1], fill=self.color)

    def getCarthesian(self):
        return self.deplacementVector

    def getPolar(self):
        return (self.norme(self.getCarthesian()),
                m.arctan(self.getCarthesian()[1]/self.getCarthesian()[0]))

    def norme(self,v):
        return m.sqrt(v[0]**2+v[1]**2)

    def getUnitVector(self, x1,y1,x2,y2):
        a = (x2-x1,y2-y1)
        aBar = self.norme(a)
        u = np.array((a[0]/aBar,a[1]/aBar))
        return u

    def getGravity(self,m1,m2,d):
        return 6.674*10**(-11)*((m1*m2)/d**2)

    def applied(self, f):
        self.appliedForces.append(f)

    def getDeltaV(self):
        sumForces = np.sum(self.appliedForces, axis=0)
        return sumForces*ECHELLE_TPS/self.mass

    def getSpeed(self):
        return self.norme(self.deplacementVector)

    def setSpeed(self,s):
        self.deplacementVector = self.getUnitVector(0,0,self.deplacementVector[0],self.deplacementVector[1])*s
        return self.deplacementVector


class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, background="white", width=300)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="white")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class mainInterface(tk.Frame):
    def __init__(self, fenetre, **kwargs):
        tk.Frame.__init__(self, fenetre, **kwargs)
        self.pack(fill=tk.BOTH, expand=True)

        self.spacialObjects = {
                #"Earth": SpacialObject(5, 3e16, 300, 200, "blue",[1,0])
                }
        
        self.shownSection = section(self)
        self.shownAside = aside(self,highlightthickness=0)
        
    def deleteSo(self,name):
        del self.spacialObjects[name]
        self.shownAside.update()


class section(tk.Canvas):
    def __init__(self, root, **kwargs):
        self.root = root
        self.isPaused = False
        tk.Canvas.__init__(self, self.root, background="black", **kwargs)
        self.pack(fill=tk.BOTH, side="left", expand=True)
        self.bind("<Button-1>", self.leftClickHandler)
        self.dragging = None
        self.bind("<ButtonPress-1>", self.dragStart)
        self.bind("<ButtonRelease-1>", self.dragStop)
        self.bind("<B1-Motion>", self.drag)
        self.i = 0
        iPlayPause = Image.open(r"img\playpause.png") 
        self.pPlayPause = ImageTk.PhotoImage(iPlayPause,size=2) 
        self.drawCanvas()

    def drawCanvas(self):
        self.delete("all")
        self.create_image(self.winfo_width()-10,10, anchor = tk.NE, image=self.pPlayPause)
        # On aplique chaque force de chaque objet
        
        
        for name, so in self.root.spacialObjects.items():
            so.applyForces(self.root.spacialObjects)

        # On fait déplace puis dessine chaque objet
        for name, so in self.root.spacialObjects.items():
            #so.drawVectors(self)
            so.move()            
            self.create_text(so.x, so.y+so.radius/ECHELLE_DIST+5, text=name, fill="white")
            self.showSpacialObject(so)
            so.drawLastPos(self)
        self.i += 1
        if not self.isPaused:
            self.after(41, self.drawCanvas)

    def showSpacialObject(self, so):
        self.drawCircle(so.radius/ECHELLE_DIST, so.x, so.y, so.color)
        pass

    def drawCircle(self, radius, centerX, centerY, color):
        self.create_oval(centerX-radius, centerY-radius, centerX+radius,
                         centerY+radius, fill=color)

    def leftClickHandler(self,e):
        if e.x >= self.winfo_width()-self.pPlayPause.width()-10 and e.y <= self.pPlayPause.height()-10: #Pause button
            if not self.isPaused:
                self.isPaused = True
            else:
                self.isPaused = False
                self.drawCanvas()
    def dragStart(self,e):
        for name, so in self.root.spacialObjects.items(): #Drag and Drop
            if e.x <= so.x+so.radius/ECHELLE_DIST+10 and e.x >= so.x-so.radius/ECHELLE_DIST-10 and e.y <= so.y-so.radius/ECHELLE_DIST+10 and e.y >= so.y-so.radius/ECHELLE_DIST-10:
                self.dragging = so
                return
    def dragStop(self,e):
        self.dragging = None
        
    def drag(self,e):
        if self.dragging is not None:
            self.dragging.x = e.x
            self.dragging.y = e.y
        

class aside(ScrollableFrame):
    def __init__(self, root, **kwargs):
        self.root = root

        ScrollableFrame.__init__(self, self.root, **kwargs)
        self.pack(side="right", fill=tk.Y)

        titre = tk.Label(self.scrollable_frame, text="Simulateur d'orbite",
                         background="white", font=("Arial", 20))
        titre.pack(side=tk.TOP)

        buttonAddObject = tk.Button(self.scrollable_frame,
                                    text="Ajouter un objet",
                                    command=self.showAddObject)
        buttonAddObject.pack()

        objectFrames = []
        i = 0
        for name, so in self.root.spacialObjects.items():
            objectFrames.append(objectFrame(self.scrollable_frame, name, so, self.root))
            i += 1

    def showAddObject(self):
        root = tk.Tk()
        addObjectWindow(root,self.root)
        root.mainloop()

    def update(self):
        self.destroy()
        self.__init__(self.root)



class objectFrame(tk.Frame):
    def __init__(self, root, name, so, mI):
        self.name = name
        self.so = so
        self.root = root
        self.mI = mI
        self.isSpeedPaused = False
        so.objectFrame = self

        super().__init__(root, background="white", relief=tk.GROOVE, bd=1)
        self.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self, text=name, background="white",
                 width=40).grid(padx=5, pady=5, row=0, column=0, columnspan=10)
        
        buttonDel = tk.Button(self,
                                    text="X",
                                    command=self.delSo)
        buttonDel.grid(row=0,
                          column=8)

        # Mass
        self.massVarNum = tk.DoubleVar(value=self.getScienti(so.mass)[0][:5])
        self.massVarPow = tk.IntVar(value=self.getScienti(so.mass)[1])

        tk.Label(self, text="Massse :",
                 background="white").grid(row=1, column=0)
        tk.Entry(self, textvariable=self.massVarNum, width=6,
                 bg="SystemButtonFace").grid(row=1, column=1)
        tk.Label(self,text="E", background="white",bd=-2).grid(row=1, column=2)
        tk.Entry(self, textvariable=self.massVarPow, width=4,
                 bg="SystemButtonFace").grid(row=1, column=3)

        tk.Label(self, text="kg", background="white").grid(row=1, column=4)

        # Speed
        tk.Label(self, text="Vitesse :",
                 background="white").grid(row=2, column=0)
        self.speedVar = tk.DoubleVar(value=so.speed)
        tk.Entry(self, textvariable=self.speedVar, width=10,
                 bg="SystemButtonFace").grid(row=2, column=1,columnspan=3)
        tk.Label(self, text="m/s", background="white").grid(row=2, column=4)
        tk.Button(self, text="Pause", command=self.toogleSpeed).grid(row=2,
                                                                     column=5)
        #Radius
        tk.Label(self, text="Rayon :",
                 background="white").grid(row=3, column=0)
        self.radiusVar = tk.DoubleVar(value=so.radius/1000)
        tk.Entry(self, textvariable=self.radiusVar, width=10,
                 bg="SystemButtonFace").grid(row=3, column=1,columnspan=3)
        tk.Label(self, text="km", background="white").grid(row=3, column=4)

        # Color
        self.color = so.color
        tk.Label(self, text="Couleur :", background="white").grid(row=4,
                                                                 column=0)
        self.colorB = tk.Button(self, text="   ", command=self.changeColor,
                                width=2, bg=self.color, relief="flat")
        self.colorB.grid(row=4, column=1)

        buttonUpdate = tk.Button(self,
                                    text="Ok",
                                    command=self.updateSo)
        buttonUpdate.grid(row=5,
                          column=8)
    def changeColor(self):
        newColor = tk.colorchooser.askcolor()[1]
        if newColor is not None:
            self.color = newColor
            self.colorB.configure(bg=newColor)

    def toogleSpeed(self):
        if self.isSpeedPaused:
            self.isSpeedPaused = False
        else:
            self.isSpeedPaused = True

    def updateSo(self):
        self.so.mass = self.getDec((self.massVarNum.get(),self.massVarPow.get()))
        self.so.radius = self.radiusVar.get()*1000
        if self.isSpeedPaused:
            self.so.setSpeed(self.speedVar.get())
            self.toogleSpeed()
        self.so.color = self.color

    def getScienti(self,n):
        return ("%e"%n).split("e")

    def getDec(self,n):
        return n[0]*10**n[1]
    
    def delSo(self):
        self.mI.deleteSo(self.name)


class addObjectWindow(tk.Frame):
    def __init__(self, fenetre, mainInterface , **kwargs):
        #test
        self.fenetre = fenetre
        self.mainInterface = mainInterface
        tk.Frame.__init__(self, fenetre, **kwargs)
        self.pack(fill=tk.BOTH)


        #Ajout d'un objet pré-existant
        self.entries = {}
        self.KnownEntries = {}
        object_registered = tk.LabelFrame(self, text="Nouvel objet à partir d'un objet pré-existant", padx=20, pady=20)
        object_registered.pack(side=tk.TOP, padx=20, pady=10)

        #Commentaire pour l'utilisateur
        Presentation1= tk.Label(object_registered, text="Ici, le nouvel objet que vous intégrerez aura les mêmes caractéristiques qu'un des objets ci-dessous, dont les caractéristiques sont déjà connues.")
        Presentation1.grid(row=0,column=0,columnspan=6)


        #Choix des profils pré-existants
        FrameChoice = tk.LabelFrame(object_registered,text="Veuillez choisir le profil de la planète pré-existante")
        FrameChoice.grid(row=1,column=0, rowspan = 3, padx=20, pady=20)
        
        
        with open('MrMalletlebest.csv', newline='') as csvfile:
            self.KnownObject = pd.read_csv(csvfile)
        
        
        self.knownObjectList = tk.Listbox(FrameChoice)
        self.knownObjectList.pack()
        
        for planet in self.KnownObject.loc[:,"Name"]:
           self.knownObjectList.insert(tk.END, planet)



        FrameVector = tk.LabelFrame(object_registered,text="Mouvement (Vecteur sous la forme x;y en m/s)")
        FrameVector.grid(row=1,column=2,columnspan=2, padx=20, pady=20)
        self.mvt = tk.StringVar()
        self.KnownEntries["vector"] = tk.Entry(FrameVector, textvariable=self.mvt, width=30)
        self.KnownEntries["vector"].pack(padx=10, pady=10)

        FrameX = tk.LabelFrame(object_registered,text="coordonée X")
        FrameX.grid(row=2,column=2, padx=20, pady=20)
        self.x = tk.IntVar(value="10")
        self.KnownEntries["x"] = tk.Entry(FrameX, textvariable=self.x, width=5)
        self.KnownEntries["x"].pack(padx=10, pady=10)

        FrameY = tk.LabelFrame(object_registered,text="coordonée Y")
        FrameY.grid(row=2,column=3, padx=20, pady=20)
        self.y = tk.IntVar()
        self.KnownEntries["y"] = tk.Entry(FrameY, textvariable=self.y, width=5)
        self.KnownEntries["y"].pack(padx=10, pady=10)
        
        
        Button_save=tk.Button(object_registered, text="OK", command=self.saveKnownObject)
        Button_save.grid(row=4,column=1, padx=20, pady=20)


        #Ajout d'un objet aux caractéristiques à choisir
        new_object = tk.LabelFrame(self, text='Nouvel objet avec de nouvelles caractéristiques', padx=20, pady=20)
        new_object.pack(side=tk.TOP, padx=20, pady=20)

        #Commentaire pour l'utilisateur
        Presentation2= tk.Label(new_object, text="Tandis qu'ici, le nouvel objet que vous intégrerez aura les caractéristiques que vous saisissez dans les espaces ci-dessous, de façon à personnaliser l'expérience.")
        Presentation2.grid(row=0,column=0,columnspan=6)

        #Choix des caractéristiques
        FrameName = tk.LabelFrame(new_object,text="Nom de l'objet")
        FrameName.grid(row=1,column=0, columnspan = 2, padx=20, pady=20)
        nameVar = tk.StringVar(value="test")
        self.entries["name"] = tk.Entry(FrameName, textvariable=nameVar, width=20)
        self.entries["name"].pack(padx=10, pady=10)

        FrameRadius = tk.LabelFrame(new_object,text="Rayon (km)")
        FrameRadius.grid(row=2,column=0)
        self.radius = tk.DoubleVar()
        self.entries["radius"] = tk.Entry(FrameRadius, textvariable=self.radius, width=8)
        self.entries["radius"].pack(padx=10, pady=10)

        FrameColor = tk.LabelFrame(new_object,text="Couleur")
        FrameColor.grid(row=2,column=1, padx=0, pady=0)
        self.color = "blue"
        self.entries["color"] = "blue"
        self.colorB = tk.Button(FrameColor, text="   ", command=self.changeColor,
                                width=2, bg=self.color, relief="flat")
        self.colorB.pack(padx=10, pady=5)

        FrameMass = tk.LabelFrame(new_object,text="Masse (Un nombre en kg)")
        FrameMass.grid(row=1,column=2, padx=20, pady=20)
        massNum = tk.DoubleVar()
        massPow = tk.IntVar()
        self.entries["massNum"] = tk.Entry(FrameMass, textvariable=massNum, width=6)
        self.entries["massNum"].pack(side = tk.LEFT, padx=5, pady=10)
        tk.Label(FrameMass,text="E",bd=-2).pack(side = tk.LEFT, padx=5, pady=10)
        self.entries["massPow"] = tk.Entry(FrameMass, textvariable=massPow, width=4)
        self.entries["massPow"].pack(side = tk.LEFT, padx=5, pady=10)

        FrameVector = tk.LabelFrame(new_object,text="Mouvement (Vecteur sous la forme x;y en m.s)")
        FrameVector.grid(row=2,column=2, padx=20, pady=20)
        self.mvt = tk.StringVar()
        self.entries["vector"] = tk.Entry(FrameVector, textvariable=self.mvt, width=30)
        self.entries["vector"].pack(padx=10, pady=10)

        FrameX = tk.LabelFrame(new_object,text="coordonée X")
        FrameX.grid(row=1,column=3, padx=20, pady=20)
        self.x = tk.IntVar(value="10")
        self.entries["x"] = tk.Entry(FrameX, textvariable=self.x, width=5)
        self.entries["x"].pack(padx=10, pady=10)


        FrameY = tk.LabelFrame(new_object,text="coordonée Y")
        FrameY.grid(row=2,column=3, padx=20, pady=20)
        self.y = tk.IntVar()
        self.entries["y"] = tk.Entry(FrameY, textvariable=self.y, width=5)
        self.entries["y"].pack(padx=10, pady=10)



        Button_save=tk.Button(new_object, text="OK", command=self.saveNewObject)
        Button_save.grid(row=3,column=1,columnspan=2, padx=20, pady=20)

    def changeColor(self):
        newColor = tk.colorchooser.askcolor()[1]
        if newColor is not None:
            self.color = newColor
            self.colorB.configure(bg=newColor)
            self.entries["color"] = newColor

    def saveNewObject(self):
        self.mainInterface.spacialObjects[self.entries["name"].get()] = SpacialObject(int(self.entries["radius"].get())*1000,
                                                                                      float(self.entries["massNum"].get())*10**int(self.entries["massPow"].get()), int(self.entries["x"].get()),
                                                                                     int(self.entries["y"].get()), self.entries["color"],np.array(self.entries["vector"].get().split(";")).astype("int32"))
        self.mainInterface.shownAside.update()
        self.fenetre.destroy()

    def saveKnownObject(self):
        selected = self.KnownObject[self.KnownObject.Name == self.knownObjectList.get(tk.ACTIVE)]
        
        self.mainInterface.spacialObjects[selected.iloc[0]["Name"]] = SpacialObject(float(selected.iloc[0]["Radius"])*1000,  float(selected.iloc[0]["MassNum"])*10**int(selected.iloc[0]["MassPow"]), int(self.KnownEntries["x"].get()), int(self.KnownEntries["y"].get()), selected.iloc[0]["Color"],np.array(self.KnownEntries["vector"].get().split(";")).astype("int32"))
        self.mainInterface.shownAside.update()
        self.fenetre.destroy()


root = tk.Tk()
root.resizable(height=None, width=None)
root.title('Orbit Simulator')
root.geometry('1000x800')

interface = mainInterface(root)
interface.mainloop()
