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
