from sys import argv

def getBarcode(record, sep):
    return record.split(sep)[0].strip()

def removeDuplicates(filename, newFilename):
    
    with open(filename, 'r') as f1, open(newFilename, 'w', encoding='utf-8') as f2:
        barcodes_seen = []

        lines1 = f1.readlines()
        barcodes1 = []

        for i in range(len(lines1)):
            barcodes1.append(getBarcode(lines1[i], ';'))

            if barcodes1[i] not in barcodes_seen:
                f2.write(lines1[i])
                barcodes_seen.append(barcodes1[i])

filename = argv[1]
new_filename = argv[2]
removeDuplicates(filename, new_filename)
