/*
 0 Barcode
 1 Descrizione
 2 Quantità
 3 Reparto
 4 Scorta
 5 Fornitore
 6 Costo
 7 Prezzo 1
 8 Prezzo 2
 9 Prezzo 3
10 Note
11 Immagini
*/

const List<String> fields = [
  'Barcode', 'Descrizione', 
  'Quantità', 'Reparto', 
  'Scorta', 'Fornitore', 
  'Costo', 'Prezzo 1', 
  'Prezzo 2', 'Prezzo 3', 
  'Note', 'Immagini',
];

String mergeFields(List<String> fieldsToMerge) {
  String record = '';
  for(int i=0; i<fields.length; i++) {
    record += fieldsToMerge[i];
    if(i != fields.length-1) {
      record += ';';
    }
  }
  return record;
}

const bool editMode = false;
const bool addMode = true;

const bool searchMode = false;
const bool deleteMode = true;
