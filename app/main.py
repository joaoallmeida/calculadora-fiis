from flask import Flask, render_template, request, redirect
import requests
import pandas as pd
import io

app = Flask(__name__)


def get_data() -> pd.DataFrame:
        try:
            url = "https://statusinvest.com.br/category/AdvancedSearchResultExport?search=%7B%22Segment%22%3A%22%22%2C%22Gestao%22%3A%22%22%2C%22my_range%22%3A%220%3B20%22%2C%22dy%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22p_vp%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22percentualcaixa%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22numerocotistas%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22dividend_cagr%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22cota_cagr%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22liquidezmediadiaria%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22patrimonio%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22valorpatrimonialcota%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22numerocotas%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%2C%22lastdividend%22%3A%7B%22Item1%22%3Anull%2C%22Item2%22%3Anull%7D%7D&CategoryType=2"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
            
            response = requests.get( url, headers=headers)
            content = response.content
            response.raise_for_status()

            df = pd.read_csv(io.StringIO(content.decode('utf-8')), sep=';')
            df['PRECO'] = df['PRECO'].apply(lambda x: float(x.replace(".", "").replace(",", ".")))
            df['ULTIMO DIVIDENDO'] = df['ULTIMO DIVIDENDO'].apply(lambda x: float(str(x).replace(".", "").replace(",", ".")))

        except Exception as e:
            raise e
        
        return df 

def calculator(codes:list, cotes:int) -> list[str, any]:
    try:

        data = list()

        df = get_data()
        df = df[df['TICKER'].isin(codes)]

        for x, y in df.iterrows():

            data.append({
                "fundo": y['TICKER'],
                "preco": y['PRECO'],
                "cotas": cotes,
                "ult_dividendo": y['ULTIMO DIVIDENDO'],
                "investimento": "{:,.2f}".format(y['PRECO'] * cotes),
                "dividendo": "{:,.2f}".format(cotes * y['ULTIMO DIVIDENDO']),
                "totalInvestir": "{:,.2f}".format(y['PRECO'] * 1000 / y['ULTIMO DIVIDENDO'])
            })

        return data
    except Exception as e:
        raise e


@app.route('/')
def index():
    return redirect('/calculadora')

@app.route("/calculadora", methods=['GET','POST'])
def calc():
    if request.method == "POST":
    
        codes = request.form.get('codigo').split(',')
        cotes = int(request.form.get('quantidade'))

        data = calculator(codes,cotes)
        
        return render_template('index.html', tableData=data)

    return render_template('index.html')

if __name__=="__main__":
    app.run(host="0.0.0.0")
    