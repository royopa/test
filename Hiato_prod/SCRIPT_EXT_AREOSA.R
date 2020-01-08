####### SCRIPT EXTENSÃO DO MODELO AREOSA 2008 PARA INCLUIR A CURVA DE PHILLIPS #######
# O PACOTE USADO SERÁ O MARSS (MAIS FÁCIL DE COLOCAR VARIÁVEIS EXÓGENAS) #

#################################### MODELO ##########################################
#      x_t = B_t*x_(t-1) + u_t + C_t*c_t + G_t*w_t,     w_t ~ N(0,Q_t)
#      y_t = Z_t*x_t + a_t + D_t*d_t + H_t*v_t,         v_t ~ N(0,R_t)
######################################################################################
# Onde,
# x_t é o vetor de não-observáveis
# y_t é o vetor de observáveis. Dimensão: nxT, então tem que ser colocado de forma que o tempo fique nas colunas
# B_t = B (invariante no meu caso), matriz de transição, é a matriz G em SCRIPT_AREOSA_2008
# u_ t = a_t = 0 (no caso, default)
# C_t = c_t = 0 (no caso, default, pois não há choque exógeno na transição)
# G_t = G, matriz que mapeia os erros, default é a identidade
# Z_t = Z, matriz que mapea as não-obs nas obs. É a matriz F no SCRIPT_AREOSA_2008, com a adição de uma equação de Phillips
# D_t = D, matriz n x 2, com os parâmetros da Phillips a serem estimados (efeito de y_(t-1) e pi_(t-1))
# d_t = matriz 2 x T, com as exógenas, no caso, y_(t-1) e pi_(t-1) (são variáveis defasadas, portanto, exógenas)
# H_t = H, matriz que mapeia os erros, default é a identidade
# Q_t = Q, matriz de variância e covariância dos erros. Aqui é a matriz W de SCRIPT_AREOSA_2008
# R_t = R, matriz de variância e covariância dos erros das obs. É a matriz V de SCRIPT_AREOSA_2008, com uma dim a mais

# m <= n segundo as regras do pacote MARSS. Isso inviabiliza o formato que AREOSA usa.

# PACOTES
library("MARSS", lib.loc="~/R/win-library/3.5")
library("stats", lib.loc="~/R/win-library/3.5")
library("Hmisc", lib.loc="~/R/win-library/3.5")

n = 4  #, numero de variáveis observáveis
m = 4  #, numero de variáveis não-observáveis (na verdade são 6, criei uma auxiliar que é igual a zero só pra equilibrar
#        o tamanho da matriz de erros)

# DADOS
y_ext = t(matrix(data = na.omit(cbind(log(E),log(C),log(Y),nuc_Pi)), nrow = nrow(data),ncol = n ))


# INPUTS DO MODELO

#Q = matrix(list("par3*par5*exp(sigma)",0,"par4*par5*exp(sigma)",0,0,0,0,0,"par1*exp(sigma)",0,0,0,0,0,
#                "par4*par5*exp(sigma)",0,"par5*exp(sigma)",0,0,0,0,0,0,0,"par2*exp(sigma)",0,0,0,
#                0,0,0,0,"exp(sigma)",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"exp(sigma7)"),nrow = 7, ncol = 7,byrow = TRUE)

#Q = matrix(0, nrow = 7, ncol = 7)
#Q[1,1] =  c("par3*par5*exp(sigma)")  #  par3*par5*exp("sigma") #sigma1 = par3*sigma3 = par3*par5*sigma5
#Q[2,2] =  c("par1*exp(sigma)")       #  par1*exp("sigma") #sigma2 = par1*sigma5
#Q[3,3] =  c("par5*exp(sigma)")       #  par5*exp("sigma")  #sigma3 = par5*sigma5
#Q[4,4] =  c("par2*exp(sigma)")       #  par2*exp("sigma") #sigma4 = par2*sigma5
#Q[5,5] =  c("exp(sigma)")            #  exp("sigma") #sigma5
#Q[7,7] =  c("exp(sigma7)")           #  exp("sigma7") #sigma7, variancia da inflação, não coloquei restrição
#Q[1,3] =  c("par4*par5*exp(sigma)")  #  par4*par5*exp("sigma")
#Q[1,3] = Q[3,1]

B = diag(n)
B[4,4] = 0
B[4,3] = 1


R = matrix(list("1103.797*s",0,0,0,0,
                "1508.861*s",0,0,0,0, 
                "676.658*s",
                0,0,0,0,"r"), nrow = n, ncol = n, byrow = TRUE)

Q = matrix(list("s",0,0,0,0,"s",0,0,0,0,"s",0,0,0,0,0), nrow = m, ncol = m, byrow = TRUE)


Z = matrix(list(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,"-b"),nrow = n, ncol = m,byrow = TRUE)
#Z = matrix(0,nrow = 4, ncol = 6)
#Z[1,1] = 1
#Z[2,3] = 1
#Z[3,5] = 1
#Z[4,6] = -c("theta") #parâmetro que será estimado
D = matrix(list(0,0,0,0,0,0,"g","b"), nrow = n, ncol = 2, byrow = TRUE  )
#D = matrix(0, nrow = 4, ncol = 2)
#D[4,1] = c("gamma")
#D[4,2] = c("theta")

d = matrix(na.omit(c(Lag(y_ext[3,],shift = 1),Lag(y_ext[4,],shift = 1))), 
           nrow = 2, ncol = length(na.omit(Lag(y_ext[4,],shift = 1))), byrow = TRUE) #AQUI TEM UMA 
#                                                                                    COLUNA A MENOS QUE y_ext 
#                                                                                    QUE TERÁ QUE SER AJUSTADO


model.list = list(Z = Z, D = D, d = d, Q = Q, R = R, A = "equal")
fit = MARSS(y_ext[,-1], model=model.list)
KF = MARSSkf(fit)

En.ext = exp(KF$xtT[1,]) #emprego potencial
Cn.ext = exp(KF$xtT[2,]) #nuci potencial
Yn.ext = exp(KF$xtT[3,]) #pib potencial