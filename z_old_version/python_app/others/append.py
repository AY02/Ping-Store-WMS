from sys import argv

def getBarcode(record, sep):
    return record.split(sep)[0].strip()

def appendFile(filename1, filename2):
    with open(filename1, 'r+') as f1, open(filename2, 'r') as f2:
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

filename1 = argv[1]
filename2 = argv[2]
appendFile(filename1, filename2)
