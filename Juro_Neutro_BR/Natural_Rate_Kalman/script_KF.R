#ESTIMAÇÃO DOS MODELOS MQO E TVP COM OS ÚLTIMOS DADOS (PARA PROJEÇÃO)
library("readxl")
library("xts")
library("seasonal")
library("mFilter")
library("uroot")
library("ggplot2")
library("reshape2")
library("dlm")
library("openxlsx")
library(dplyr)

# Lendo a Base de Dados
data_quarterly <- read_excel("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/HLW_Code/inputData/rstar.data.br.xls") %>% as.data.frame #Base de dados trimestral
setwd("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR")
############################DATA FINAL DOS DADOS##############################

crt_year = 2018 #Ano final dos dados
crt_mth = 3 # Trimestre final dos dados

########################Base de dados transformada############################
#Dados convertidas em séries de tempo
#Inflação
inflation = ts(data_quarterly$inflation, start = c(2003,1), end = c(crt_year,crt_mth), frequency=4)
#Focus
expec     = ts(data_quarterly$exp_inf,   start = c(2003,1), end = c(crt_year,crt_mth), frequency=4)
mt     <- c(4, 4, 4, 4, 5.5, 5.5, 5.5, 5.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 
            4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 
            4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 
            4.5, 4.5, 4.5, 4.5, 4.5)
mt     = ts(mt,   start = c(2003,1), end = c(crt_year,crt_mth), frequency=4)
#selic 
selic     = ts(data_quarterly$interest,  start = c(2003,1), end = c(crt_year,crt_mth), frequency=4)
#PIB
pib       = ts(data_quarterly$gdp.log,   start = c(2003,1), end = c(crt_year,crt_mth), frequency=4)


gap_pib    = hpfilter(ts(data_quarterly$gdp.log, start=c(2003,1), end=c(crt_year,crt_mth), frequency=4))$cycle
gap_inf    = inflation - mt

#MQOs
#Livres com PIM, Desemp e CRB em R$
aux_dat1 = na.omit(cbind(selic, inflation, Lag(selic,k=1), gap_pib, gap_inf))
mqo1 = lm(aux_dat1[,1] ~ -1 + ts(seasonal.dummies(aux_dat1[,1]),start=(start(aux_dat1[,1])),end =end(aux_dat1[,1]),frequency=4)   
          + aux_dat1[,2] + aux_dat1[,3] + aux_dat1[,4] + aux_dat1[,5])


######################Modelos para achar TVP por MV e Kalman Filter#######################

#Modelo para achar TVP por MV e Kalman Filter

#Defining model


# y_t = Theta_t*F_t + v_t
# Theta_t = Theta_t(-1) + w_t

# y_t : Inflação
# Theta_t : Parametros
# F_t : Covariadas

#Definindo parametros com os dados

# Explicitando variáveis da função dlm

# FF : Vetor 1xN , onde N é o numero de regressores. A primeira entrada deverá ser 1 (intercepto)
#      As entradas seguintes poderão ser iguais a 1, mas serão substituídas pelos regressores
#      variantes no tempo
# GG : Matriz identidade NxN (pois estamos supondo que os Thetas seguem Random Walk)
# V  : variância de y, invariante no tempo. Será uma incógnita a ser estimada por MV
# W  : Matriz NxN diagonal, com as entradas diagonais sendo as variâncias das eq. de transição.
#      Serão incógnitas
# JFF: Vetor 1xN, onde a primeira entrada é igual a 0 (intercepto invariável) e as outras serão
#      iguais a k, onde k é a coluna referente na matriz X (olhar abaixo)
# X  : matriz tx(N-1), com as colunas contendo os regressores (variantes no tempo)
# M0 : Vetor 1xN de priors para a média dos Thetas
# C0 : Matriz NxN diagonal com priors para variância dos Thetas


########################### PIM, Desemp e CRB em R$ ##################################

#Criando a matriz X (regressores variantes no tempo)
x1 = cbind(1, aux_dat1[,2], aux_dat1[,3], aux_dat1[,4], aux_dat1[,5])
N1 = ncol(x1)#parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM1 <- function(sigma) {
  FF = matrix(c(rep(1,N1)) , nrow = 1 , ncol = N1) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N1)
  V = exp(sigma[1])
  W = diag(N1)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = 10^(-10); #exp(sigma[3])
  W[3,3] = 10^(-10); #exp(sigma[4])
  W[4,4] = 10^(-10); #exp(sigma[5])
  #W[5,5] = exp(sigma[6])
  #W[6,6] = exp(sigma[7])
  #W[7,7] = exp(sigma[8])
  #W[8,8] = exp(sigma[9])
  JFF = matrix(c(seq(from=1,to=N1,by=1)) , nrow = 1 , ncol = N1)#tem que ser matriz
  m0 = c(rep(0,N1)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N1 , ncol = N1)
  diag(C0) = 1
  
  myModel1 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x1)
  return(myModel1)
}

MLEstim1 <- dlmMLE(aux_dat1[,1] , parm = c(1, 1) , build = ModelDLM1,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE1 <- ModelDLM1(MLEstim1$par) #Modelo com as variâncias estimadas

fit.kalman1 <- dlmFilter(aux_dat1[,1] , dlmInflMLE1) #Filtro de Kalman. Parâmetros estimados em m
fit.kalman2 <- dlmSmooth(aux_dat1[,1] , dlmInflMLE1) #Filtro de Kalman. Parâmetros estimados em m

###########################Desemp CRB##################################

#Criando a matriz X (regressores variantes no tempo)
x2 = cbind(aux_dat2[,2],aux_dat2[,3],aux_dat2[,4],ts(seasonal.dummies(aux_dat2[,1]),start=(start(aux_dat2[,1])),end =end(aux_dat2[,1]),frequency=4))
N2 = ncol(x2) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM2 <- function(sigma) {
  FF = matrix(c(rep(1,N2)) , nrow = 1 , ncol = N2) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N2)
  V = exp(sigma[1])
  W = diag(N2)
  W[1,1] = exp(sigma[2])
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  JFF = matrix(c(seq(from=1,to=N2,by=1)) , nrow = 1 , ncol = N2) #tem que ser matriz
  m0 = c(rep(0,N2)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N2 , ncol = N2)
  diag(C0) = 100
  
  myModel2 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x2)
  return(myModel2)
}

MLEstim2 <- dlmMLE(aux_dat2[,1] , parm = c(1,1,1,1,1,1,1,1) , build = ModelDLM2,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE2 <- ModelDLM2(MLEstim2$par) #Modelo com as variâncias estimadas

fit.kalman2 <- dlmFilter(aux_dat2[,1] , dlmInflMLE2) #Filtro de Kalman. Parâmetros estimados em m

###########################PIM, Desemp, Cambio e IPA##################################

#Criando a matriz X (regressores variantes no tempo)
x3 = cbind(aux_dat3[,2],aux_dat3[,3],aux_dat3[,4],aux_dat3[,5],aux_dat3[,6],ts(seasonal.dummies(aux_dat3[,1]),start=(start(aux_dat3[,1])),end =end(aux_dat3[,1]),frequency=4))
N3 = ncol(x3) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM3 <- function(sigma) {
  FF = matrix(c(rep(1,N3)) , nrow = 1 , ncol = N3) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N3)
  V = exp(sigma[1])
  W = diag(N3)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  W[9,9] = exp(sigma[10])
  JFF = matrix(c(seq(from=1,to=N3,by=1)) , nrow = 1 , ncol = N3) #tem que ser matriz
  m0 = c(rep(0,N3)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N3 , ncol = N3)
  diag(C0) = 100
  
  myModel3 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x3)
  return(myModel3)
}

MLEstim3 <- dlmMLE(aux_dat3[,1] , parm = c(1,1,1,1,1,1,1,1,1,1) , build = ModelDLM3,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE3 <- ModelDLM3(MLEstim3$par) #Modelo com as variâncias estimadas

fit.kalman3 <- dlmFilter(aux_dat3[,1] , dlmInflMLE3) #Filtro de Kalman. Parâmetros estimados em m


#########################PIM, Desemp, Cambio, IPA e Temperatura################################

#Criando a matriz X (regressores variantes no tempo)
x4 = cbind(aux_dat4[,2],aux_dat4[,3],aux_dat4[,4],aux_dat4[,5],aux_dat4[,6],aux_dat4[,7],ts(seasonal.dummies(aux_dat4[,1]),start=(start(aux_dat4[,1])),end =end(aux_dat4[,1]),frequency=4))
N4 = ncol(x4) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM4 <- function(sigma) {
  FF = matrix(c(rep(1,N4)) , nrow = 1 , ncol = N4) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N4)
  V = exp(sigma[1])
  W = diag(N4)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  W[9,9] = exp(sigma[10])
  W[10,10] = exp(sigma[11])
  JFF = matrix(c(seq(from=1,to=N4,by=1)) , nrow = 1 , ncol = N4) #tem que ser matriz
  m0 = c(rep(0,N4)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N4 , ncol = N4)
  diag(C0) = 100
  
  myModel4 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x4)
  return(myModel4)
}

MLEstim4 <- dlmMLE(aux_dat4[,1] , parm = c(1,1,1,1,1,1,1,1,1,1,1) , build = ModelDLM4,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE4 <- ModelDLM4(MLEstim4$par) #Modelo com as variâncias estimadas

fit.kalman4 <- dlmFilter(aux_dat4[,1] , dlmInflMLE4) #Filtro de Kalman. Parâmetros estimados em m


#######################Desemp, Cambio, IPA e Temperatura#################################

#Criando a matriz X (regressores variantes no tempo)
x5 = cbind(aux_dat5[,2],aux_dat5[,3],aux_dat5[,4],aux_dat5[,5],aux_dat5[,6],ts(seasonal.dummies(aux_dat5[,1]),start=(start(aux_dat5[,1])),end =end(aux_dat5[,1]),frequency=4))
N5 = ncol(x5) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM5 <- function(sigma) {
  FF = matrix(c(rep(1,N5)) , nrow = 1 , ncol = N5) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N5)
  V = exp(sigma[1])
  W = diag(N5)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  W[9,9] = exp(sigma[10])
  JFF = matrix(c(seq(from=1,to=N5,by=1)) , nrow = 1 , ncol = N5) #tem que ser matriz
  m0 = c(rep(0,N5)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N5 , ncol = N5)
  diag(C0) = 100
  
  myModel5 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x5)
  return(myModel5)
}

MLEstim5 <- dlmMLE(aux_dat5[,1] , parm = c(1,1,1,1,1,1,1,1,1,1) , build = ModelDLM5,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE5 <- ModelDLM5(MLEstim5$par) #Modelo com as variâncias estimadas

fit.kalman5 <- dlmFilter(aux_dat5[,1] , dlmInflMLE5) #Filtro de Kalman. Parâmetros estimados em m


###########################Desemp, Cambio e Temperatura##################################

#Criando a matriz X (regressores variantes no tempo)
x6 = cbind(aux_dat6[,2],aux_dat6[,3],aux_dat6[,4],aux_dat6[,5],ts(seasonal.dummies(aux_dat6[,1]),start=(start(aux_dat6[,1])),end =end(aux_dat6[,1]),frequency=4))
N6 = ncol(x6) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM6 <- function(sigma) {
  FF = matrix(c(rep(1,N6)) , nrow = 1 , ncol = N6) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N6)
  V = exp(sigma[1])
  W = diag(N6)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  JFF = matrix(c(seq(from=1,to=N6,by=1)) , nrow = 1 , ncol = N6) #tem que ser matriz
  m0 = c(rep(0,N6)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N6 , ncol = N6)
  diag(C0) = 100
  
  myModel6 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x6)
  return(myModel6)
}

MLEstim6 <- dlmMLE(aux_dat6[,1] , parm = c(1,1,1,1,1,1,1,1,1,1) , build = ModelDLM6,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE6 <- ModelDLM6(MLEstim6$par) #Modelo com as variâncias estimadas

fit.kalman6 <- dlmFilter(aux_dat6[,1] , dlmInflMLE6) #Filtro de Kalman. Parâmetros estimados em m


###########################Desemp, CRB e Expectativas trimestrais##################################

#Criando a matriz X (regressores variantes no tempo)
x7 = cbind(aux_dat7[,2],aux_dat7[,3],aux_dat7[,4],aux_dat7[,5],ts(seasonal.dummies(aux_dat7[,1]),start=(start(aux_dat7[,1])),end =end(aux_dat7[,1]),frequency=4))
N7 = ncol(x7) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM7 <- function(sigma) {
  FF = matrix(c(rep(1,N7)) , nrow = 1 , ncol = N7) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N7)
  V = exp(sigma[1])
  W = diag(N7)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  JFF = matrix(c(seq(from=1,to=N7,by=1)) , nrow = 1 , ncol = N7) #tem que ser matriz
  m0 = c(rep(0,N7)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N7 , ncol = N7)
  diag(C0) = 100
  
  myModel7 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x7)
  return(myModel7)
}

MLEstim7 <- dlmMLE(aux_dat7[,1] , parm = c(0,0,0,0,0,0,0,0,0) , build = ModelDLM7,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE7 <- ModelDLM7(MLEstim7$par) #Modelo com as variâncias estimadas

fit.kalman7 <- dlmFilter(aux_dat7[,1] , dlmInflMLE7) #Filtro de Kalman. Parâmetros estimados em m



###########################Desemp, CRB e Expectativas 12m##################################

#Criando a matriz X (regressores variantes no tempo)
x8 = cbind(aux_dat8[,2],aux_dat8[,3],aux_dat8[,4],aux_dat8[,5],ts(seasonal.dummies(aux_dat8[,1]),start=(start(aux_dat8[,1])),end =end(aux_dat8[,1]),frequency=4))
N8 = ncol(x8) #parâmetros
# Vou deixar todos os componentes variarem no tempo
# Definindo
ModelDLM8 <- function(sigma) {
  FF = matrix(c(rep(1,N8)) , nrow = 1 , ncol = N8) #tem que ser matriz (apesar de 1 linha)
  GG = diag(N8)
  V = exp(sigma[1])
  W = diag(N8)
  W[1,1] = exp(sigma[2]) 
  W[2,2] = exp(sigma[3])
  W[3,3] = exp(sigma[4])
  W[4,4] = exp(sigma[5])
  W[5,5] = exp(sigma[6])
  W[6,6] = exp(sigma[7])
  W[7,7] = exp(sigma[8])
  W[8,8] = exp(sigma[9])
  JFF = matrix(c(seq(from=1,to=N8,by=1)) , nrow = 1 , ncol = N8) #tem que ser matriz
  m0 = c(rep(0,N8)) #tem que ser vetor (não matriz, mesmo que com uma linha)
  C0 = matrix(0 , nrow = N8 , ncol = N8)
  diag(C0) = 100
  
  myModel8 = dlm(FF = FF , GG = GG , V = V , W = W , m0 = m0 , C0 = C0 , JFF = JFF , X = x8)
  return(myModel8)
}

MLEstim8 <- dlmMLE(aux_dat8[,1] , parm = c(1,1,1,1,1,1,1,1,1,1) , build = ModelDLM8,method = "Nelder-Mead")

#Nesse ponto temos as variâncias já estimadas por MLE

dlmInflMLE8 <- ModelDLM8(MLEstim8$par) #Modelo com as variâncias estimadas

fit.kalman8 <- dlmFilter(aux_dat8[,1] , dlmInflMLE8) #Filtro de Kalman. Parâmetros estimados em m






############################SALVANDO ÚLTIMOS COEFICIENTES#####################################

# MQO1 PDC
assign(paste("Coef TVP1 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP1 PIM",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP1 CRB",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP1 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP1 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP1 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP1 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP1 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman1$m[which(index(fit.kalman1$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )

#MQO2 DC
assign(paste("Coef TVP2 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP2 CRB",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP2 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP2 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP2 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP2 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP2 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman2$m[which(index(fit.kalman2$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )

#MQO3 PDCaI
assign(paste("Coef TVP3 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP3 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP3 PIM",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP3 FX",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP3 IPA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP3 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP3 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP3 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )
assign(paste("Coef TVP3 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman3$m[which(index(fit.kalman3$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),9] )

#MQO4 PDCaIT
assign(paste("Coef TVP4 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP4 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP4 PIM",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP4 FX",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP4 IPA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP4 ONI",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP4 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP4 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )
assign(paste("Coef TVP4 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),9] )
assign(paste("Coef TVP4 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman4$m[which(index(fit.kalman4$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),10] )

#MQO5 DCaIT
assign(paste("Coef TVP5 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP5 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP5 FX",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP5 IPA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP5 ONI",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP5 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP5 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP5 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )
assign(paste("Coef TVP5 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman5$m[which(index(fit.kalman5$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),9] )

#MQO6 DCaT
assign(paste("Coef TVP6 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP6 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP6 FX",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP6 ONI",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP6 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP6 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP6 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP6 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman6$m[which(index(fit.kalman6$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )

#MQO7 DCE
assign(paste("Coef TVP7 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP7 CRB",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP7 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP7 EXPEC",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP7 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP7 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP7 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP7 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman7$m[which(index(fit.kalman7$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )

#MQO8 DCE12
assign(paste("Coef TVP8 INERCIA",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),1] )
assign(paste("Coef TVP8 CRB",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),2] )
assign(paste("Coef TVP8 DESEMP",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),3] )
assign(paste("Coef TVP8 EXPEC12",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),4] )
assign(paste("Coef TVP8 SD1",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),5] )
assign(paste("Coef TVP8 SD2",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),6] )
assign(paste("Coef TVP8 SD3",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),7] )
assign(paste("Coef TVP8 SD4",paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep=" "),sep="" ) ,fit.kalman8$m[which(index(fit.kalman8$m)==paste(crt_year, substr((crt_mth-1)/4,start=2,stop=4),sep="")),8] )


#################################MATRIZES DE COEFICIENTES#########################################

# 1 Livres com PIM, Desemp e CRB em R$
Coefs.1 = matrix(nrow = ncol(aux_dat1)+3 , ncol = 2)
row.names(Coefs.1) = names(mqo1$coefficients)
colnames(Coefs.1) = c("MQO","TVP")
Coefs.1[,1] = summary(mqo1)$coefficients[,1]
Coefs.1[1,2] = `Coef TVP1 SD12017 .75`
Coefs.1[2,2] = `Coef TVP1 SD22017 .75`
Coefs.1[3,2] = `Coef TVP1 SD32017 .75`
Coefs.1[4,2] = `Coef TVP1 SD42017 .75`
Coefs.1[5,2] = `Coef TVP1 INERCIA2017 .75`
Coefs.1[6,2] = `Coef TVP1 PIM2017 .75`
Coefs.1[7,2] = `Coef TVP1 CRB2017 .75`
Coefs.1[8,2] = `Coef TVP1 DESEMP2017 .75`


# 2 Livres com  Desemp CRB
Coefs.2 = matrix(nrow = ncol(aux_dat2)+3 , ncol = 2)
row.names(Coefs.2) = names(mqo2$coefficients)
colnames(Coefs.2) = c("MQO","TVP")
Coefs.2[,1] = summary(mqo2)$coefficients[,1]
Coefs.2[1,2] = `Coef TVP2 SD12017 .75`
Coefs.2[2,2] = `Coef TVP2 SD22017 .75`
Coefs.2[3,2] = `Coef TVP2 SD32017 .75`
Coefs.2[4,2] = `Coef TVP2 SD42017 .75`
Coefs.2[5,2] = `Coef TVP2 INERCIA2017 .75`
Coefs.2[6,2] = `Coef TVP2 CRB2017 .75`
Coefs.2[7,2] = `Coef TVP2 DESEMP2017 .75`

# 3 Livres com PIM, Desemp, Cambio e IPA

Coefs.3 = matrix(nrow = ncol(aux_dat3)+3 , ncol = 2)
row.names(Coefs.3) = names(mqo3$coefficients)
colnames(Coefs.3) = c("MQO","TVP")
Coefs.3[,1] = summary(mqo3)$coefficients[,1]
Coefs.3[1,2] = `Coef TVP3 SD12017 .75`
Coefs.3[2,2] = `Coef TVP3 SD22017 .75`
Coefs.3[3,2] = `Coef TVP3 SD32017 .75`
Coefs.3[4,2] = `Coef TVP3 SD42017 .75`
Coefs.3[5,2] = `Coef TVP3 INERCIA2017 .75`
Coefs.3[6,2] = `Coef TVP3 DESEMP2017 .75`
Coefs.3[7,2] = `Coef TVP3 PIM2017 .75`
Coefs.3[8,2] = `Coef TVP3 FX2017 .75`
Coefs.3[9,2] = `Coef TVP3 IPA2017 .75`

# 4 Livres com PIM, Desemp, Cambio, IPA e Temperatura

Coefs.4 = matrix(nrow = ncol(aux_dat4)+3 , ncol = 2)
row.names(Coefs.4) = names(mqo4$coefficients)
colnames(Coefs.4) = c("MQO","TVP")
Coefs.4[,1] = summary(mqo4)$coefficients[,1]
Coefs.4[1,2] = `Coef TVP4 SD12017 .75`
Coefs.4[2,2] = `Coef TVP4 SD22017 .75`
Coefs.4[3,2] = `Coef TVP4 SD32017 .75`
Coefs.4[4,2] = `Coef TVP4 SD42017 .75`
Coefs.4[5,2] = `Coef TVP4 INERCIA2017 .75`
Coefs.4[6,2] = `Coef TVP4 DESEMP2017 .75`
Coefs.4[7,2] = `Coef TVP4 PIM2017 .75`
Coefs.4[8,2] = `Coef TVP4 FX2017 .75`
Coefs.4[9,2] = `Coef TVP4 IPA2017 .75`
Coefs.4[10,2] = `Coef TVP4 ONI2017 .75`

# 5 Livres com Desemp, Cambio, IPA e Temperatura

Coefs.5 = matrix(nrow = ncol(aux_dat5)+3 , ncol = 2)
row.names(Coefs.5) = names(mqo5$coefficients)
colnames(Coefs.5) = c("MQO","TVP")
Coefs.5[,1] = summary(mqo5)$coefficients[,1]
Coefs.5[1,2] = `Coef TVP5 SD12017 .75`
Coefs.5[2,2] = `Coef TVP5 SD22017 .75`
Coefs.5[3,2] = `Coef TVP5 SD32017 .75`
Coefs.5[4,2] = `Coef TVP5 SD42017 .75`
Coefs.5[5,2] = `Coef TVP5 INERCIA2017 .75`
Coefs.5[6,2] = `Coef TVP5 DESEMP2017 .75`
Coefs.5[7,2] = `Coef TVP5 FX2017 .75`
Coefs.5[8,2] = `Coef TVP5 IPA2017 .75`
Coefs.5[9,2] = `Coef TVP5 ONI2017 .75`

# 6 Livres com Desemp, Cambio e Temperatura

Coefs.6 = matrix(nrow = ncol(aux_dat6)+3 , ncol = 2)
row.names(Coefs.6) = names(mqo6$coefficients)
colnames(Coefs.6) = c("MQO","TVP")
Coefs.6[,1] = summary(mqo6)$coefficients[,1]
Coefs.6[1,2] = `Coef TVP6 SD12017 .75`
Coefs.6[2,2] = `Coef TVP6 SD22017 .75`
Coefs.6[3,2] = `Coef TVP6 SD32017 .75`
Coefs.6[4,2] = `Coef TVP6 SD42017 .75`
Coefs.6[5,2] = `Coef TVP6 INERCIA2017 .75`
Coefs.6[6,2] = `Coef TVP6 DESEMP2017 .75`
Coefs.6[7,2] = `Coef TVP6 FX2017 .75`
Coefs.6[8,2] = `Coef TVP6 ONI2017 .75`

# 7 Livres com Desemp, CRB e Expectativas trimestrais

Coefs.7 = matrix(nrow = ncol(aux_dat7)+3 , ncol = 2)
row.names(Coefs.7) = names(mqo7$coefficients)
colnames(Coefs.7) = c("MQO","TVP")
Coefs.7[,1] = summary(mqo7)$coefficients[,1]
Coefs.7[1,2] = `Coef TVP7 SD12017 .75`
Coefs.7[2,2] = `Coef TVP7 SD22017 .75`
Coefs.7[3,2] = `Coef TVP7 SD32017 .75`
Coefs.7[4,2] = `Coef TVP7 SD42017 .75`
Coefs.7[5,2] = `Coef TVP7 INERCIA2017 .75`
Coefs.7[6,2] = `Coef TVP7 CRB2017 .75`
Coefs.7[7,2] = `Coef TVP7 DESEMP2017 .75`
Coefs.7[8,2] = `Coef TVP7 EXPEC2017 .75`

# 8 Livres com Desemp, CRB e Expectativas 12 meses a frente

Coefs.8 = matrix(nrow = ncol(aux_dat8)+3 , ncol = 2)
row.names(Coefs.8) = names(mqo8$coefficients)
colnames(Coefs.8) = c("MQO","TVP")
Coefs.8[,1] = summary(mqo8)$coefficients[,1]
Coefs.8[1,2] = `Coef TVP8 SD12017 .75`
Coefs.8[2,2] = `Coef TVP8 SD22017 .75`
Coefs.8[3,2] = `Coef TVP8 SD32017 .75`
Coefs.8[4,2] = `Coef TVP8 SD42017 .75`
Coefs.8[5,2] = `Coef TVP8 INERCIA2017 .75`
Coefs.8[6,2] = `Coef TVP8 CRB2017 .75`
Coefs.8[7,2] = `Coef TVP8 DESEMP2017 .75`
Coefs.8[8,2] = `Coef TVP8 EXPEC122017 .75`


############################GRÁFICOS################################
setwd("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/Modelos/R")
# Inércia
pdf('inercia.pdf')
plot(fit.kalman1$m[,1],type="l",main="Evolução dos Coeficientes de Inércia",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,1],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,1],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,1],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman5$m[,1],type="l",col="orange",lty=1,lwd=2)
lines(fit.kalman6$m[,1],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman7$m[,1],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman8$m[,1],type="l",col="green4",lty=1,lwd=2)
dev.off()
# Câmbio
pdf('cambio.pdf')
plot(fit.kalman3$m[,4],type="l",main="Evolução dos Coeficientes de Câmbio",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman4$m[,4],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman5$m[,3],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman6$m[,3],type="l",col="yellow",lty=1,lwd=2)
dev.off()
# Desemprego 
pdf('desemprego.pdf')
plot(fit.kalman1$m[,4],type="l",main="Evolução dos Coeficientes de Desemprego",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,3],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,2],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,2],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman5$m[,2],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman6$m[,2],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman7$m[,3],type="l",col="green4",lty=1,lwd=2)
lines(fit.kalman8$m[,3],type="l",col="orange",lty=1,lwd=2)
dev.off()
# CRB
pdf('CRB.pdf')
plot(fit.kalman1$m[,3],type="l",main="Evolução dos Coeficientes do CRB (em R$)",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,2],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman7$m[,2],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman8$m[,2],type="l",col="green",lty=1,lwd=2)
dev.off()
# Expectativas Tri
pdf('expectativas_tri.pdf')
plot(fit.kalman7$m[,4],type="l",main="Evolução dos Coeficientes de Expectativas",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
dev.off()
# Expectativas 12 meses
pdf('expectativas_12.pdf')
plot(fit.kalman8$m[,4],type="l",main="Evolução dos Coeficientes de Expectativas",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
dev.off()
#SD 1
pdf('SD1.pdf')
plot(fit.kalman1$m[,5],type="l",main="Evolução dos Coeficientes de Seas 1",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,4],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,6],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,7],type="l",col="green",lty=1,lwd=2)
lines(fit.kalman5$m[,6],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman6$m[,5],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman7$m[,5],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman8$m[,5],type="l",col="green4",lty=1,lwd=2)
dev.off()

#SD 2
pdf('SD2.pdf')
plot(fit.kalman1$m[,6],type="l",main="Evolução dos Coeficientes de Seas 2",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,5],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,7],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,8],type="l",col="green",lty=1,lwd=2)
lines(fit.kalman5$m[,7],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman6$m[,6],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman7$m[,6],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman8$m[,6],type="l",col="green4",lty=1,lwd=2)
dev.off()

#SD 3
pdf('SD3.pdf')
plot(fit.kalman1$m[,7],type="l",main="Evolução dos Coeficientes de Seas 3",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,6],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,8],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,9],type="l",col="green",lty=1,lwd=2)
lines(fit.kalman5$m[,8],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman6$m[,7],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman7$m[,7],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman8$m[,7],type="l",col="green4",lty=1,lwd=2)
dev.off()

#SD 4
pdf('SD4.pdf')
plot(fit.kalman1$m[,8],type="l",main="Evolução dos Coeficientes de Seas 4",xlab="Período",ylab="Coeficiente",col="black",lty=1,lwd=2)
lines(fit.kalman2$m[,7],type="l",col="red",lty=1,lwd=2)
lines(fit.kalman3$m[,9],type="l",col="blue",lty=1,lwd=2)
lines(fit.kalman4$m[,10],type="l",col="green",lty=1,lwd=2)
lines(fit.kalman5$m[,9],type="l",col="yellow",lty=1,lwd=2)
lines(fit.kalman6$m[,8],type="l",col="aquamarine",lty=1,lwd=2)
lines(fit.kalman7$m[,8],type="l",col="coral",lty=1,lwd=2)
lines(fit.kalman8$m[,8],type="l",col="green4",lty=1,lwd=2)
dev.off()


#source("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/Modelos/R/mallowsweights")
#W = matrix(sol$solution, nrow=16,ncol=1)
#row.names(W) = c('mqo1','mqo2','mqo3','mqo4','mqo5','mqo6','mqo7','mqo8','tvp1','tvp2','tvp3','tvp4','tvp5','tvp6','tvp7','tvp8')


pt_medio = fit.kalman4$m[,4]
pt_crb_medio = rowMeans(cbind(fit.kalman1$m[,4],fit.kalman2$m[,4],fit.kalman7$m[,3],fit.kalman8$m[,3]))
wb = write.xlsx(pt_medio,file = "pt_medio.xlsx")
wb = write.xlsx(pt_crb_medio,file = "pt_medio_crb.xlsx")
