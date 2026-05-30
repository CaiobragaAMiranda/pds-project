from flask import Flask, request, jsonify, render_template
from pds.service import PDSService
import pandas as pd
import io

app = Flask(__name__)
# Certifique-se que o arquivo .pkl está na raiz onde roda o comando
pds_service = PDSService("./model_RFC_ROC_AUC_SMOTE.pkl")

# Definindo as colunas esperadas pelo service.py
EXPECTED_COLS = ["LOC", "COM", "BLK", "NOF", "NOC", "APF", "AMC", "NER", "NEH", "CYC", "MAD"]

@app.route('/', methods=['GET'])
def index():
    """Renderiza a página inicial com o formulário de upload."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400

    try:
        # Lê o CSV
        df = pd.read_csv(file, sep=';')

        # Verifica colunas
        missing_cols = [col for col in EXPECTED_COLS if col not in df.columns]
        if missing_cols:
            return f"Erro: Faltam colunas: {missing_cols}", 400

        results = []
        for index, row in df.iterrows():
            data_tuple = [row[col] for col in EXPECTED_COLS]
            pred = pds_service.predict(data_tuple)
            results.append(int(pred[0]))

        df['PREDICAO_BUG'] = results
        
        # --- MUDANÇA AQUI ---
        # Em vez de criar HTML, convertemos para uma lista de dicionários
        # Ex: [{'LOC': 559, 'COM': 47, ...}, {...}]
        dados_tabela = df.to_dict(orient='records')

        return render_template('index.html', dados=dados_tabela)

    except Exception as e:
        return f"Erro ao processar: {str(e)}", 500

# Mantemos a API original funcionando caso queira usar via código
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        data_tuple = data.get('data_tuple')
        result = pds_service.predict(data_tuple)
        return jsonify({"result": [int(element) for element in result]})
    except (TypeError, ValueError) as e:
        print(e)
        return jsonify({'error': 'Invalid parameters'}), 400

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)