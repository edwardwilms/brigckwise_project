from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from decimal import Decimal
from typing import Dict
import pandas as pd
import numpy as np

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
        if not Decimal('0') <= self.taxa_performance <= Decimal('100'):
            raise ValueError("taxa_performance must be between 0 and 100")
        if not Decimal('0') <= self.corretagem <= Decimal('100'):
            raise ValueError("corretagem must be between 0 and 100")

@app.post("/update-excel")
async def update_excel(input_data: InputData):
    try:
        # Load the Excel file
        df = pd.read_excel('c:/Users/wilmsedw/Documents/brickwise_project/BUSINESS PLAN - BWI.xlsx', sheet_name='INPUTS')

        # Update the input values in the Excel file
        df.loc[6, 'C'] = input_data.operacao_total  # C7
        df.loc[7, 'D'] = input_data.financiamento  # D8
        df.loc[12, 'G'] = input_data.metragem_terreno  # G14
        df.loc[13, 'G'] = input_data.metragem_total_venda  # G15
        df.loc[14, 'G'] = input_data.metragem_equivalente_construcao  # G16
        df.loc[15, 'G'] = input_data.custo_m2_construcao  # G17
        df.loc[16, 'G'] = input_data.preco_m2_venda  # G18
        df.loc[18, 'G'] = input_data.preco_terreno  # G20
        df.loc[20, 'D'] = input_data.custo_construcao  # D21
        df.loc[20, 'E'] = input_data.custo_construcao_prazo  # E21
        df.loc[23, 'D'] = float(input_data.taxa_performance)  # D24
        df.loc[26, 'C'] = float(input_data.corretagem)  # C27

        # Save the updated Excel file without overwriting the entire sheet
        with pd.ExcelWriter('BUSINESS PLAN - BWI.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name='INPUTS')

        return {"status": "success", "message": "Excel file updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/read-excel")
async def read_excel(file_path: str):
    try:
        # Load the Excel file
        df = pd.read_excel('c:/Users/wilmsedw/Documents/brickwise_project/BUSINESS PLAN - BWI.xlsx', sheet_name='INPUTS')

        # Extract the input values from the Excel file
        input_data = {
            "operacao_total": df.loc[6, 'C'],
            "financiamento": df.loc[7, 'D'],
            "metragem_terreno": df.loc[12, 'G'],
            "metragem_total_venda": df.loc[13, 'G'],
            "metragem_equivalente_construcao": df.loc[14, 'G'],
            "custo_m2_construcao": df.loc[15, 'G'],
            "preco_m2_venda": df.loc[16, 'G'],
            "preco_terreno": df.loc[18, 'G'],
            "custo_construcao": df.loc[20, 'D'],
            "custo_construcao_prazo": df.loc[20, 'E'],
            "taxa_performance": Decimal(str(df.loc[23, 'D'])),
            "corretagem": Decimal(str(df.loc[26, 'C']))
        }

        # Load the output values from the 'FLUXO AUTOMATICO' sheet
        df = pd.read_excel('c:/Users/wilmsedw/Documents/brickwise_project/BUSINESS PLAN - BWI.xlsx', sheet_name='FLUXO AUTOMATICO')
        output_data = {
            "exposicao_caixa": df.loc[0, 'E3'],
            "meses_payback": df.loc[0, 'E4'],
            "corretagem": df.loc[0, 'E5'],
            "taxa_sucesso": df.loc[0, 'E6'],
            "lucro_bruto": df.loc[0, 'E7'],
            "ir_ganho_capital": df.loc[0, 'E8'],
            "lucro_liquido": df.loc[0, 'E9'],
            "roi": df.loc[0, 'E10'],
            "tir_mensal": df.loc[0, 'E11']
        }

        return {"status": "success", "inputData": input_data, "outputData": output_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/calculate")
async def calculate(input_data: InputData):
    try:
        # Perform calculations based on the input data
        exposicao_caixa = input_data.operacao_total - input_data.financiamento
        meses_payback = 12
        corretagem = input_data.preco_terreno * (input_data.corretagem / 100)
        taxa_sucesso = 0.8
        lucro_bruto = (input_data.metragem_total_venda * input_data.preco_m2_venda) - input_data.custo_construcao
        ir_ganho_capital = lucro_bruto * 0.15
        lucro_liquido = lucro_bruto - ir_ganho_capital
        roi = lucro_liquido / input_data.financiamento
        tir_mensal = 0.05

        outputs = {
            "exposicao_caixa": exposicao_caixa,
            "meses_payback": meses_payback,
            "corretagem": corretagem,
            "taxa_sucesso": taxa_sucesso,
            "lucro_bruto": lucro_bruto,
            "ir_ganho_capital": ir_ganho_capital,
            "lucro_liquido": lucro_liquido,
            "roi": roi,
            "tir_mensal": tir_mensal
        }
        return {"status": "success", "data": outputs}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))