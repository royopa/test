library(readxl)
library(dplyr)
library(lubridate)

path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/Natural_Rate_Kalman/"


#Taxa de juro real ex ante
source(paste0(path,"Data/MFISWAP0_swap.R"))
swap <- swap[, c("datas", "swap360_med")]
source(paste0(path,"Data/BCB_inf_exp.R"))
swap <- merge(swap, ipca_exp_sm, by=c("datas"))
swap$jrr_ante <- swap$swap360_med - swap$ipca_exp_sm
swap <- swap[, c("datas", "jrr_ante")]


#Taxa de juro real ex post
source(paste0(path,"Data/MFIJURO0_selic.R"))
selic <- selic[, c("datas","selic_copom")]
source(paste0(path,"Data/PRCIPCA0_ipca_grupos.R"))
ipca <- ipca_mes <- ipca_mes[,c("datas", "ipca_geral")]
ipca$ipca_geral <- NA
for (i in 13:nrow(ipca)){ipca$ipca_geral[i] <- 100*(ipca_mes$ipca_geral[i] / ipca_mes$ipca_geral[i-12] -1)}
selic <- merge(selic, ipca, by=c("datas"))
selic$jrr_post <- selic$selic_copom - selic$ipca_geral
selic$desv_ipca <- selic$ipca_geral - 4.5
selic <- selic[, c("datas", "jrr_post", "desv_ipca", "ipca_geral")]


#Variaveis controle
pib_pot <- read.csv(paste0(path,"Data/EST_prod_pot.csv")); names(pib_pot) <- c("datas", "pib_pot")
pib_pot$datas <- pib_pot$datas %>% as.Date(origin="1970-03-05"); day(pib_pot$datas) <- 1

source(paste0(path,"Data/PIBTRIM1_contas_nacionais.R"))
pib_tri <- pib_tri[, c("datas", "val_add")]

df <- merge(swap, selic,    by=c("datas"))
df <- merge(df,   pib_tri,  by=c("datas"))
df <- merge(df,   pib_pot,  by=c("datas"))

df$hiato <- log(df$pib_pot) - log(df$val_add)
