# -*- coding: utf-8 -*-
import tkinter as tk
import numpy as np
import tkinter.colorchooser
import math as m

class SpacialObject:
    def __init__(self, radius, mass, x, y, color,mvt):
        self.radius = radius
        self.mass = mass
        self.x = x
        self.y = y
        self.speed = 0
        self.deplacementVector = np.array(mvt, dtype='float64')
        self.color = color
        self.appliedForces = []

    def move(self):
        deltaV = self.getDeltaV()
        self.deplacementVector = self.deplacementVector + deltaV
        self.x += self.getCarthesian()[0]
        self.y += self.getCarthesian()[1]

    def applyForces(self,spacialObjects):
        for name,so in spacialObjects.items():
            if so != self:
                u = self.getUnitVector(so.x,so.y,self.x,self.y)
                u *=self.getGravity(self.mass,so.mass,self.norme((self.x-so.x,self.y-so.y)))
                so.applied(u)
                
    def drawVectors(self,c):
        for v in self.appliedForces:
            c.create_line(self.x, self.y, self.x+v[0], self.y+v[1], fill='white')
            
        c.create_line(self.x, self.y, self.x+self.getCarthesian()[0]*20, self.y+self.getCarthesian()[1]*20, fill='green')
        
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
        return sumForces*300/self.mass

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
                "Earth": SpacialObject(5, 6*10**4, 200, 300, "blue",[0,-6]),
                "Sun": SpacialObject(5, 2*10**10, 300, 300, "yellow",[0,0])
            }
        self.shownSection = section(self)
        self.shownAside = aside(self)


class section(tk.Canvas):
    def __init__(self, root, **kwargs):
        self.root = root

        tk.Canvas.__init__(self, self.root, background="black", **kwargs)
        self.pack(fill=tk.BOTH, side="left", expand=True)
        self.i = 0
        self.drawCanvas()

    def drawCanvas(self):
        self.delete("all")
        # On aplique chaque force de chaque objet
        for name, so in self.root.spacialObjects.items():
            so.applyForces(self.root.spacialObjects)
        
        # On fait déplace puis dessine chaque objet
        for name, so in self.root.spacialObjects.items():
            #so.drawVectors(self)
            so.move()
            self.create_text(so.x, so.y+so.radius+5, text=name, fill="white")
            self.showSpacialObject(so)
        self.i += 1
        self.after(41, self.drawCanvas)

    def showSpacialObject(self, so):
        self.drawCircle(so.radius, so.x, so.y, so.color)
        pass

    def drawCircle(self, radius, centerX, centerY, color):
        self.create_oval(centerX-radius, centerY-radius, centerX+radius,
                         centerY+radius, fill=color)


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
        addObjectWindow(root)
        root.mainloop()


class objectFrame(tk.Frame):
    def __init__(self, root, name, so):
        self.name = name
        self.so = so
        self.root = root

        super().__init__(root, background="white", relief=tk.GROOVE, bd=1)
        self.pack(side=tk.TOP, padx=5, pady=5)

        tk.Label(self, text=name, background="white",
                 width=40).grid(padx=5, pady=5, row=0, column=0, columnspan=6)

        # Mass
        tk.Label(self, text="Massse :",
                 background="white").grid(row=1, column=0)
        massVar = tk.StringVar(value=so.mass)
        massVar.trace_add("write", lambda a, b, c: print(a, b, c))
        tk.Entry(self, textvariable=massVar, width=5,
                 bg="SystemButtonFace").grid(row=1, column=1)
        tk.Label(self, text="kg", background="white").grid(row=1, column=2)

        # Speed
        tk.Label(self, text="Vitesse :",
                 background="white").grid(row=2, column=0)
        speedVar = tk.IntVar(value=so.speed)
        tk.Entry(self, textvariable=speedVar, width=5,
                 bg="SystemButtonFace").grid(row=2, column=1)
        tk.Label(self, text="m/s", background="white").grid(row=2, column=2)

        # Color
        tk.Label(self, text="Coleur :", background="white").grid(row=3,
                                                                 column=0)
        self.colorB = tk.Button(self, text="   ", command=self.changeColor,
                                width=2, bg=so.color, relief="flat")
        self.colorB.grid(row=3, column=1)

    def changeColor(self):
        newColor = tk.colorchooser.askcolor()[1]
        if newColor is not None:
            self.so.color = newColor
            self.colorB.configure(bg=newColor)


class addObjectWindow(tk.Frame):
    def __init__(self, fenetre, **kwargs):
        tk.Frame.__init__(self, fenetre, **kwargs)
        self.pack(fill=tk.BOTH)


root = tk.Tk()
root.resizable(height=None, width=None)
root.title('Orbit Simulator')
root.geometry('1000x800')

interface = mainInterface(root)
interface.mainloop()
