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
        self.sheet = client.open("Keycards").sheet1

    def getUserByField(self, fieldName, fieldValue):
        (user, index) = self._getUserByField(fieldName, fieldValue)
        return user
    
    def _getUserByField(self, fieldName, fieldValue):
        records = self.sheet.get_all_records()
        try:
            return ((user,i+2) for i,user in enumerate(records) if user[fieldName] == fieldValue).next()
        except StopIteration:
            raise KeyError("User Not Found")

    def addUser(self, user):
        columnNames = self.sheet.row_values(1)
        row = [user.get(col,'') for col in columnNames]
        self.sheet.insert_row(row,2)

    def updateUser(self, keyField, keyValue, user):
        (unused_user, row) = self._getUserByField(keyField, keyValue)
        col_headers = self.sheet.row_values(1)
        
        cell_list = self.sheet.range(row,1,row,self.sheet.col_count)

        for cell in cell_list:
            cell.value = user.get(col_headers[cell.col-1],cell.value)
        
        self.sheet.update_cells(cell_list)    
        
