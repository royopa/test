setwd("E:/Dissertacao")
library(readxl)
library(ggplot2)
library(DataCombine)

rm(list=ls())

#Importe todos os dados presentes na planilha  fonte.xlsx para o R.
data <- as.data.frame(read_excel("Prova 4E/fonte.xlsx"))
data <- read.csv(file ="Prova 4E/fonte.csv", header =TRUE, sep =";", dec=",")
n <- dim(data)[1] #1071 obs
m <- dim(data)[2] #13 vars
names <- names(data)

#Já no R, mantenha apenas os dados referentes à 
#Indicador (coluna B): PMC.  Série (coluna C): Vol. vendas - índice restrito. 
#Indicador (coluna B): PIM.  Série (coluna C): índice de Produção Física Industrial - Industria geral.  
#Em ambos os casos, mantenha tanto as séries originais e com ajuste sazonal (dessaz), de acordo com a base indicada na coluna D. Exclua as demais variáveis de sua base de dados. 
pmc <- data[data$Indicador == "PMC", c(3, 5, 6, 12, 13)]
pmc <- pmc[pmc$Serie == "Vol. vendas - indice restrito",]
pmc_or <- pmc[pmc$Base == "Original",c(4,5)]
pmc_des <- pmc[pmc$Base == "Dessaz.",c(4,5)]

pim <- data[data$Indicador == "PIM", c(3, 5, 6, 12, 13)]
pim <- pim[pim$Serie == "indice de Producao Fisica Industrial - Industria geral",]
pim_or <- pim[pim$Base == "Original",c(4,5)]
pim_des <- pim[pim$Base == "Dessaz.",c(4,5)]

#Crie um gráfico de linha para a evolução da PMC - original e dessaz - ao longo do tempo. 
#Utilizando um gráfico de colunas, faça o mesmo para a série da PIM. 
pmc_final <- merge(pmc_or, pmc_des, by=c("Data"))
pim_final <- merge(pim_or, pim_des, by=c("Data"))

data_final <- merge(pmc_final, pim_final, by=c("Data"))
names(data_final) <- c("data","pmc_or", "pmc_des", "pim_or", "pim_des")

ggplot(data_final, aes(data, )) + 
            geom_line(aes(, pmc_or),  colour = "red") + 
            geom_line(aes(, pmc_des), colour = "blue")

ggplot(data_final, aes(data, )) + 
            geom_line(aes(, pim_or),  colour = "red") + 
            geom_line(aes(, pim_des), colour = "blue")

#Utilizando as séries mensais com ajuste sazonal dos níveis da PMC e da PIM estime o seguinte modelo:
#        PIM = c + beta_1*PMC_t + beta_2*PMC_(t-1) + epsilon_t
df <- data_final
df <- slide(df, Var = "pmc_des", slideBy = -1)
names(df)[6] <- "pmc_des_1"

model1 <- lm(pim_des ~ pmc_des + pmc_des_1, data = df)

#Apresente graficamente os resíduos (epsilon_t) estimados. 
df_res <- data.frame(df$data[-1], model1$residuals)
names(df_res) <- c("data","res")
ggplot(df_res, aes(data, )) + 
            geom_line(aes(, res), colour = "blue")

#Trimestralize os dados da PIM e da PMC, a partir do cálculo da média dos números índices mensais ao longo do trimestre. 
n <- dim(df)[1] #184 obs
df$pim_tri <- df$pmc_tri <- 0
for (i in 3:n){
  df$pim_tri[i] <- mean(df$pim_des[(i-2):i])
  df$pmc_tri[i] <- mean(df$pmc_des[(i-2):i])}

id <- 3*(1:61); df_tri <- df[id, c(1,7,8)]

#Utilizando a série trimestral das variáveis em seus valores originais, estime a seguinte regressão
#dlog(PIM_t) = c + beta_1*dlog(PMC_(t-1)) + D_(Q=1) + D_(Q=2) + D_(Q=3) + epsilon_t   
#Onde dlog representa a primeira diferença do log da variável em questão, e D_(Q=q) representa uma dummy sazonal para o trimestre Q.
df_tri <- slide(df_tri, Var = "pmc_tri", slideBy = -1)
df_tri <- slide(df_tri, Var = "pim_tri", slideBy = -1)
names(df_tri)[c(4,5)] <- c("pmc_tri_1","pim_tri_1")
df_tri[, 2:5] <- log(df_tri[, 2:5])
df_tri$d_pmc <- df_tri$pmc_tri - df_tri$pmc_tri_1
df_tri$d_pim <- df_tri$pim_tri - df_tri$pim_tri_1

df_tri <- df_tri[, c(1,6,7)]
id_1tri <- 4*(1:15)-3; id_2tri <- id_1tri + 1; id_3tri <- id_1tri + 2
df_tri$d_1t <- df_tri$d_2t <- df_tri$d_3t <- 0
df_tri$d_1t[id_1tri] <- 1; df_tri$d_2t[id_2tri] <- 1; df_tri$d_3t[id_3tri] <- 1

df_tri <- slide(df_tri, Var = "d_pmc", slideBy = -1)
names(df_tri)[c(7)] <- c("d_pmc_1")

model2 <- lm(d_pim ~ d_pmc_1 + d_1t + d_2t + d_3t , data = df_tri)

#Utilize os dados presentes na planilha phillips.xlsx
#Utilizando o software de sua preferência uma curva de Phillips a partir dos dados. 
#Realize uma projeção fora da amostra.
#Avalie os resultados de seu modelo. 
#Comente as estatísticas que você analisou para selecionar o modelo final.
phi <- as.data.frame(read_excel("Prova 4E/phillips_data.xlsx", skip =1))
names(phi)[c(2,5)] <- c("data","pim")
phi <- phi[18:73, c("data", "IPCA_pl", "pim", "cambio", "expec_infl", "hiato", "CRB_f", "ipa_agr", "ipa_ind")]

phi_in <- phi[1:50, ]; phi_out <- phi[51:56, ]
coefs <- phi_out; coefs[, 2:9] <- 0; names(coefs)[2] <- "intercept"
model3 <- lm(IPCA_pl ~ pim + cambio + expec_infl + hiato + CRB_f + ipa_agr + ipa_ind, data = phi_in)

for (i in 1:6){coefs[i,2:9] <- model3$coefficients}

coefs[,3:9] <- coefs[,3:9] * phi_out[,3:9] 
phi_out$ipca_out <- rowSums(coefs[,2:9])
phi_in$ipca_out <- phi_in$IPCA_pl

phi_final <- rbind(phi_in, phi_out)
phi_final$data <- 1:56

ggplot(phi_final, aes(data, )) + 
          geom_line(aes(, IPCA_pl), colour = "blue") +  
          geom_line(aes(, ipca_out), colour = "red")
  