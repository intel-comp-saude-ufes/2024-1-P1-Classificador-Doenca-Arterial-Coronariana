# -*- coding: utf-8 -*-
"""20240530-cad.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18aHlDta6yEM3Hb7bYMyc9IhqL7dGMvbM

## Leitura e conversão em dados numéricos

Dados obtidos do dataset [Classification of Coronary Artery Disease](https://www.kaggle.com/datasets/saeedeheydarian/classification-of-coronary-artery-disease) do Kaggle.
"""

# Imports
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.model_selection import GridSearchCV

# Leitura dos dados
df = pd.read_csv("CAD.csv")
df.head()

# Informações gerais dos datasets mostram que não existem dados nulos
# Existem, no entanto, diversas colunas com dados em formato de texto (object)
# que precisam ser convertidos para numéricos
df.info()

# Existem várias colunas con dados booleanos no formato Y/N esses dados precisam
# ser convertidos para valores inteiros, especificamente 1/0
colunas_booleanas = ["Obesity",
                     "CRF",
                     "CVA",
                     "Airway disease",
                     "Thyroid Disease",
                     "CHF",
                     "DLP",
                     "Weak Peripheral Pulse",
                     "Lung rales",
                     "Systolic Murmur",
                     "Diastolic Murmur",
                     "Dyspnea",
                     "Atypical",
                     "Nonanginal",
                     "Exertional CP",
                     "LowTH Ang",
                     "LVH",
                     "Poor R Progression",
                     "FBS",
                     ]
df[colunas_booleanas].head()

df[colunas_booleanas] = df[colunas_booleanas].replace(["Y", "N"],[1, 0])
df[colunas_booleanas].head()

# A coluna "Sex", possui dados "Male" e "Fmale", que serão substituídos por
# 0 e 1
df["Sex"] = df["Sex"].replace(["Male", "Fmale"],[0, 1])
# A coluna "VHD", possui dados "N", "mild", "Moderate" e "Severe", que possuem
# uma ideia de sequencia e, por isso serão substituídos respectivamente por:
# 0, 1, 2 e 3
df["VHD"] = df["VHD"].replace(["N", "mild", "Moderate", "Severe"],[0, 1, 2, 3])
# A coluna "Cath", possui dados "Normal" e "Cad", que serão substuídos por 0 e 1
# respectivamente
df["Cath"] = df["Cath"].replace(["Normal", "Cad"],[0, 1])
df.head()

# Agora é possível observar que todos os dados são numéricos e não nulos
df.info()

"""## Etapa 1 - Avaliações Iniciais

Após realizado o pré-processamento, utilizamos o PCA para plotar os nossos dados para termos uma noção da distribuição das amostras.
"""

import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Separando a nossa coluna alvo
Y = df["Cath"]
df.drop(columns = ["Cath"], inplace=True)
# Apenas renomeando
X = df

# PLOT 2D DOS DADOS

pca = PCA(n_components = 2)
X_plot = pca.fit_transform(X)
X_plot = pd.DataFrame(X_plot)

columns = ['x', 'y']

X_plot.columns = columns

# Plotando
fig, ax = plt.subplots()
ax.scatter(X_plot[Y==1]['x'], X_plot[Y==1]['y'])
ax.scatter(X_plot[Y==0]['x'], X_plot[Y==0]['y'])

ax.legend(['CAD', 'Normal'])

ax.set_xlabel('Eixo X')
ax.set_ylabel('Eixo Y')
ax.set_title('Plot 2D dos Dados')

fig.show()

# PLOT 3D DOS DADOS

pca = PCA(n_components = 3)
X_plot = pca.fit_transform(X)
X_plot = pd.DataFrame(X_plot)

columns = ['x', 'y', 'z']

X_plot.columns = columns

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(X_plot[Y==1]['x'], X_plot[Y==1]['y'], X_plot[Y==1]['z'])
ax.scatter(X_plot[Y==0]['x'], X_plot[Y==0]['y'], X_plot[Y==0]['z'])

ax.set_xlabel('Eixo X')
ax.set_ylabel('Eixo Y')
ax.set_zlabel('Eixo Z')
ax.set_title('Plot 3D dos Dados')

ax.legend(['CAD', 'Normal'])

plt.show()

"""Com base na visualização dos dados, podemos fazer uma análise superficial dos nossos dados de forma a escolher alguns métodos de classificação para começarmos a avaliar. Todavia, é preciso considerar a natureza dos dados que estamos lidando para escolhermos nossa metodologia.

Informações clínicas de pacientes, como é o nosso caso, mostram-se dados difíceis de serem obtidos. Portanto, é natural que a quantidade de pacientes na base não seja muito grande. Apesar de ser um problema compreensível, não podemos ignorá-lo na hora de treinar o nosso modelo.

Assim, uma decisão que tomamos é a de usar ***Cross Validation*** em todos os métodos nos quais ele for passível. O objetivo é que consigamos analisar o desempenho dos modelos que iremos treinar sem precisar separar uma parte para teste e uma para treino, uma vez que a quantidade de amostras é limitada.

Dito isso, os métodos que iremos treinar, assim como a justificativa para tomarmos tais decisões, são:


* **Árvore de decisão -** Como estamos lidando com dados de saúde, muitas vezes algumas condições de saúde estão mais relacionadas a ocorrência de uma certa doença do que outras. Por exemplo, no nosso caso, estamos tentando identificar se um paciente ao chegar com dor no peito no hospital está infartando ou não. Apesar de poder ocorrer em pessoas saudáveis, é de conhecimento geral que pessoas com pressão alta, taxas de colesterol elevadas e etc são mais sucetíveis a infartarem. Desse modo, nossa ideia é que a árvore de decisão se beneficiará de tais fatos para conseguir "montar seus galhos" de forma mais precisa. Como nosso dataset é pequeno, gostariamos de explorar uma **Random Forest** também caso o desempenho da árvore se mostre promissor.
* **Logistic Regression -** Apesar de ser um método mais simples, ele lida bem com um dataset mais reduzido e é conhecido por ter bons resultados quando trata-se de classificar de forma binária, que é o nosso caso, pois ou o paciente tem uma doença cardiovascular ou ele não tem. Assim , é um método que vale a pena ser testado pois tem um indicativo de bons resultados.
* **SVM -** Apesar de não ser o primeiro método pensado para o nosso caso, após analisarmos a distribuição dos dados nos plots, principalmente na parte 3D, ponderamos sobre a possibilidade de talvez esse método ser capaz de separar as nossas duas classes visto que, aparentemente, uma delas se encontra mais a esquerda e mais aglomerada que a outra. Isso é apenas uma suposição, mas devido a pequena quantidade de amostras, decidimos investigar também essa possibilidade.



Vale ressaltar que apesar da **Árvore de Decisão** não precisa de normalização ou padronização dos dados devido ao funcionamento dos métodos, para o **SVM** e o **Logistic Regression** optamos por realizar a normalização dos dados, pois são métodos sensíveis a amplitude dos valores. Como alguns dados do nosso dataset estão em proporções muito maiores que os demais, a normalização fez-se necessária. A escolha da normalização ao invés da padronização se deve ao fato de **NÃO** tratarmos outliers. Estamos nos baseando no fato de que são todos os dados reais, e de que se já chegaram pacientes com esse estado clínico então nosso modelo precisa ser capaz de lidar com esses "outliers" que de fato ocorrem. Como a normalização é mais indicada para lidar com *supostos outliers*, nós a escolhemos.

Por último, caso o desempenho dos métodos escolhidos não seja satisfatório, vamos tentar criar um ensemble com os três métodos escolhidos ou com que tiver o melhor desempenho. Avaliaremos essa possibilidade após o treino e avaliação dos nossos primeiros modelos.
"""

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, balanced_accuracy_score

def showEstimatorMetrics(y, y_pred):

    cm = confusion_matrix(y, y_pred)
    cm = cm / len(y)
    cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels = ["Normal", "Cad"])
    cm_display.plot()

    print(f"Acuracia: {100 * accuracy_score(y, y_pred):.2f}%")
    print(f"Acuracia Balanceada: {100 * balanced_accuracy_score(y, y_pred):.2f}%")
    print(f"Precision: {100 * precision_score(y, y_pred):.2f}%")
    print(f"Recall: {100 * recall_score(y, y_pred):.2f}%")
    print(f"F1-score: {100 * f1_score(y, y_pred):.2f}%")

"""### Árvore de Decisão"""

from sklearn.tree import DecisionTreeClassifier

"""Como o nosso dataset é reduzido, decidimos fazer uma busca exaustiva em busca do melhor parâmetro para a altura da árvore usado o **GridSearch**."""

# Definindo parametros para o GridSearch
grid_params = {
    'max_depth': [None, 2, 4, 6, 8, 10],
    'random_state' : [47]
}

# Declarando o modelo
tree_clf = DecisionTreeClassifier()

# Treinando com os parâmetros. Lembra-se que o cross validation está sendo realizado
# internamente no GridSearch usando o Cross Validation estratificado
grid = GridSearchCV(tree_clf, grid_params, cv=10)
grid.fit(X, Y)

best_params = grid.best_params_
best_score = grid.best_score_

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor acurácia no cross-validation: {best_score}")

# Redeclarando o modelo com os parâmetros escolhidos
tree_clf = DecisionTreeClassifier(max_depth=6, random_state=47)

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(tree_clf, X, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""Analisando as métricas e a consequente matriz de confusão já percebemos um problema óbvio no nosso modelo, que é a quantidade alta de falsos negativos para CAD. Em certa de 10% dos casos, o modelo prediz que a pessoa está *saudável* quando, na verdade, ela tem sim uma *doença cardiovascular*. Esse é um número bem ruim se formos interpretar ele como **1 a cada 10 pacientes que apresentam uma doença cardíaca são mandados de volta para casa sem tratamento**. Isso pode se tornar algo como *1 a cada 10 pacientes com doenças cardiovasculares morrem por falta de tratamento* , o que tem um peso muito maior.

Portanto, precisamos avaliar novos métodos e buscar formas de aumentar o valor do *Recall*, diminuindo assim o nosso número de falsos negativos.

Vamos refazer o nosso treinamento modificando o peso da classe CAD. Nossa esperança é diminuir o número de falsos negativos. Todavia, uma possível consequência é a diminuir o *Precision* do modelo.
"""

# Definindo parametros para o GridSearch
grid_params = {
    'class_weight' : [{0:1, 1:1}, {0:1, 1:2}, {0:1, 1:3}, {0:1, 1:4}, {0:1, 1:5}, {0:1, 1:6}, {0:1, 1:7}, {0:1, 1:8}, {0:1, 1:9}, {0:1, 1:10}],
}

# Declarando o modelo
tree_clf = DecisionTreeClassifier(max_depth=6, random_state=47)

# Treinando com os parâmetros. Lembra-se que o cross validation está sendo realizado
# internamente no GridSearch usando o Cross Validation estratificado
grid = GridSearchCV(tree_clf, grid_params, cv=10, scoring='recall')
grid.fit(X, Y)

best_params = grid.best_params_
best_score = grid.best_score_

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor recall no cross-validation: {best_score}")

# Redeclarando o modelo com os parâmetros escolhidos
tree_clf = DecisionTreeClassifier(max_depth=6, random_state=47, class_weight={0:1, 1:10})

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(tree_clf, X, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""Aumentando o peso da classe **CAD**, conseguimos aumentar o *Recall*, ou seja, diminuimos o nosso número de falsos negativos. Mas, ainda assim, o nosso número de falsos negativos é relativamente alto, sendo cerca de 7% das amostras. Além disso, o *Precision* e a acurácia do modelo cairam de forma significativa, o que é um indicativo que estamos indo para o caminho errado.

Com base nisso, nossa última tentativa com **Árvore de Decisão** será treinar uma **Random Forest** e avaliar se o *Recall* para esse modelo possui melhores resultados do que os obtidos até agora.
"""

from sklearn.tree import export_graphviz
import graphviz
from google.colab import files

tree_clf.fit(X, Y)
dot_data = export_graphviz(tree_clf, out_file=None,
                           feature_names=X.columns,
#                           class_names=iris.target_names,
                           filled=True, rounded=True,
                           special_characters=True)
graph = graphviz.Source(dot_data)
graph.render("decision_tree")  # Salva a árvore em um arquivo
graph.view()  # Abre uma visualização da árvore
files.download("decision_tree.pdf")

"""#### Random Forest"""

from sklearn.ensemble import RandomForestClassifier

# Declarando o modelo com os parâmetros escolhidos anteriormente
# Vou deixar o padrão de 100 árvores
rand_forest_clf = RandomForestClassifier(max_depth=6, random_state=47, class_weight={0:1, 1:10})

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(rand_forest_clf, X, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""O modelo treinado com **Random Forest** para os parâmetros anteriormente avaliados possui um *Recall* excelente. Todavia, o custo disso é uma baixa acurácia e *Precision*. Além disso, como no nosso dataset as duas classes não são bem distribuídas e a classe desejada tem um maior número de amostras, além de termos dado um maior peso para a mesma, percebemos pela matriz de confusão que o que o nosso modelo está tentando fazer é estimar quase sempre para a classe **CAD**, o que por si só já garante uma acurácia elevada.

Contudo, sabemos que da forma que está nosso modelo não deve ser eficiente generalizando no mundo real. Então, o que vamos fazer é retreinar a **Random Forest** mas agora considerando o mesmo peso para as duas classes.
"""

# Declarando o modelo com os parâmetros escolhidos anteriormente
# Vou deixar o padrão de 100 árvores
rand_forest_clf = RandomForestClassifier(max_depth=6, random_state=47)

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(rand_forest_clf, X, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""O resultado agora foi muito melhor! O *Recall* continua com um valor elevado, mas o *Precision* e a acurácia aumentaram. Nosso modelo não está mais tendenciosamente estimando na classe majoritária. Isso é um ótimo indicativo.

Até o momento, uma **Random Forest** com *max_depth=6* e classes igualmente distribuídas possui o melhor resultado, com uma acurácia de 85.48% e recall de 94.44%.

### Logistic Regression
"""

from sklearn.linear_model import LogisticRegression

# Padronização dos dados
scaler = StandardScaler()
X_padr = scaler.fit_transform(X)

# Definindo parametros para o GridSearch
grid_params = {
    'class_weight' : [{0 : 1, 1 : 1}, {0 : 1, 1 : 2}, {0 : 1, 1 : 3}, {0 : 1, 1 : 4}, {0 : 1, 1 : 5}],
}

# Declarando o modelo
lr_clf = LogisticRegression(random_state=47)

# Treinando com os parâmetros. Lembra-se que o cross validation está sendo realizado
# internamente no GridSearch usando o Cross Validation estratificado
grid = GridSearchCV(lr_clf, grid_params, cv=10, scoring='f1')
grid.fit(X_padr, Y)

best_params = grid.best_params_
best_score = grid.best_score_

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor F1-score no cross-validation: {best_score}")

# Redeclarando o modelo com os parâmetros escolhidos
lr_clf = LogisticRegression(class_weight={0:1, 1:3}, random_state=47)

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(lr_clf, X_padr, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""Apesar do **Logistic Regression** ser um método recomendado para classificações binárias, para o nosso caso, onde o *Recall* era mais importante que a acurácia, o resultado obtido não foi superior aos demais métodos analisados. Além disso, a quantidade de falsos positivos para a classe **CAD** está elevada.

Outros métodos precisam ser analisados.

### SVM
"""

from sklearn.svm import SVC

"""O SVM é bem sensível ao range de valores dos dados, então para treinar esse modelo precisaremos antes normalizar os dados."""

# Padronização dos dados
scaler = StandardScaler()
X_padr = scaler.fit_transform(X)

"""Como o SVC possui muitos hiperparâmetros, vamos rodar um GridSearch em bsca dos melhores."""

# Definindo parametros para o GridSearch
grid_params = {
    'kernel' : ['linear', 'poly', 'rbf', 'sigmoid'],
}

# Declarando o modelo
svc_clf = SVC(random_state=47)

# Treinando com os parâmetros. Lembra-se que o cross validation está sendo realizado
# internamente no GridSearch usando o Cross Validation estratificado
grid = GridSearchCV(svc_clf, grid_params, cv=10, scoring='f1', refit=False)
grid.fit(X_padr, Y)

best_params = grid.best_params_
best_score = grid.best_score_

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor F1-score no cross-validation: {best_score}")

# Redeclarando o modelo com os parâmetros escolhidos
svc_clf = SVC(kernel='sigmoid', random_state=47)

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(svc_clf, X_padr, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""O método *Suport Vector Machine* com kernel *sigmoid* apresentou um resultado surpreendentemente bom. Atingiu uma média de 86% de acurácia e um *Recall* de 91%. Apesar de mais simples, o método se encaixou super bem no nosso dataset.

## Etapa 2 - Avaliações Finais e Conclusão

Dos três métodos que nos propormos a avaliar na etapa anterior, o **SVC** com *kernel sigmoid* e o **Random Forest** com *max_depth* = 6 e *random_state* = 47 obtiveram os melhores resultados, com acurácia de 86% e 85% e *recall* de 91% e 94%, respectivamente.

Apesar do *recall* estar aceitável, gostaríamos de um modelo que tivesse um *recall* acima de 90% e uma acurácia de pelo menos uns 88% também. Sabemos que dificilmente conseguiremos um classificador "perfeito", mas faremos uma última tentativa utilizando dois últimos métodos: **XGBClassifier** e um **ensemble de SVC**. Cada um foi escolhido pelos seguintes motivos:

* O **XGBClassifier** tem tido resultados muito promissores, principalmente nas competições do kaggle. De uns anos pra cá, todos os ganhadores têm usado esse método para treinar seus modelos. Como obtivemos resultados positivos com a Random Forest, essa método valia muito uma tentativa. O XGBClassifier se assemelha a uma Random Forest, mas utiliza a técnica de gradiente descendente para ir construindo suas próximas árvores com base no erro residual da anterior.

* O **SVC** obteve a melhor acurácia média dos dois métodos, mas o *recall* ainda ficou um pouco atrás que a Random Forest. Por esse motivo, acreditamos que valeria a pena tentar aplicar esse método num ensemble para observamos se seleção de diferentes conjuntos de teste melhorariam o desempenho do modelo. Nossa esperança é de que seja e até supere a Random Forest treinada anteriormente.

### XGBClassifier
"""

# Padronização dos dados
scaler = StandardScaler()
X_padr = scaler.fit_transform(X)

# Definindo parametros para o GridSearch
grid_params = {
    "n_estimators" : [2, 4, 6, 8, 10],
    "max_depth" : [2, 4, 6, 8, 10],
    "learning_rate" : [1, 2, 3],
    "objective" : ["binary:logistic"]
}

# Declarando o modelo
xgb_clf = xgb.XGBClassifier()

# Treinando com os parâmetros. Lembra-se que o cross validation está sendo realizado
# internamente no GridSearch usando o Cross Validation estratificado
grid = GridSearchCV(xgb_clf, grid_params, cv=10, scoring="recall", refit=False)
grid.fit(X_padr, Y)

best_params = grid.best_params_
best_score = grid.best_score_

print(f"Melhores parâmetros: {best_params}")
print(f"Melhor recall no cross-validation: {best_score}")

# Redeclarando o modelo com os parâmetros escolhidos
xgb_clf = xgb.XGBClassifier(learning_rate = 1, max_depth = 2, n_estimators = 6, objective = "binary:logistic")

# Especificando detalhes do cross validation
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(xgb_clf, X_padr, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""Os resultados obtidos não foram ruins, mas, com uma acurácia de 84% e um *recall* de 93%, o classificador XGBoost teve um desempenho bem semelhante ao Random Forest, não demonstrando nenhuma vantagem sobre esse, como era esperado. Como o *recall* da Random Forest foi levemente maior, ainda é preferível esta ao XGBoost.

### Ensemble SVM
"""

from sklearn.ensemble import BaggingClassifier
from sklearn.pipeline import Pipeline

# Declarando o modelo com os parâmetros escolhidos na Parte 2
svc_clf = SVC(kernel='sigmoid', random_state=74)

# Ensemble
bg_clf = BaggingClassifier(svc_clf, random_state=74)
# ab_clf = AdaBoostClassifier(svc_clf, random_state=47, algorithm='SAMME')

skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=47)

# Obtendo classes preditas
Y_pred = cross_val_predict(bg_clf, X_padr, Y, cv=skf)

# Mostrando resultado obtido
showEstimatorMetrics(Y, Y_pred)

"""| Método | Acurácia | Acurácia Balanceada | Precision | Recall | F1-score |
|--------|--------|--------|--------|--------|--------|
|Random Forest |  85.48% | 78.83% | 86.44% | 94.44% | 90.27%
|SVC | 86.14% | 82.38% | 89.55% | 91.20% | 90.37%
|XGBoost |  84.49% | 77.79% | 85.96% | 93.52% | 89.58%
|Ensemble SVC |  86.47% | 82.96% | 89.95% | 91.20% | 90.57%

Comparando os melhores resultados que obtivemos, em caso de colocar um modelo em produção, o que colocariamos seria o **Random Forest**. Nossa escolha foi baseada no melhor desempenho médio do modelo. A prioridade era garantir o maior *recall* possível, pois como estamos lidando com uma doença cardiovascular, devemos diminuir ao máximo a taxa de falsos negativos do nosso modelo. Assim, dos modelos treinados, o maior *recall* foi do método **Random Forest**. Apesar de não possuir o maior *precision*, pois possui uma taxa de 11% de falsos positivos enquanto outros métodos alcançaram 7.3%, a acurácia do método se aproxima bastante dos demais modelos treinados. Dessa forma, nos pareceu coerente escolher o modelo que nos entregasse o menor núemro de falsos negativos, visto a gravidade da natureza do problema, em detrimento de outras taxas como acurácia e *precision*.
"""