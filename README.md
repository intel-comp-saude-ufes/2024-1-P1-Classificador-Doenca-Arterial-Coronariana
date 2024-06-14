# 2024-2-P1-Classificador-Doenca-Arterial-Coronariana
Trabalho 01 - Disciplina Inteligência Computacional em Saúde (TIC - INF16170 / PINF-X073)

O presente trabalho tem como objetivo a implementação e a análise de diferentes classificadores de doença arterial coronariana (DAC). Para isso, utilizou-se a base pública *Classification of Coronary Artery Disease* presente no Kaggle. Mais informações sobre a base, como descrição das colunas e informações gerais sobre os dados, podem ser encontradas no link [aqui](https://www.kaggle.com/datasets/saeedeheydarian/classification-of-coronary-artery-disease/data).


## Métodos
Baseado nas características da base, optou-se por treinar e avaliar os seguintes métodos:
- Regressão Logística
- Árvore de Decisão
- Random Forest
- SVM
- XGBoost

## Como executar
O código que implementa os classificadores está disponível tanto no formato de jupyter-notebook quanto em python. Para executar o código, basta clonar o repositório e na pasta raíz digitar no terminal:

Em caso de jupyter-notebook, é preciso ter o jupyter instalado. Para instalar, basta digitar no terminal:
```
pip install notebook
```
Depois, basta executar o comando:
```
jupyter cad_classifier.ipynb
```
Em caso de python:
```
python cad_classifier.py
```
É importante garantir que o arquivo `CAD.csv` esteja na mesma pasta que o código.

## Mais informações

Para mais informações sobre o projeto, assista ao vídeo feito pelos organizadores descrevendo a motivação por trás do projeto. O vídeo pode ser encontrado [aqui](https://youtu.be/cdmFSs4j_go).
