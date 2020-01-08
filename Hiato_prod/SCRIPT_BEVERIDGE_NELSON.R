####### SCRIPT QUE CALCULA O TREND DO PIB POR BEVERIDGE-NELSON #######
# O PACOTE USADO SERÁ O DLM, POIS CONTÉM UMA FUNÇÃO PARA ISSO #
# PAPER USADO COMO BASE: State Space Modeling in Macroeconomics and Finance 
# (http://faculty.washington.edu/ezivot/statespacesurvey.pdf)
# http://research.economics.unsw.edu.au/jmorley/m02.pdf

library("dlm", lib.loc="~/R/win-library/3.4")


y_d = diff(log(Y))

# Explicitando variáveis da função dlm

modeldlmBN = function(phi){
  
  FF = matrix(data = c(1,0,0,0),nrow = 1, ncol = 4)
  
  GG = matrix(data = 0, nrow = 4, ncol = 4)
  GG[1,1] = phi[1]
  GG[1,2] = phi[2]
  GG[1,3] = phi[3]
  GG[1,4] = phi[4]
  GG[2,1] = 1
  GG[4,3] = 1
  
  V = 0
  
  W = diag(nrow = 4,ncol = 4)
  W[4,4] = 0
  W[2,2] = 0
  W[3,3] = exp(phi[5])
  W[1,1] = exp(phi[5])
  W[1,3] = exp(phi[5])
  W[3,1] = exp(phi[5])
  
  m0 = c(0,0,0,0)
  C0 = 100*diag(4)
  
  model_aux = dlm(FF = FF, GG = GG, V = V, W = W, m0 = m0, C0 = C0)
  return(model_aux)
  
}

MLEestimBN = dlmMLE(y_d, parm = c(1,1,1,1,1), build = modeldlmBN)

fit.kalman.BN = dlmFilter(y_d, mod = modeldlmBN(MLEestimBN$par)) #filtro de kalman para estimar os não-obs
#Séries estimadas estão em m

# Construindo a tendência de BN
F = matrix(data = 0, nrow = 4, ncol = 4)
F[1,] = MLEestimBN$par[1:4]
F[2,1] = 1
F[4,3] = 1
aux = matrix(data = c(1,0,0,0),nrow = 1,ncol = 4)%*%F%*%solve(diag(4) - F)

Yn.BN = vector()
for (i in 1:length(Y)){
  Yn.BN[i] = Y[i] + aux%*%t(fit.kalman.BN$m)[,i]
}

#wb = write.xlsx(Yn.BN,file = "output_BN.xlsx")
