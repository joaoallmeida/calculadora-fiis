from flask import Flask, render_template, request
from calculator import Calculator

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/', methods=['GET','POST'])
def calc():
    """
    Coleta os dados de entradas:
        * Codigo do fundo
        * Quantidade de cotas
        * Valor a investir
    """
    if request.method == "POST":
        # Collect all the dynamically generated fields
        form_data = []
        data_found_aux = {}
        data_value_aux = {}

        # Loop through form data to capture dynamic fields
        for key in request.form:

            if key.startswith('found'):
                try:
                    index = key.split('_')[1]
                except IndexError:
                    index = 1

                found = request.form[key]
                data_found_aux[index] = found.upper()

            if key.startswith('value_invested'):
                try:
                    index = key.split('_')[2]
                except IndexError:
                    index = 1

                value_invested = request.form[key]
                data_value_aux[index] = float(value_invested.replace(',',''))

        for index in data_found_aux:
            if index in data_value_aux:
                form_data.append({
                   data_found_aux[index]:data_value_aux[index]
                })

        choice = request.form.get('choice')

        calc = Calculator(form_data,choice)
        data = calc.calculator()

        return render_template('index.html', data=data)

    return render_template('index.html')

@app.route('/sobre', methods=['GET'])
def about():
    return render_template('about.html')

if __name__=="__main__":
    app.run(host="0.0.0.0", debug=True)
