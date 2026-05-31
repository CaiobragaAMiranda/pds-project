import os
from flask import Flask, request, jsonify, render_template
from pds.service import PDSService
import pandas as pd

app = Flask(__name__)

# Lógica de seleção de modelo: Prioriza o Agente RL (Bug Hunter)
RL_MODEL_PATH = "./pds_bug_hunter_agent.zip"
LEGACY_MODEL_PATH = "./model_RFC_ROC_AUC_SMOTE.pkl"

if os.path.exists(RL_MODEL_PATH):
    pds_service = PDSService(RL_MODEL_PATH)
elif os.path.exists(LEGACY_MODEL_PATH):
    pds_service = PDSService(LEGACY_MODEL_PATH)
else:
    # Caso nenhum modelo exista, inicializamos um placeholder (pode falhar no predict)
    print("AVISO: Nenhum arquivo de modelo encontrado na raiz.")
    pds_service = None

# Colunas esperadas para o modelo supervisionado legado
EXPECTED_COLS = ["LOC", "COM", "BLK", "NOF", "NOC", "APF", "AMC", "NER", "NEH", "CYC", "MAD"]

@app.route('/', methods=['GET'])
def index():
    """Renderiza a página inicial com info do modelo ativo."""
    model_info = "Nenhum modelo carregado"
    if pds_service:
        model_info = "RL (PPO - Bug Hunter)" if pds_service.use_rl else "Supervisionado (Random Forest)"
    return render_template('index.html', model_type=model_info)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
    
    file = request.files['file']
    if file.filename == '':
        return "Nenhum arquivo selecionado", 400

    if not pds_service:
        return "Erro: Serviço de predição não inicializado (modelo ausente)", 500

    try:
        # Lê o CSV (suporta separador ; ou ,)
        try:
            df = pd.read_csv(file, sep=';')
            if len(df.columns) <= 1: # Tenta vírgula se o ponto-e-vírgula falhar
                file.seek(0)
                df = pd.read_csv(file, sep=',')
        except:
            return "Erro ao ler CSV. Certifique-se que o separador é ';' ou ','", 400

        results = []
        for index, row in df.iterrows():
            # Tenta pegar file_path para o RL
            file_path = row.get('file_path') or row.get('path')
            
            # Prepara tupla de métricas para o legado (preenche com 0 se faltar)
            data_tuple = [float(row.get(col, 0)) for col in EXPECTED_COLS]
            
            pred = pds_service.predict(data_tuple=data_tuple, file_path=file_path)
            results.append(int(pred[0]))

        df['PREDICAO_BUG'] = results
        dados_tabela = df.to_dict(orient='records')

        return render_template('index.html', 
                               dados=dados_tabela, 
                               model_type="RL" if pds_service.use_rl else "Legacy")

    except Exception as e:
        return f"Erro ao processar: {str(e)}", 500

@app.route('/predict', methods=['POST'])
def predict():
    """API de predição direta via JSON."""
    if not pds_service:
        return jsonify({'error': 'Service not initialized'}), 500
        
    try:
        data = request.get_json()
        data_tuple = data.get('data_tuple')
        file_path = data.get('file_path')
        
        result = pds_service.predict(data_tuple=data_tuple, file_path=file_path)
        
        return jsonify({
            "result": [int(element) for element in result],
            "model_type": "RL" if pds_service.use_rl else "Legacy",
            "file_path_used": file_path if pds_service.use_rl else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
