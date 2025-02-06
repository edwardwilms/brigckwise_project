from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decimal import Decimal
from typing import Dict
import pandas as pd
import openpyxl
import xlwings as xw
import os

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

current_dir = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_dir, 'BUSINESS PLAN - BWI.xlsx')

@app.post("/update-excel")
async def update_excel(input_data: InputData):
    try:
        # Open the Excel file
        workbook = openpyxl.load_workbook(excel_path)
        worksheet = workbook['INPUTS']

        # Update the input values in the Excel file
        worksheet['C7'] = input_data.operacao_total
        worksheet['D8'] = input_data.financiamento
        worksheet['C13'] = input_data.metragem_terreno
        worksheet['C14'] = input_data.metragem_total_venda
        worksheet['C15'] = input_data.metragem_equivalente_construcao
        worksheet['C16'] = input_data.custo_m2_construcao
        worksheet['C17'] = input_data.preco_m2_venda
        worksheet['C19'] = input_data.preco_terreno
        worksheet['D21'] = input_data.custo_construcao
        worksheet['E21'] = input_data.custo_construcao_prazo
        worksheet['C24'] = float(input_data.taxa_performance)
        worksheet['C27'] = float(input_data.corretagem)

        # Save the modified Excel file
        workbook.save(excel_path)

        return {"status": "success", "message": "Excel file updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/read-excel")
async def read_excel():
    try:
        # Open the Excel file
        workbook = openpyxl.load_workbook(excel_path, data_only=True)
        input_worksheet = workbook['INPUTS']
        
        # Using xlwings to read the output values from the Excel file
        app = xw.App(visible=False)
        wb = xw.Book(excel_path)
        sheet = wb.sheets['FLUXO AUTOMATICO']
        
        # Read values from cells with formulas
        exposicao_caixa = sheet.range('E3').value
        meses_payback = sheet.range('E4').value
        corretagem_venda = sheet.range('E5').value
        taxa_sucesso = sheet.range('E6').value
        lucro_bruto = sheet.range('E7').value
        ir_ganho_capital = sheet.range('E8').value
        lucro_liquido = sheet.range('E9').value
        roi = sheet.range('E10').value
        tir_mensal = sheet.range('E11').value
        
        wb.close()
        app.quit()
        
        # Multiply taxa_performance, corretagem, rio and tir_mensal by 100
        taxa_performance = input_worksheet['C24'].value * 100 if input_worksheet['C24'].value else 0
        corretagem = input_worksheet['C27'].value * 100 if input_worksheet['C27'].value else 0
        roi = roi * 100 if roi else 0
        tir_mensal = tir_mensal * 100 if tir_mensal else 0

        # Return the output data
        return {
            "inputData": {
                "operacao_total": input_worksheet['C7'].value,
                "financiamento": input_worksheet['D8'].value,
                "metragem_terreno": input_worksheet['C13'].value,
                "metragem_total_venda": input_worksheet['C14'].value,
                "metragem_equivalente_construcao": input_worksheet['C15'].value,
                "custo_m2_construcao": input_worksheet['C16'].value,
                "preco_m2_venda": input_worksheet['C17'].value,
                "preco_terreno": input_worksheet['C19'].value,
                "custo_construcao": input_worksheet['D21'].value,
                "custo_construcao_prazo": input_worksheet['E21'].value,
                "taxa_performance": taxa_performance,
                "corretagem": corretagem
            },
            "outputData": {
                "exposicao_caixa": exposicao_caixa,
                "meses_payback": meses_payback,
                "corretagem_venda": corretagem_venda,
                "taxa_sucesso": taxa_sucesso,
                "lucro_bruto": lucro_bruto,
                "ir_ganho_capital": ir_ganho_capital,
                "lucro_liquido": lucro_liquido,
                "roi": roi,
                "tir_mensal": tir_mensal
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))