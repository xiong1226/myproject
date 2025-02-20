import tkinter as tk
import os
import random
def changeImage():
    global rolling
    if rolling:
        #TODO 
        random_image = random.choice(IMAGES)
        label.configure(image=random_image)
        label.image = random_image 
        label.after(50,changeImage)

def keyPress(event):
    global rolling
    if rolling:
        rolling = False
    else:
        rolling = True
        label.after(50,changeImage)

window = tk.Tk()
window.title("Dice Roller")
rolling = False
DOT_IMAGES = ['/resource/1.png', '/resource/2.png', '/resource/3.png',
              '/resource/4.png', '/resource/5.png', '/resource/6.png']
IMAGES = [tk.PhotoImage(file=os.path.dirname(__file__)+DOT_IMAGES[i]) for i in range(6)]
label = tk.Label(window,height=400,width=400)
label.configure(image=IMAGES[0])

window.bind("<ButtonPress-1>", keyPress)
label.pack()
window.mainloop()