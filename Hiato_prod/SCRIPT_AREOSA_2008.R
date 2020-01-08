# SCRIPT QUE APLICA O FILTRO DE KALMAN PARA RESOLUÇÃO DO PROBLEMA PROPOSTO EM AREOSA (2008)

# SCRIPT CONSTRUÍDO PARA SER UMA SUBROTINA DO SCRITP "SCRIPT_POTENTIAL_GDP.R"

# FILTRO NADA MAIS É DO QUE UM FILTRO HP COM RESTRIÇÃO DA FUNÇÃO DE PRODUÇÃO
# STATE-SPACE MODEL:        y_t = F*Theta_t + v_t             vt ~ N(0,Vt)
#                           Theta_t = G*Theta_t(-1) + wt      wt ~ N(0,Wt)
# ONDE, 
# y_t = Vetor dos parâmetros observáveis: PIB, NUCI e Emprego (1-u)
# Theta_t = vetor de variáveis não-observáveis: PIB potencial, NUCI potencial e Emprego potencial (e auxiliares)
# F = Matriz da measurement equation: relaciona y_t com as variáveis não observáveis
# G = Matriz de transição: hipóteses de evolução dos parâmetros não observáveis

# Areosa coloca os mesmos erros nas duas equações

# LIBRARIES
library("readxl", lib.loc="~/R/win-library/3.5")
library("dlm", lib.loc="~/R/win-library/3.5")

# MODELO
alpha = 0.3 # income capital share
# parâmetros da maximização (filtro)
beta_y = 1
beta_e = 1
beta_c = 1
lambda_y = 1600
lambda_e = 1600
lambda_c = 1600
# Restrição dos parâmetros
par1 = (beta_y*lambda_y)/(beta_e*lambda_e) #sigma2 = par1*sigma5
par2 = (beta_y*lambda_y)/(beta_c*lambda_c) #sigma4 = par2*sigma5
par3 = (beta_c + beta_y*(alpha^2))/(beta_e + beta_y*((1-alpha)^2)) #sigma1 = par3*sigma3
par4 = - (beta_y*alpha*(1-alpha))/(beta_e + beta_y*((1-alpha)^2)) #sigma13 = par4*sigma3
par5 = (beta_y*lambda_y*(beta_e + beta_y*((1-alpha)^2)))/(beta_e*beta_c + 
                                                            beta_c*beta_y*((1-alpha)^2) + 
                                                            beta_e*beta_y*(alpha^2)) #sigma3  = par5*sigma5

# Explicitando variáveis da função dlm

# FF : Matriz 3xN , onde N é o numero de parâmetros não observáveis (não são só 3 devido a montagem do modelo)
# GG : Matriz NxN que define a relação das observáveis e as não observáveis.
# V  : Matriz 3x3 onde as diagonais são as variâncias do vetor y, a serem estimadas.
# W  : Matriz (N-1)x(N-1), com as entradas diagonais sendo as variâncias das eq. de transição.
#      Serão estimadas. A matriz W é onde serão impostas as restrições. Não é diagonal.
# M0 : Vetor 3xN de priors para a média dos Thetas
# C0 : Matriz NxN diagonal com priors para variância dos Thetas
N = 6 #definindo N de acordo com a montagem do modelo

modeldlm = function(sigma){
  FF = matrix(0,nrow = 3,ncol = N)
  FF[1,1] = 1
  FF[2,3] = 1
  FF[3,5] = 1
  GG = matrix(0 , nrow = N , ncol = N)
  GG[1,1] = 2
  GG[1,2] = -1
  GG[2,1] = 1
  GG[3,3] = 2
  GG[3,4] = -1
  GG[4,3] = 1
  GG[5,5] = 2
  GG[5,6] = -1
  GG[6,5] = 1
  # Definindo as variâncias (a serem estimadas) e restrições
  # Ponte entre o Vetor Sigma e os parâmetros sigma (matriz de variância e covariância dos erros)
  # sigma[1] = sigma5
  
  
  V = diag(3)
  V[1,1] = par3*par5*exp(sigma[1]) #sigma1 = par3*sigma3 = par3*par5*sigma5
  V[2,2] = par5*exp(sigma[1])  #sigma3 = par5*sigma5
  V[3,3] = ((1-alpha)^2)*V[1,1] + (alpha^2)*V[2,2]
  V[1,3] = (1-alpha)*V[1,1] + alpha*par4*par5*exp(sigma[1]) #Derivando a covariância, segundo termo é o sigma13
  V[3,1] = V[1,3]
  V[2,3] = alpha*V[2,2] + (1-alpha)*par4*par5*exp(sigma[1])
  V[3,2] = V[2,3]
  
  
  W = diag(N)
  W[1,1] = par1*exp(sigma[1]) #sigma2 = par1*sigma5
  W[2,2] = 0
  W[3,3] = par2*exp(sigma[1]) #sigma4 = par2*sigma5
  W[4,4] = 0
  W[5,5] = exp(sigma[1]) #sigma5
  W[6,6] = 0
  
  m0 = c(rep(0,N)) #guess inicial
  C0 = 100*diag(N)
  
  model_aux = dlm(FF = FF, GG = GG, V = V, W = W, m0 = m0, C0 = C0)
  return(model_aux)
  
}

MLEestim = dlmMLE(y, parm = 1, build = modeldlm)

fit.kalman = dlmFilter(y, mod = modeldlm(MLEestim$par)) #filtro de kalman para estimar os não-obs
#Séries estimadas estão em m

En = exp(fit.kalman$m[,1]) #emprego potencial
Cn = exp(fit.kalman$m[,3]) #nuci potencial
Yn = exp(fit.kalman$m[,5]) #pib potencial
