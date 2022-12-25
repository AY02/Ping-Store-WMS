import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

filename = ''
filename2 = ''

def getBarcode(record, sep):
    return record.split(sep)[0].strip()

def appendFile():
    if filename != '' and filename2 != '':
        with open(filename, 'r+') as f1, open(filename2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

            for i in range(len(lines2)):
                isInside = False
                
                for j in range(len(lines1)):
                    if getBarcode(lines2[i], ';') == getBarcode(lines1[j], ';'):
                        isInside = True
                        break
                if not isInside:
                    f1.write(lines2[i])

def removeDuplicates():
    if filename != '':
        newFilename = 'new_import.txt'
        with open(filename, 'r') as f1, open(newFilename, 'w', encoding='utf-8') as f2:
            barcodes_seen = []

            lines1 = f1.readlines()
            barcodes1 = []

            for i in range(len(lines1)):
                barcodes1.append(getBarcode(lines1[i], ';'))

                if barcodes1[i] not in barcodes_seen:
                    f2.write(lines1[i])
                    barcodes_seen.append(barcodes1[i])

def browseFiles():
    root.update()
    global filename
    filename = askopenfilename()
    if filename:
        labelFile.configure(text=filename)

def browseFiles2():
    root.update()
    global filename2
    filename2 = askopenfilename()
    if filename2:
        labelFile2.configure(text=filename2)

appendMode = False
def appendFile_onClick():
    global appendMode, removeMode
    if not appendMode:
        labelFile.grid(row=1, column=1, columnspan=5, sticky=tk.W + tk.E)
        buttonExplore.grid(row=1, column=6)
        labelFile2.grid(row=2, column=1, columnspan=5, sticky=tk.W + tk.E)
        buttonExplore2.grid(row=2, column=6)
        global filename, filename2
        filename = ''
        labelFile.configure(text='Seleziona un file')
        filename2 = ''
        labelFile2.configure(text='Seleziona un file')
        appendMode = True
        removeMode = False
    else:
        appendFile()

removeMode = False
def removeDuplicates_onClick():
    global removeMode, appendMode
    if not removeMode:
        labelFile.grid(row=1, column=1, columnspan=5, sticky=tk.W + tk.E)
        buttonExplore.grid(row=1, column=6)
        labelFile2.grid_remove()
        buttonExplore2.grid_remove()
        global filename, filename2
        filename = ''
        labelFile.configure(text='Seleziona un file')
        filename2 = ''
        labelFile2.configure(text='Seleziona un file')
        removeMode = True
        appendMode = False
    else:
        removeDuplicates()

root = tk.Tk()
root.title('File Manipulation (Alpha v0.1)')
root.config(background='white')

labelFile = tk.Label(root, text='Seleziona un file', width=80, height=2, fg='blue')
buttonExplore = tk.Button(root, text='Browse Files', width=20, height=2, command=browseFiles)

labelFile2 = tk.Label(root, text='Seleziona un file', width=80, height=2, fg='blue')
buttonExplore2 = tk.Button(root, text='Browse Files', width=20, height=2, command=browseFiles2)

button_AppendFile = tk.Button(root, text='Append File', width=100, height=5, command=appendFile_onClick)
button_RemoveDuplicates = tk.Button(root, text='Remove Duplicates', width=100, height=5, command=removeDuplicates_onClick)

#columnspan e' quante colonne occupa, sticky e' da dove si estende se il widget e' superiore alla cella
button_AppendFile.grid(row=3, column=1, columnspan=6, sticky=tk.W + tk.E)
button_RemoveDuplicates.grid(row=4, column=1, columnspan=6, sticky=tk.W + tk.E)

root.mainloop()
