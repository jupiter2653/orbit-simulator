# -*- coding: utf-8 -*-
import tkinter as tk
import numpy as np
import tkinter.colorchooser
import math as m

ECHELLE_DIST = 1000  # 1px <-> ECHELLE_DIST m
ECHELLE_TPS = 600  # 1 frame <-> ECHELLE_TPS s


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
        self.x += self.deplacementVector[0]
        self.y += self.deplacementVector[1]
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
        return self.norme(self.deplacementVector)*ECHELLE_DIST/ECHELLE_TPS

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
                "Earth": SpacialObject(5, 3e16, 500, 300, "yellow",[-2,0]),
                "Sun": SpacialObject(5, 3e16, 300, 350, "yellow",[-2,0]),
                "Mars": SpacialObject(5, 0.0001, 300, 275, "red",[-1,-1])
                #"Jsp": SpacialObject(5, 3*10**15, 200, 400, "white",[1,0]),
                #"Jsp2": SpacialObject(5, 3*10**15, 500, 400, "white",[1,0]),
            }
        self.shownSection = section(self)
        self.shownAside = aside(self)


class section(tk.Canvas):
    def __init__(self, root, **kwargs):
        self.root = root
        self.isPaused = False
        tk.Canvas.__init__(self, self.root, background="black", **kwargs)
        self.pack(fill=tk.BOTH, side="left", expand=True)
        self.bind("<Button-1>", self.leftClickHandler)
        self.i = 0
        self.drawCanvas()

    def drawCanvas(self):
        self.delete("all")
        self.create_rectangle(self.winfo_width()-40,0,self.winfo_width(),40,fill="white")
        # On aplique chaque force de chaque objet
        for name, so in self.root.spacialObjects.items():
            so.applyForces(self.root.spacialObjects)

        # On fait déplace puis dessine chaque objet
        for name, so in self.root.spacialObjects.items():
            #so.drawVectors(self)
            so.move()
            self.create_text(so.x, so.y+so.radius+5, text=name, fill="white")
            self.showSpacialObject(so)
            so.drawLastPos(self)
        self.i += 1
        if not self.isPaused:
            self.after(41, self.drawCanvas)

    def showSpacialObject(self, so):
        self.drawCircle(so.radius, so.x, so.y, so.color)
        pass

    def drawCircle(self, radius, centerX, centerY, color):
        self.create_oval(centerX-radius, centerY-radius, centerX+radius,
                         centerY+radius, fill=color)

    def leftClickHandler(self,e):
        if e.x >= self.winfo_width()-40 and e.y <= 40: #Pause button
            if not self.isPaused:
                self.isPaused = True
            else:
                self.isPaused = False
                self.drawCanvas()


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
            objectFrames.append(objectFrame(self.scrollable_frame, name, so))
            i += 1

    def showAddObject(self):
        root = tk.Tk()
        addObjectWindow(root,self.root)
        root.mainloop()


class objectFrame(tk.Frame):
    def __init__(self, root, name, so):
        self.name = name
        self.so = so
        self.root = root
        self.isSpeedPaused = False
        so.objectFrame = self

        super().__init__(root, background="white", relief=tk.GROOVE, bd=1)
        self.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self, text=name, background="white",
                 width=40).grid(padx=5, pady=5, row=0, column=0, columnspan=6)

        # Mass
        tk.Label(self, text="Massse :",
                 background="white").grid(row=1, column=0)
        self.massVar = tk.DoubleVar(value=so.mass)
        tk.Entry(self, textvariable=self.massVar, width=10,
                 bg="SystemButtonFace").grid(row=1, column=1)
        tk.Label(self, text="kg", background="white").grid(row=1, column=2)

        # Speed
        tk.Label(self, text="Vitesse :",
                 background="white").grid(row=2, column=0)
        self.speedVar = tk.DoubleVar(value=so.speed)
        tk.Entry(self, textvariable=self.speedVar, width=10,
                 bg="SystemButtonFace").grid(row=2, column=1)
        tk.Label(self, text="m/s", background="white").grid(row=2, column=2)
        tk.Button(self, text="Pause", command=self.toogleSpeed).grid(row=2,
                                                                     column=3)

        # Color
        self.color = so.color
        tk.Label(self, text="Couleur :", background="white").grid(row=3,
                                                                 column=0)
        self.colorB = tk.Button(self, text="   ", command=self.changeColor,
                                width=2, bg=self.color, relief="flat")
        self.colorB.grid(row=3, column=1)

        buttonUpdate = tk.Button(self,
                                    text="Ok",
                                    command=self.updateSo)
        buttonUpdate.grid(row=4,
                          column=4)
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
        self.so.mass = self.massVar.get()
        if self.isSpeedPaused:
            self.so.setSpeed(self.speedVar.get())
            self.toogleSpeed()
        self.so.color = self.color


class addObjectWindow(tk.Frame):
    def __init__(self, fenetre, mainInterface , **kwargs):
        #test
        self.fenetre = fenetre
        self.mainInterface = mainInterface
        tk.Frame.__init__(self, fenetre, **kwargs)
        self.pack(fill=tk.BOTH)


        #Ajout d'un objet pré-existant
        object_registered = tk.LabelFrame(self, text="Nouvel objet à partir d'un objet pré-existant", padx=20, pady=20)
        object_registered.pack(side=tk.TOP, padx=20, pady=10)

        #Commentaire pour l'utilisateur
        Presentation1= tk.Label(object_registered, text="Ici, le nouvel objet que vous intégrerez aura les mêmes caractéristiques qu'un des objets ci-dessous, dont les caractéristiques sont déjà connues.")
        Presentation1.pack()

        #Choix des profils pré-existants
        self.valueobject = tk.IntVar()
        ButtonEarth = tk.Radiobutton(object_registered, text="Terre", variable=self.valueobject, value=1)
        ButtonMoon = tk.Radiobutton(object_registered, text="Lune", variable=self.valueobject, value=2)
        ButtonMars = tk.Radiobutton(object_registered, text="Mars", variable=self.valueobject, value=3)
        ButtonEarth.pack(side=tk.LEFT, padx=20, pady=20)
        ButtonMoon.pack(side=tk.LEFT, padx=20, pady=20)
        ButtonMars.pack(side=tk.LEFT, padx=20, pady=20)

        Button_save=tk.Button(object_registered, text="OK", command=fenetre.destroy)
        Button_save.pack(side=tk.BOTTOM)

        #Ajout d'un objet aux caractéristiques à choisir
        new_object = tk.LabelFrame(self, text='Nouvel objet avec de nouvelles caractéristiques', padx=20, pady=20)
        new_object.pack(side=tk.TOP, padx=20, pady=20)

        #Commentaire pour l'utilisateur
        Presentation2= tk.Label(new_object, text="Tandis qu'ici, le nouvel objet que vous intégrerez aura les caractéristiques que vous saisissez dans les espaces ci-dessous, de façon à personnaliser l'expérience.")
        Presentation2.pack()

        #Choix des caractéristiques
        self.values = {}

        FrameName = tk.LabelFrame(new_object,text="Nom de l'objet")
        FrameName.pack(side=tk.LEFT, padx=20, pady=20)
        self.name = tk.StringVar()
        entree = tk.Entry(FrameName, textvariable=self.name, width=30)
        entree.pack(padx=10, pady=10)

        FrameRadius = tk.LabelFrame(new_object,text="Rayon (Un nombre en pixel)")
        FrameRadius.pack(side=tk.LEFT, padx=20, pady=20)
        self.radius = tk.DoubleVar()
        entree = tk.Entry(FrameRadius, textvariable=self.radius, width=30)
        entree.pack(padx=10, pady=10)

        FrameMass = tk.LabelFrame(new_object,text="Masse (Un nombre en kg)")
        FrameMass.pack(side=tk.LEFT, padx=20, pady=20)
        self.mass = tk.DoubleVar()
        entree = tk.Entry(FrameMass, textvariable=self.mass, width=30)
        entree.pack(padx=10, pady=10)

        FrameX = tk.LabelFrame(new_object,text="coordonée x")
        FrameX.pack(side=tk.LEFT, padx=20, pady=20)
        self.x = tk.IntVar()
        entree = tk.Entry(FrameX, textvariable=self.x, width=30)
        entree.pack(padx=10, pady=10)

        FrameY = tk.LabelFrame(new_object,text="coordonée y")
        FrameY.pack(side=tk.BOTTOM, padx=20, pady=20)
        self.y = tk.IntVar()
        entree = tk.Entry(FrameY, textvariable=self.y, width=30)
        entree.pack(padx=10, pady=10)

        FrameVector = tk.LabelFrame(new_object,text="Mouvement (Vecteur sous la forme [x;y])")
        FrameVector.pack(side=tk.BOTTOM, padx=20, pady=20)
        self.mvt = tk.IntVar()
        entree = tk.Entry(FrameVector, textvariable=self.mvt, width=30)
        entree.pack(padx=10, pady=10)

        FrameColor = tk.LabelFrame(new_object,text="Couleur")
        FrameColor.pack(side=tk.BOTTOM, padx=20, pady=20)
        self.color = "blue"
        self.values["color"] = "blue"
        self.colorB = tk.Button(FrameColor, text="   ", command=self.changeColor,
                                width=2, bg=self.color, relief="flat")
        self.colorB.pack()

        Button_save=tk.Button(new_object, text="OK", command=self.saveNewObject)
        Button_save.pack(side=tk.BOTTOM)

    def changeColor(self):
        newColor = tk.colorchooser.askcolor()[1]
        if newColor is not None:
            self.color = newColor
            self.colorB.configure(bg=newColor)
            self.values["color"] = newColor




    def saveNewObject(self):
        print(self.name.get(),self.name)
        print(self.radius, self.mass, self.x, self.y, self.color,[2,0])
        print(self.radius.get(), self.mass.get(), self.x.get(), self.y.get(), self.color,[2,0])
        self.mainInterface.spacialObjects[self.name.get()] = SpacialObject(self.radius.get(), self.mass.get(), self.x.get(), self.y.get(), self.values["color"],[2,0])  #radius, mass, x, y, color, mvt
        self.fenetre.destroy()

root = tk.Tk()
root.resizable(height=None, width=None)
root.title('Orbit Simulator')
root.geometry('1000x800')

interface = mainInterface(root)
interface.mainloop()
