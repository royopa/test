# SCRIPT QUE APLICA O FILTRO DE KALMAN PARA RESOLU��O DO PROBLEMA PROPOSTO EM AREOSA (2008)

# SCRIPT CONSTRU�DO PARA SER UMA SUBROTINA DO SCRITP "SCRIPT_POTENTIAL_GDP.R"

# FILTRO NADA MAIS � DO QUE UM FILTRO HP COM RESTRI��O DA FUN��O DE PRODU��O
# STATE-SPACE MODEL:        y_t = F*Theta_t + v_t             vt ~ N(0,Vt)
#                           Theta_t = G*Theta_t(-1) + wt      wt ~ N(0,Wt)
# ONDE, 
# y_t = Vetor dos par�metros observ�veis: PIB, NUCI e Emprego (1-u)
# Theta_t = vetor de vari�veis n�o-observ�veis: PIB potencial, NUCI potencial e Emprego potencial (e auxiliares)
# F = Matriz da measurement equation: relaciona y_t com as vari�veis n�o observ�veis
# G = Matriz de transi��o: hip�teses de evolu��o dos par�metros n�o observ�veis

# Areosa coloca os mesmos erros nas duas equa��es

# LIBRARIES
library("readxl", lib.loc="~/R/win-library/3.5")
library("dlm", lib.loc="~/R/win-library/3.5")

# MODELO
alpha = 0.3 # income capital share
# par�metros da maximiza��o (filtro)
beta_y = 1
beta_e = 1
beta_c = 1
lambda_y = 1600
lambda_e = 1600
lambda_c = 1600
# Restri��o dos par�metros
par1 = (beta_y*lambda_y)/(beta_e*lambda_e) #sigma2 = par1*sigma5
par2 = (beta_y*lambda_y)/(beta_c*lambda_c) #sigma4 = par2*sigma5
par3 = (beta_c + beta_y*(alpha^2))/(beta_e + beta_y*((1-alpha)^2)) #sigma1 = par3*sigma3
par4 = - (beta_y*alpha*(1-alpha))/(beta_e + beta_y*((1-alpha)^2)) #sigma13 = par4*sigma3
par5 = (beta_y*lambda_y*(beta_e + beta_y*((1-alpha)^2)))/(beta_e*beta_c + 
                                                            beta_c*beta_y*((1-alpha)^2) + 
                                                            beta_e*beta_y*(alpha^2)) #sigma3  = par5*sigma5

# Explicitando vari�veis da fun��o dlm

# FF : Matriz 3xN , onde N � o numero de par�metros n�o observ�veis (n�o s�o s� 3 devido a montagem do modelo)
# GG : Matriz NxN que define a rela��o das observ�veis e as n�o observ�veis.
# V  : Matriz 3x3 onde as diagonais s�o as vari�ncias do vetor y, a serem estimadas.
# W  : Matriz (N-1)x(N-1), com as entradas diagonais sendo as vari�ncias das eq. de transi��o.
#      Ser�o estimadas. A matriz W � onde ser�o impostas as restri��es. N�o � diagonal.
# M0 : Vetor 3xN de priors para a m�dia dos Thetas
# C0 : Matriz NxN diagonal com priors para vari�ncia dos Thetas
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
  # Definindo as vari�ncias (a serem estimadas) e restri��es
  # Ponte entre o Vetor Sigma e os par�metros sigma (matriz de vari�ncia e covari�ncia dos erros)
  # sigma[1] = sigma5
  
  
  V = diag(3)
  V[1,1] = par3*par5*exp(sigma[1]) #sigma1 = par3*sigma3 = par3*par5*sigma5
  V[2,2] = par5*exp(sigma[1])  #sigma3 = par5*sigma5
  V[3,3] = ((1-alpha)^2)*V[1,1] + (alpha^2)*V[2,2]
  V[1,3] = (1-alpha)*V[1,1] + alpha*par4*par5*exp(sigma[1]) #Derivando a covari�ncia, segundo termo � o sigma13
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

fit.kalman = dlmFilter(y, mod = modeldlm(MLEestim$par)) #filtro de kalman para estimar os n�o-obs
#S�ries estimadas est�o em m

En = exp(fit.kalman$m[,1]) #emprego potencial
Cn = exp(fit.kalman$m[,3]) #nuci potencial
Yn = exp(fit.kalman$m[,5]) #pib potencial
