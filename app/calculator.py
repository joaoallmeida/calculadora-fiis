from flask import flash
from typing import Dict
from datetime import datetime
from utils import encodeParam

import requests
import pandas as pd
import io
import traceback

class Calculator:
    def __init__(self, codes:list, choice:str, value:float) -> None:
        self.codes = [x.strip() for x in codes]
        self.choice = choice
        self.value = value
        self.currentYear = datetime.now().year

    def calculator(self) -> Dict:

        data_list = list()
        data_dict = dict()

        try:
            df = self.__get_data__()

            if self.__check_exists__(df):
                for _ , row in df.iterrows():

                    if self.choice == 'quotas':
                        cotes = self.value
                    else:
                        cotes = ( (self.value / len(df.index)) / row['PRECO'])

                    values = {
                        "fundo": row['TICKER'],
                        "preco": row['PRECO'],
                        "cotas": round(cotes),
                        "ult_dividendo": row['ULTIMO DIVIDENDO'],
                        "investimento": (row['PRECO'] * cotes),
                        "dividendo": (cotes * row['ULTIMO DIVIDENDO']),
                        "totalInvestir": (row['PRECO'] * 1000 / row['ULTIMO DIVIDENDO']),
                        "totalCotas": round((1000 / row['ULTIMO DIVIDENDO'])),
                        "report": self.__get_report__(row['TICKER'])
                    }

                    data_list.append(values)

                data_dict['result'] = data_list

                if len(data_list) > 1:
                    data_dict['summary'] = {
                        'total_investido': sum(row['investimento'] for row in data_list),
                        'total_dividendo': sum(row['dividendo'] for row in data_list),
                        'total_investir': sum(row['totalInvestir'] for row in data_list),
                        'total_cotas':  sum(row['totalCotas'] for row in data_list)
                    }

        except Exception as e:
            flash(f'Erro ao calcular metricas: {traceback.format_exc()}', "error")
        return data_dict

    def __get_data__(self) -> pd.DataFrame:
            url = "https://statusinvest.com.br/category/AdvancedSearchResultExport?search=%7B%22Segment%22%3A%22%22%2C%22Gestao%22%3A%22%22%2C%22my_range%22%3A%220%3B20%22%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_vp%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22percentualcaixa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22numerocotistas%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividend_cagr%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22cota_cagr%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezmediadiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22patrimonio%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22valorpatrimonialcota%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22numerocotas%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lastdividend%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%7D&CategoryType=2"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate"
            }

            try:
                response = requests.get( url, headers=headers)
                content = response.content
                response.raise_for_status()

                df = pd.read_csv(io.StringIO(content.decode('utf-8')), sep=';')

                df = df[df['TICKER'].isin(self.codes)]
                df['PRECO'] = df['PRECO'].apply(lambda x: float(x.replace(".", "").replace(",", ".")))
                df['DY'] = df['DY'].apply(lambda x: float(x.replace(".", "").replace(",", ".")))
                df['ULTIMO DIVIDENDO'] = df['ULTIMO DIVIDENDO'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")))

            except Exception as e:
                raise e
            return df

    def __get_report__(self, code:str) -> str:

        header = {"Content-Type":"application/json"}

        try:
            paramGetDetail = encodeParam({'typeFund':7,'identifierFund':code.replace('11','')})
            urlGetDetail = f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetDetailFundSIG/{paramGetDetail}"


            responseDetail = requests.get(urlGetDetail, headers=header, verify=False)
            details = responseDetail.json()['detailFund']

            cnpj = details['cnpj']
            identifierFund = details['acronym']

            paramListDocs = encodeParam(
                {
                    "pageNumber":1
                    ,"pageSize":4
                    ,"cnpj":cnpj
                    ,"identifierFund":identifierFund
                    ,"typeFund":7
                    ,"dateInitial":f"{self.currentYear}-01-01"
                    ,"dateFinal":f"{self.currentYear}-12-31"
                    ,"category":"7"
                }
            )
            urlListDocs = f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedDocuments/{paramListDocs}"
            responseDocs = requests.get(urlListDocs, headers=header, verify=False)
            docsList = responseDocs.json()

            if docsList['page']['totalRecords'] > 0:
                urlLink = docsList['results'][0]['urlViewerFundosNet'].replace('visualizarDocumento', 'exibirDocumento')
            else:
                paramListDocs = encodeParam(
                    {
                        "pageNumber":1
                        ,"pageSize":4
                        ,"cnpj":cnpj
                        ,"identifierFund":identifierFund
                        ,"typeFund":7
                        ,"dateInitial":f"{self.currentYear-1}-01-01"
                        ,"dateFinal":f"{self.currentYear-1}-12-31"
                        ,"category":"7"
                    }
                )
                urlListDocs = f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedDocuments/{paramListDocs}"
                responseDocs = requests.get(urlListDocs, headers=header, verify=False)
                docsList = responseDocs.json()

                urlLink = docsList['results'][0]['urlViewerFundosNet'].replace('visualizarDocumento', 'exibirDocumento')
        except IndexError:
            urlLink = None
        except Exception as e:
            raise e
        return urlLink

    def __check_exists__(self, df:pd.DataFrame) -> bool:
        check = False
        for code in self.codes:
            if code not in df['TICKER'].values:
                flash(f"Fundo imobiliário {code} não encontrado.", "warning")
            else:
                check = True
        return check
