from flask import Flask, jsonify, request
import numpy as np
from scipy.integrate import dblquad, tplquad
import matplotlib.pyplot as plt

app = Flask(__name__)

dados_temperatura = [
    {'data': '2024-06-10', 'temp_min': 20, 'temp_max': 28},
    {'data': '2024-06-11', 'temp_min': 18, 'temp_max': 25},
    {'data': '2024-06-12', 'temp_min': 28, 'temp_max': 35},
    {'data': '2024-06-13', 'temp_min': 15, 'temp_max': 20},
    {'data': '2024-06-13', 'temp_min': 17, 'temp_max': 29},
    {'data': '2024-06-14', 'temp_min': 22, 'temp_max': 30},
    {'data': '2024-06-14', 'temp_min': 24, 'temp_max': 32}
]

# Consultar todas as temperaturas
@app.route('/dados_temperatura', methods=['GET'])
def obter_temperaturas():
    return jsonify(dados_temperatura)

# Consultar temperatura por data
@app.route('/dados_temperatura/<data>', methods=['GET'])
def obter_temperatura_por_data(data):
    for registro in dados_temperatura:
        if registro['data'] == data:
            return jsonify(registro)
    return jsonify({'erro': 'Data não encontrada'}), 404

# Editar temperatura por data
@app.route('/dados_temperatura/<data>', methods=['PUT'])
def editar_temperatura_por_data(data):
    temperatura_alterada = request.get_json()
    for registro in dados_temperatura:
        if registro['data'] == data:
            registro.update(temperatura_alterada)
            return jsonify(registro)
    return jsonify({'erro': 'Data não encontrada'}), 404

# Criar nova temperatura
@app.route('/dados_temperatura', methods=['POST'])
def incluir_nova_temperatura():
    nova_temperatura = request.get_json()
    dados_temperatura.append(nova_temperatura)
    return jsonify(nova_temperatura), 201

# Excluir temperatura por data
@app.route('/dados_temperatura/<data>', methods=['DELETE'])
def excluir_temperatura(data):
    for i, registro in enumerate(dados_temperatura):
        if registro['data'] == data:
            del dados_temperatura[i]
            return jsonify({'mensagem': 'Registro excluído com sucesso'})
    return jsonify({'erro': 'Data não encontrada'}), 404

# Definindo a função de temperatura (x, y) e (x, y, z)
def funcao_temperatura_dupla(x, y):
    return np.sin(x) * np.cos(y)  # Exemplo de função

def funcao_temperatura_tripla(x, y, z):
    return np.sin(x) * np.cos(y) * np.exp(z)  # Exemplo de função

# Rota para calcular a integral dupla e tripla da função de temperatura
@app.route('/calcular_integral', methods=['POST'])
def calcular_integral():
    params = request.get_json()
    tipo = params.get('tipo', 'dupla')
    if tipo == 'dupla':
        resultado, _ = dblquad(funcao_temperatura_dupla, 0, 1, lambda x: 0, lambda x: 1)
    elif tipo == 'tripla':
        resultado, _ = tplquad(funcao_temperatura_tripla, 0, 1, lambda x: 0, lambda x: 1, lambda x, y: 0, lambda x, y: 1)
    else:
        return jsonify({'erro': 'Tipo de integral inválido'}), 400
    return jsonify({'resultado': resultado})

# Rota para gerar o gráfico da distribuição de temperatura
@app.route('/plotar_distribuicao_temperatura', methods=['POST'])
def plotar_distribuicao_temperatura():
    params = request.get_json()
    x_min = params.get('x_min', 0)
    x_max = params.get('x_max', 1)
    y_min = params.get('y_min', 0)
    y_max = params.get('y_max', 1)
    tipo_grafico = params.get('tipo_grafico', 'contorno')
    
    x = np.linspace(x_min, x_max, 100)
    y = np.linspace(y_min, y_max, 100)
    X, Y = np.meshgrid(x, y)
    Z = funcao_temperatura_dupla(X, Y)

    plt_path = 'distribuicao_temperatura.png'
    
    if tipo_grafico == 'contorno':
        plt.contourf(X, Y, Z, 20, cmap='RdGy')
        plt.colorbar()
        plt.title('Distribuição de Temperatura')
        plt.xlabel('X')
        plt.ylabel('Y')
    elif tipo_grafico == 'linha':
        # Vamos plotar uma linha para y fixo (por exemplo, y = 0.5)
        y_fixed = 0.5
        z_line = funcao_temperatura_dupla(x, y_fixed)
        plt.plot(x, z_line)
        plt.title(f'Temperatura ao longo de x para y={y_fixed}')
        plt.xlabel('X')
        plt.ylabel('Temperatura')
    
    plt.savefig(plt_path)
    plt.close()

    return jsonify({'mensagem': 'Gráfico gerado', 'path': plt_path})

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)

