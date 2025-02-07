# -*- coding: utf-8 -*-
"""rede_neural_do_zero.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MSz2rePeZPIibDwm3U2j6KFVCoybaW_M

Rede neural para o reconhecimento de numeros escritos a mão. Serve para identificar os numeros devido a cada caligrafia ter oseu estilo dificultando o seu reconhecimento.
"""

import numpy as np
import torch #framework de progamação, ele disse
import torch.nn.functional as F #funçoes
import torchvision #biblioteca visão cumputacional
import matplotlib.pyplot as plt
from time import time #para colocar o tempo de execução, tem que chamar dessa forma ?!
from torchvision import datasets, transforms
from torch import nn, optim

"""Agora vai chamar e transformar o dataset de imagens ❗"""

transform = transforms.ToTensor()  # definindo a conversão de imagem para tensor

trainset = datasets.MNIST('./MNIST_data/', download=True, train=True, transform=transform)  # Carrega a parte de treino do dataset
trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True, num_workers=4)
#trainloader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)  # Cria um buffer para pegar os dados por partes

valset = datasets.MNIST('./MNIST_data/', download=True, train=False, transform=transform)  # Carrega a parte de validação do dataset
valloader = torch.utils.data.DataLoader(valset, batch_size=64, shuffle=True)  # Cria um buffer para pegar os dados por partes

"""O carregamento do dataset MNIST foi concluído com sucesso. O script conseguiu contornar o erro 403 Forbidden usando um mirror alternativo e baixou e extraiu todos os arquivos necessários. Você pode prosseguir com seu projeto usando o dataset MNIST."""

#dataiter = iter(trainloader)
#imagens, etiquetas = dataiter.next() NÃO DEU CERTO DESSE JEITO POR CONTA DO NEXT()
#plt.inshow(imagens[0].numpy().squeeze(), cmap='gray_r');

for imagens, etiquetas in trainloader:
    # Acesse o lote de imagens e rótulos aqui
    plt.imshow(imagens[0].numpy().squeeze(), cmap='gray_r')
    break  # Remova esta linha se quiser processar todos os lotes

print(imagens[0].shape) #para verificar as dimensões do tensor de cada imagem
print(etiquetas[0].shape) #para verificar as dimensões do tensor de cada etiqueta

"""O modelo da rede você enconta em keras application, nesse caso foi usado inceptionV3. Não sei de onde vem o codigo definido mas é respectivo ao inceptionV3."""

class Modelo(nn.Module):
    def __init__(self):
        super(Modelo, self).__init__()
        self.linear1 = nn.Linear(784, 128)  # camada de entrada, 784 neurônios que se ligam a 128
        self.linear2 = nn.Linear(128, 64)  # camada interna 1, 128 neurônios que se ligam a 64
        self.linear3 = nn.Linear(64, 10)  # camada interna 2, 64 neurônios que se ligam a 10
        # para a camada de saída não é necessário definir nada pois só precisamos pegar o output da camada interna 2

    def forward(self, x):
        x = F.relu(self.linear1(x))  # função de ativação da camada de entrada para a camada interna 1
        x = F.relu(self.linear2(x))  # função de ativação da camada interna 1 para a camada interna 2
        x = self.linear3(x)  # função de ativação da camada interna 2 para a camada de saída, nesse caso f(x) = x
        return F.log_softmax(x, dim=1)  # dados utilizados para calcular a perda

def treino(modelo, trainloader, device):

    otimizador = optim.SGD(modelo.parameters(), lr=0.01, momentum=0.5)  # define a política de atualização dos pesos e da bias
    inicio = time()  # timer para sabermos quanto tempo levou o treino

    criterio = nn.NLLLoss()  # definindo o critério para calcular a perda
    EPOCHS = 10  # numero de epochs que o algoritmo rodará
    modelo.train()  # ativando o modo de treinamento do modelo

    for epoch in range(EPOCHS):
        perda_acumulada = 0  # inicialização da perda acumulada da epoch em questão

        for imagens, etiquetas in trainloader:

            imagens = imagens.view(imagens.shape[0], -1)  # convertendo as imagens para "vetores" de 28*28 casas para ficar compatível com o modelo
            otimizador.zero_grad()  # zerando os gradientes por conta do ciclo anterior

            output = modelo(imagens.to(device))  # colocando os dados no modelo
            perda_instantanea = criterio(output, etiquetas.to(device)) #calculando a perda da epoch em questão

            #etiquetas = etiquetas.to(device)
            #perda_instantânea = criterio(output, etiquetas)  # calculando a perda da epoch em questão
            perda_instantanea.backward()  # back propagation a partir da perda

            otimizador.step()  # atualizando os pesos e a bias

            perda_acumulada += perda_instantanea.item()  # atualização da perda acumulada

        else:
            print("Epoch {} - Perda resultante: {}".format(epoch+1, perda_acumulada/len(trainloader)))
    print("\nTempo de treino (em minutos) =", (time()-inicio)/60)

def validacao(modelo, valloader, device): #Modelo de validação!!!!!
    conta_corretas, conta_todas = 0, 0
    for imagens, etiquetas in valloader:
        for i in range(len(etiquetas)):
            img = imagens[i].view(1, 784)

            # desativar o autograd para acelerar a validação. Grafos computacionais dinâmicos têm um custo alto de processamento
            with torch.no_grad():
                logps = modelo(img.to(device))  # output do modelo em escala logarítmica

            ps = torch.exp(logps)  # converte output para escala normal(lembrando que é um tensor)
            probab = list(ps.cpu().numpy()[0])
            etiqueta_pred = probab.index(max(probab))  # converte o tensor em um número, no caso, o número que o modelo previu
            etiqueta_certa = etiquetas.numpy()[i]
            if(etiqueta_certa == etiqueta_pred):  # compara a previsão com o valor correto
                conta_corretas += 1
            conta_todas += 1

    print("Total de imagens testadas = ", conta_todas)
    print("\nPrecisão do modelo = {}%".format(conta_corretas*100/conta_todas))

modelo = Modelo()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') #verificação se tem cuda na gpu, se não vai rodar com cpu. nem todos os pcs tem cuda
modelo.to(device)

