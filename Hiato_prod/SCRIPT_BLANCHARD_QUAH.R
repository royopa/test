# SCRIPT QUE CALCULA O PRODUTO POTENCIAL USANDO O MÉTODO DE BLANCHARD E QUAH (VAR ESTRUTURAL)

library("vars",      lib.loc="~/R/win-library/3.5")
library("rootSolve", lib.loc="~/R/win-library/3.5")

#CRIANDO AS SÉRIES (usando como base https://sites.ualberta.ca/~sfossati/e509/files/slides/Lec10.R )

yt = log(Y)
dyt = diff(yt)
unt = log(1-E)
cut = log(C)

dyt = ts(dyt, start = c(1996,2), frequency = 4)
unt = ts(unt, start = c(1996,1), frequency = 4)
cut = ts(cut, start = c(1996,1), frequency = 4)

vardata0 = na.omit(cbind(dyt,unt,cut)) #dados para o VAR
vardata1 = na.omit(cbind(dyt,unt,cut,pi_ts)) #dados para o VAR com inflação
vardata2 = na.omit(cbind(dyt,unt)) #dados para o VAR só com desemprego (como o original)

model0 = VAR(vardata0, lag.max = 4, type = "none") #primeiro VAR estimado
BQ0 = BQ(model0) #SVAR com restrição de longo prazo estimado

model1 = VAR(vardata1, lag.max = 4, type = "none") #primeiro VAR estimado
BQ1 = BQ(model1) #SVAR com restrição de longo prazo estimado

model2 = VAR(vardata2, lag.max = 4, type = "none") #primeiro VAR estimado
BQ2 = BQ(model2) #SVAR com restrição de longo prazo estimado

B_inv0 = solve(BQ0$B) #invertendo para o cálculo (olhar https://www.rbnz.govt.nz/-/media/ReserveBank/Files/Publications/Discussion%20papers/2000/dp00-3.pdf)
B_inv1 = solve(BQ1$B)
B_inv2 = solve(BQ2$B)

epislon0 = resid(model0) #resíduos da forma reduzida
epislon1 = resid(model1)
epislon2 = resid(model2)

struc_s0 = B_inv0%*%t(epislon0) #choques estruturais
struc_s1 = B_inv1%*%t(epislon1)
struc_s2 = B_inv2%*%t(epislon2)

irf.dyt0 = irf(BQ0, impulse="dyt",boot=FALSE,n.ahead=nrow(epislon0)) #impulso resposta 
irf.dyt1 = irf(BQ1, impulse="dyt",boot=FALSE,n.ahead=nrow(epislon1))
irf.dyt2 = irf(BQ2, impulse="dyt",boot=FALSE,n.ahead=nrow(epislon2))

# Calculando o Output Gap e Potential GDP
un_sh0 = vector(length = nrow(epislon0))
cu_sh0 = vector(length = nrow(epislon0)) #vetores de choques acumulados
un_sh1 = vector(length = nrow(epislon1))
cu_sh1 = vector(length = nrow(epislon1)) #vetores de choques acumulados
pi_sh1 = vector(length = nrow(epislon1))
un_sh2 = vector(length = nrow(epislon2))


for (i in 1:length(un_sh0)) {
  un_sh0[i] = irf.dyt0$irf$dyt[1:i,2] %*% struc_s0[2,1:i] #choques de demanda acumulados são os resíduos x a impulso
  cu_sh0[i] = irf.dyt0$irf$dyt[1:i,3] %*% struc_s0[3,1:i] #resposta
}

for (i in 1:length(un_sh1)) {
  un_sh1[i] = irf.dyt1$irf$dyt[1:i,2] %*% struc_s1[2,1:i] #choques de demanda acumulados são os resíduos x a impulso
  cu_sh1[i] = irf.dyt1$irf$dyt[1:i,3] %*% struc_s1[3,1:i] #resposta
  pi_sh1[i] = irf.dyt1$irf$dyt[1:i,4] %*% struc_s1[4,1:i]
}
for (i in 1:length(un_sh2)) {
  un_sh2[i] = irf.dyt2$irf$dyt[1:i,2] %*% struc_s0[2,1:i] #choques de demanda acumulados são os resíduos x a impulso
                                                          #resposta
}



dem_tot_sh0 = -(un_sh0 + cu_sh0) #output gap (esse output gap é calculado na variação do PIB)
dem_tot_sh1 = -(un_sh1 + cu_sh1 + pi_sh1)
dem_tot_sh2 = -(un_sh2)