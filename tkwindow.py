import tkinter
import tkinter.font as TkFont
from tkinter import *
from tkinter import messagebox
import json


class MainWindow:
    def __init__(self):

        self.commandsList = []

        self.window = Tk()
        self.window.title("Gesture selector")
        self.window.geometry("1100x600")
        self.window.resizable (False,False)
        self.window.config(background="darkgray")
    
        optionsFrame = Frame(self.window,bg="darkgray")
        optionsFrame.grid(row=0,column=0)

        customFont = TkFont.Font(family="Arial", size=15)

        self.text1 = Label(optionsFrame, text="Swipe Up",font=customFont)
        self.text1.grid(row=0,column = 0, padx=20,pady=(40,6))

        self.box1 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box1.grid(row = 0, column = 1, padx=20, pady=(40,6))

        self.text2 = Label(optionsFrame, text="Swipe Down",font=customFont)
        self.text2.grid(row = 1, column = 0, padx=20, pady=14)

        self.box2 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box2.grid(row=1, column = 1, padx=20,pady=14)

        self.text3 = Label(optionsFrame, text="Swipe Left",font=customFont)
        self.text3.grid(row = 2, column = 0, padx=20, pady=14)

        self.box3 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box3.grid(row=2, column = 1, padx=20,pady=14)

        self.text4 = Label(optionsFrame, text="Swipe Right",font=customFont)
        self.text4.grid(row = 3, column = 0, padx=20, pady=14)

        self.box4 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box4.grid(row=3, column = 1, padx=20,pady=14)

        self.text5 = Label(optionsFrame, text="Fist",font=customFont)
        self.text5.grid(row = 4, column = 0, padx=20, pady=14)

        self.box5 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box5.grid(row=4, column = 1, padx=20,pady=14)

        self.text6 = Label(optionsFrame, text="Peace",font=customFont)
        self.text6.grid(row = 5, column = 0, padx=20, pady=14)

        self.box6 = Text(optionsFrame, height=1, width=35, font=customFont)
        self.box6.grid(row=5, column = 1, padx=20,pady=14)


        buttonClear = Button(optionsFrame, text="Clear", font=customFont, command=self.clear)
        buttonClear.grid(row = 2, column = 3, padx=10)

        buttonApply = Button(optionsFrame, text = "Apply", font=customFont,command=self.Apply)
        buttonApply.grid(row = 6, column = 1, padx=50, pady=(0,5))

        buttonLast = Button(optionsFrame, text = "Use Last \n Settings", font=customFont,command=self.stop)
        buttonLast.grid(row = 6, column = 2, padx=0,pady=(0,5))


    def stop(self):
        self.window.destroy()

    def clear(self):
        self.box1.delete("1.0",END)
        self.box2.delete("1.0",END)
        self.box3.delete("1.0",END)
        self.box4.delete("1.0",END)
        self.box5.delete("1.0",END)
        self.box6.delete("1.0",END)


    def Apply(self):
        textList = ["Swipe Up","Swipe Down","Swipe Left","Swipe Right","Fist","Peace"]
        boxList = [
            self.box1, self.box2, self.box3, self.box4, self.box5,self.box6
            ]
        answer = messagebox.askyesno(title= "Confirmation",
                                     message="Are you sure?",
                                     icon="warning",
                                     default= "no",
                                     )
        
        if answer:
            for textBox in boxList:
                if textBox.get:
                    self.commandsList.append(textBox.get("1.0", END))
                else:
                    self.commandsList.append('')
        
        
        jsonCommands = json.dumps(self.commandsList)
        print(jsonCommands)

        #settings is now all the appropraite commands
        with open("savedSettings.txt","w") as f:
            for i in range(len(textList)):
                f.write(f"{textList[i]}: {self.commandsList[i]}")
        
        self.window.destroy()
        



    def run(self):
        self.window.mainloop()