from flask import Flask, render_template, request, redirect, flash
from typing import Dict
import requests
import pandas as pd
import io
import traceback



class Calculator:

    def __init__(self, codes:list, choice:str, value:float) -> None:
        self.codes = [x.strip() for x in codes]
        self.choice = choice 
        self.value = value


    def get_data(self) -> pd.DataFrame:
            
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
    
    def check_exists(self, df:pd.DataFrame):
        check = False
        for code in self.codes:
            if code not in df['TICKER'].values:
                flash(f"Fundo imobiliário {code} não encontrado.", "warning")
            else:
                check = True
        return check

    def calculator(self) -> Dict:
        
        data_list = list()
        data_dict = dict()
        
        try:
            df = self.get_data()

            if self.check_exists(df):
                for _ , row in df.iterrows():
        
                    if self.choice == 'cotas':
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
                        "totalCotas": round((1000 / row['ULTIMO DIVIDENDO']))
                    }

                    data_list.append(values)
        
                data_dict['result'] = data_list
            
                if len(data_list) > 1:
                    data_dict['summary'] = {
                        'total_investido': sum(row['investimento'] for row in data_list),
                        'total_dividendo': sum(row['dividendo'] for row in data_list),
                        'total_investir': sum(row['totalInvestir'] for row in data_list),
                        'total_cotas':sum(row['totalCotas'] for row in data_list)    
                    }

        except Exception as e:
            flash(f'Erro ao calcular metricas: {traceback.format_exc()}', "error")
        
        return data_dict
            
    
###########################################################
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():
    # Redirecionando URL para o endereço /calculadora
    return redirect('/calculadora')

@app.route("/calculadora", methods=['GET','POST'])
def calc():
    # Verifica o tipo de requisição.
    if request.method == "POST":
        """
            Coleta os dados de entradas:
             * Codigo do fundo
             * Quantidade de cotas
             * Valor a investir
        """

        codes = request.form.get('codigo').upper().split(',')
        value = float(request.form.get('valor'))
        choice = request.form.get('radio')

        calc = Calculator(codes,choice,value)
        data = calc.calculator()

        return render_template('index.html', data=data)
        

    return render_template('index.html')

if __name__=="__main__":
    app.run(host="0.0.0.0")