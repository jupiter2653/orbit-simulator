# -*- coding: utf-8 -*-
import tkinter as tk

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self,background="white",width=300)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas,bg="white")

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

root = tk.Tk()
root.resizable(height = None, width = None)

root.title('Orbit Simulator')
root.geometry('1000x800') 

mainCanvas = tk.Canvas(root,background="black")
mainCanvas.pack(fill=tk.BOTH,side="left",expand=True)

listFrame = ScrollableFrame(root)
listFrame.pack(side="right",fill=tk.Y)
titre = tk.Label(listFrame.scrollable_frame,text="Simulateur d'orbite",background="white",font=("Arial", 20))
titre.pack(side=tk.TOP)
buttonAddObject = tk.Button(listFrame.scrollable_frame, text="Ajouter un objet", command=lambda a : a)
buttonAddObject.pack()


objectFrames = []
for i in range(50):
    objectFrames.append(tk.Frame(listFrame.scrollable_frame,background="white",relief=tk.GROOVE,bd=1))
    objectFrames[i].pack(side=tk.TOP,padx=5,pady=5)
    
    planetName = tk.Label(objectFrames[i], text="Nom de la planète",background="white",width=40)
    planetName.grid(padx=5,pady=5,row=0,column=0,columnspan=6)

    #Mass
    tk.Label( objectFrames[i], text="Massse :",background="white").grid(row=1,column=0)
    massVar = tk.StringVar()
    tk.Entry( objectFrames[i], textvariable=massVar, width=5,bg="SystemButtonFace").grid(row=1,column=1)
    tk.Label( objectFrames[i], text="kg",background="white").grid(row=1,column=2)
    
    #Speed
    tk.Label( objectFrames[i], text="Vitesse :",background="white").grid(row=2,column=0)
    speedVar = tk.StringVar()
    tk.Entry( objectFrames[i], textvariable=speedVar, width=5,bg="SystemButtonFace").grid(row=2,column=1)
    tk.Label( objectFrames[i], text="m/s",background="white").grid(row=2,column=2)

tk.mainloop() 