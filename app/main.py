from flask import Flask, render_template, request, redirect, flash
from calculator import Calculator

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET','POST'])
def calc():
    # Verifica o tipo de requisição.
    if request.method == "POST":
        """
            Coleta os dados de entradas:
             * Codigo do fundo
             * Quantidade de cotas
             * Valor a investir
        """

        founds = request.form.get('found').upper().split(',')
        value_invested = float(str(request.form.get('value_invested',type=str)).replace(',',''))
        choice = request.form.get('choice')

        calc = Calculator(founds,choice,value_invested)
        data = calc.calculator()

        return render_template('index.html', data=data)

    return render_template('index.html')

@app.route('/sobre', methods=['GET'])
def about():
    return render_template('about.html')


if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)
