import gspread
from gspread import Cell
from oauth2client.service_account import ServiceAccountCredentials
 
class UserDatabase:
    def __init__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
 
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.

        #Uncomment for DEV
        #self.sheet = client.open("Keycards").worksheet("Test Sheet")

        #Uncomment for PROD
        self.sheet = client.open("Keycards").sheet1

    def getUserByField(self, fieldName, fieldValue):
        (user, index) = self._getUserByField(fieldName, fieldValue)
        return user
    
    def _getUserByField(self, fieldName, fieldValue):
        fields = self.sheet.row_values(1)
        field_column_idx = fields.index(fieldName) + 1
        print(fieldName + " at " + str(field_column_idx))

        field_values = self.sheet.col_values(field_column_idx)

        try:
            user_row_idx = field_values.index(fieldValue) + 1
            user_values = self.sheet.row_values(user_row_idx)
            
            user = dict(zip(fields,user_values))
            user.pop('',None)
            
            return (user, user_row_idx)
        except ValueError:
            raise KeyError("User Not Found")

    def addUser(self, user):
        columnNames = self.sheet.row_values(1)
        row = [user.get(col,'') for col in columnNames]
        self.sheet.append_row(row)

    def updateUser(self, keyField, keyValue, user):
        (unused_user, row) = self._getUserByField(keyField, keyValue)
        col_headers = self.sheet.row_values(1)

        cells = self.sheet.range(row,1,row,len(col_headers))
        
        for (col,header) in enumerate(col_headers):
            cell = cells[col]#self.sheet.cell(row, col)
            col = col + 1
            new_value = user.get(header, cell.value)
            if(header == 'ID' or not header or new_value == cell.value): continue
            self.sheet.update_cell(row, col, new_value)
