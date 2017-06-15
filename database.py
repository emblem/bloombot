import gspread
import json
from gspread import Cell
from oauth2client.service_account import ServiceAccountCredentials
 
class UserDatabase:
    def __init__(self):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        self.init_client()

    def init_client(self):
        client = gspread.authorize(self.creds)
 
        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.

        #Uncomment for DEV
        self.sheet = client.open("Keycards").worksheet("Test Sheet")

        #Uncomment for PROD
        #self.sheet = client.open("Keycards").sheet1

    def getUserByField(self, fieldName, fieldValue):
        (user, index) = self._getUserByField(fieldName, fieldValue)
        return user
    
    def _getUserByField(self, fieldName, fieldValue):
        self.init_client()
        fields = self.sheet.row_values(1)
        field_column_idx = fields.index(fieldName) + 1

        field_values = self.sheet.col_values(field_column_idx)[1:]        

        try:
            if fieldName == "Plate":                
                user_row_idx = self.findPlate(field_values, fieldValue)
            else:
                user_row_idx = field_values.index(fieldValue)

            user_row_idx = user_row_idx + 2
            user_values = self.sheet.row_values(user_row_idx)

            plate_idx = fields.index("Plate")
            if user_values[plate_idx]:
                user_values[plate_idx] = json.loads(user_values[plate_idx])
            else:
                user_values[plate_idx] = [""]
            
            user = dict(zip(fields,user_values))
            user.pop('',None)
            
            return (user, user_row_idx)
        except ValueError as e:
            print(e)
            raise KeyError("User Not Found")

    def findPlate(self, field_values, plateKey):
        for idx, plate_list_str in enumerate(field_values):
            if not plate_list_str: continue            
            
            plate_list = json.loads(plate_list_str)
            for plate in plate_list:
                if plate == plateKey:
                    return idx
        raise ValueError("No such plate")

    def addUser(self, user):
        self.init_client()
        columnNames = self.sheet.row_values(1)
        row = [user.get(col,'') if col != "Plate" else json.dumps(user.get(col,'')) for col in columnNames]
        self.sheet.append_row(row)

    def updateUser(self, keyField, keyValue, user):
        (unused_user, row) = self._getUserByField(keyField, keyValue)

        col_headers = self.sheet.row_values(1)

        cells = self.sheet.range(row,1,row,len(col_headers))
        
        for (col,header) in enumerate(col_headers):
            cell = cells[col]#self.sheet.cell(row, col)
            col = col + 1
            if header != "Plate":
                new_value = user.get(header, cell.value)
            else:
                if(user.get(header,None)):
                    new_value = json.dumps(user.get(header))
                elif cell.value:
                    new_value = cell.value
                else:
                    new_value = '[""]'

            if(header == 'ID' or not header or new_value == cell.value): continue
            self.sheet.update_cell(row, col, new_value)
