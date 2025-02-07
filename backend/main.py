from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decimal import Decimal
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
import locale
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    operacao_total: float
    financiamento: float
    metragem_terreno: float
    metragem_total_venda: float
    metragem_equivalente_construcao: float
    custo_m2_construcao: float
    preco_m2_venda: float
    preco_terreno: float
    custo_construcao: float
    custo_construcao_prazo: float
    taxa_performance: Decimal
    corretagem: Decimal

    def __init__(self, **data):
        super().__init__(**data)
        self.taxa_performance = self.taxa_performance / 100
        self.corretagem = self.corretagem / 100
        if not Decimal('0') <= self.taxa_performance <= Decimal('1'):
            raise ValueError("taxa_performance must be between 0 and 100")
        if not Decimal('0') <= self.corretagem <= Decimal('1'):
            raise ValueError("corretagem must be between 0 and 100")

# Google Sheets setup
# Path to your downloaded JSON key file
# Uncomment line bellow for when using local development
# SERVICE_ACCOUNT_FILE = 'C:/Users/wilmsedw/Documents/brickwise_project/backend/brickwise-450120-69ac0aa13cfa.json'

# Spreadsheet ID.  You can find this in the URL of your sheet.
SPREADSHEET_ID = '18r93lBqOF1DjY9bvHOjIp00REAv-NUf5Xq6d5jupsrY'

# The scopes (permissions) your app needs.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Uncomment line bellow for when using local development
'''credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
credentials = service_account.Credentials.from_service_account_file(
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), scopes=SCOPES
)'''
# Get the JSON string from the environment variable
credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# Parse the JSON string into a dictionary
credentials_dict = json.loads(credentials_json)

# Create credentials from the dictionary
credentials = service_account.Credentials.from_service_account_info(
    info=credentials_dict, scopes=SCOPES
)

service = build('sheets', 'v4', credentials=credentials)

@app.post("/update-excel")
async def update_excel(input_data: InputData):
    try:
        # Update Google Sheet
        sheet_name = 'INPUTS'  # Replace with your sheet name
        updates = {
            'C7': input_data.operacao_total,
            'D8': input_data.financiamento,
            'C13': input_data.metragem_terreno,
            'C14': input_data.metragem_total_venda,
            'C15': input_data.metragem_equivalente_construcao,
            'C16': input_data.custo_m2_construcao,
            'C17': input_data.preco_m2_venda,
            'C19': input_data.preco_terreno,
            'D21': input_data.custo_construcao,
            'E21': input_data.custo_construcao_prazo,
            'C24': float(input_data.taxa_performance),
            'C27': float(input_data.corretagem),
        }

        for cell, value in updates.items():
            range_name = f'{sheet_name}!{cell}'
            body = {'values': [[value]]}  # Data must be a list of lists
            service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=range_name, valueInputOption='RAW', body=body).execute()

        return {"status": "success", "message": "Google Sheet updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/read-excel")
async def read_excel():
    try:
        # Read from Google Sheet
        input_sheet_name = 'INPUTS'
        output_sheet_name = 'FLUXO AUTOMATICO'
        input_cells = [
            'C7', 'D8', 'C13', 'C14', 'C15', 'C16', 'C17', 'C19', 'D21', 'E21', 'C24', 'C27',
        ]
        output_cells = ['E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11']  # Cells, not ranges yet

        input_ranges = [f'{input_sheet_name}!{cell}' for cell in input_cells]  # Create full ranges
        output_ranges = [f'{output_sheet_name}!{cell}' for cell in output_cells]  # Create full ranges


        input_result = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=input_ranges).execute()
        output_result = service.spreadsheets().values().batchGet(spreadsheetId=SPREADSHEET_ID, ranges=output_ranges).execute()

        input_value_ranges = input_result.get('valueRanges', [])
        output_value_ranges = output_result.get('valueRanges', [])

        input_values = {}
        for value_range in input_value_ranges:
            range_ = value_range.get('range')
            cell = range_.split('!')[1]  # Extract cell (e.g., C7)
            values = value_range.get('values', [])
            input_values[cell] = values[0][0] if values else None

        output_values = {}
        for value_range in output_value_ranges:
            range_ = value_range.get('range')
            cell = range_.split('!')[1]  # Extract cell
            values = value_range.get('values', [])
            output_values[cell] = values[0][0] if values else None

        def convert_percentage(value_str):  # Helper function
            if value_str:
                value_str = value_str.replace(',', '.')  # Replace comma with period
                value_str = value_str.replace('%', '')   # Remove %
                try:
                    value = float(value_str)
                    return value / 100 * 100 # divide by 100 to get the decimal representation and multiply by 100 to get the percentage value.
                except ValueError:
                    return 0  # Handle cases where conversion fails
            return 0  # Return 0 for empty or None values
        
        def convert_currency_number(value_str):
            if value_str:
                # Remove currency symbols (R$, $, etc.) and spaces
                value_str = re.sub(r'[R$\s]', '', value_str).strip()  # Remove currency symbols and spaces

                # Attempt locale-aware conversion
                try:
                    locale.setlocale(locale.LC_ALL, '')  # Use system's locale
                    value = locale.atof(value_str)
                    return value
                except (ValueError, AttributeError): # Handle cases where locale fails
                    try: # Attempt to use US locale
                        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
                        value = locale.atof(value_str)
                        return value
                    except (ValueError, AttributeError): # If even US fails, try converting after replacing comma with dot
                        value_str = value_str.replace(',', '.')
                        try:
                            value = float(value_str)
                            return value
                        except ValueError:
                            return 0
            return 0
        
        operacao_total = convert_currency_number(input_values.get('C7'))
        metragem_terreno = convert_currency_number(input_values.get('C13'))
        metragem_total_venda = convert_currency_number(input_values.get('C14'))
        metragem_equivalente_construcao = convert_currency_number(input_values.get('C15'))
        custo_m2_construcao = convert_currency_number(input_values.get('C16'))
        preco_m2_venda = convert_currency_number(input_values.get('C17'))
        preco_terreno = convert_currency_number(input_values.get('C19'))
        taxa_performance = convert_percentage(input_values.get('C24', '0%'))
        corretagem = convert_percentage(input_values.get('C27', '0%'))
        exposicao_caixa = convert_currency_number(output_values.get('E3'))
        corretagem_venda = convert_currency_number(output_values.get('E5'))
        taxa_sucesso = convert_currency_number(output_values.get('E6'))
        lucro_bruto = convert_currency_number(output_values.get('E7'))
        ir_ganho_capital = convert_currency_number(output_values.get('E8'))
        lucro_liquido = convert_currency_number(output_values.get('E9'))
        roi = convert_percentage(output_values.get('E10', '0%'))
        tir_mensal = convert_percentage(output_values.get('E11', '0%'))

        return {
            "inputData": {
                "operacao_total": operacao_total,
                "financiamento": float(input_values.get('D8', 0)),
                "metragem_terreno": metragem_terreno,
                "metragem_total_venda": metragem_total_venda,
                "metragem_equivalente_construcao": metragem_equivalente_construcao,
                "custo_m2_construcao": custo_m2_construcao,
                "preco_m2_venda": preco_m2_venda,
                "preco_terreno": preco_terreno,
                "custo_construcao": float(input_values.get('D21', 0)),
                "custo_construcao_prazo": float(input_values.get('E21', 0)),
                "taxa_performance": taxa_performance,
                "corretagem": corretagem,
            },
            "outputData": {
                "exposicao_caixa": exposicao_caixa,
                "meses_payback": float(output_values.get('E4', 0)),
                "corretagem_venda": corretagem_venda,
                "taxa_sucesso": taxa_sucesso,
                "lucro_bruto": lucro_bruto,
                "ir_ganho_capital": ir_ganho_capital,
                "lucro_liquido": lucro_liquido,
                "roi": roi,
                "tir_mensal": tir_mensal,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))