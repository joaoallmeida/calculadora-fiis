from flask import Flask, render_template, request, redirect, flash
from calculator import Calculator


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
    app.run(host="0.0.0.0", debug=True)