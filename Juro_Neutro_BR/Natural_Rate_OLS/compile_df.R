library(readxl)
library(dplyr)
library(lubridate)

path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/Natural_Rate_OLS/"


##Taxa de juro real ex ante
#source(paste0(path,"data/MFISWAP0_swap.R"))
#swap <- swap[, c("datas", "swap360_med")]
#source(paste0(path,"data/BCB_inf_exp.R"))
#swap <- merge(swap, ipca_exp_sm, by=c("datas"))
#swap$jrr_ante <- swap$swap360_med - swap$ipca_exp_sm
#swap <- swap[, c("datas", "jrr_ante")]
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/Natural_Rate_OLS/data/" 
swap <- as.data.frame(read_excel(
  "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/Natural_Rate_OLS/data/juro_real.xlsx"), 
  sheet="Sheet1")
names(swap) <- c("datas", "jrr_ante")
swap$datas <- swap$datas %>% as.character


#Taxa de juro real ex post
source(paste0(path,"data/MFIJURO0_selic.R"))
selic <- selic[, c("datas","selic_copom")]
source(paste0(path,"data/PRCIPCA0_ipca_grupos.R"))
ipca <- ipca_mes <- ipca_mes[,c("datas", "ipca_geral")]
ipca$ipca_geral <- NA
for (i in 13:nrow(ipca)){ipca$ipca_geral[i] <- 100*(ipca_mes$ipca_geral[i] / ipca_mes$ipca_geral[i-12] -1)}
selic <- merge(selic, ipca, by=c("datas"))
selic$jrr_post <- selic$selic_copom - selic$ipca_geral
selic$desv_ipca <- selic$ipca_geral - 4.5
selic <- selic[, c("datas","jrr_post", "desv_ipca")]


#Variaveis controle
pib_pot <- read.csv("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Hiato_prod/EST_prod_pot.csv")
names(pib_pot) <- c("datas", "pib_pot", "pib")
pib_pot$datas <- pib_pot$datas %>% as.Date(origin="1970-03-05")
day(pib_pot$datas) <- 1; pib_pot$datas <- pib_pot$datas %>% as.character
source(paste0(path,"data/PIBTRIM1_contas_nacionais.R"))
pib_tri <- pib_tri[, c("datas", "pib_merc", "poupanca")]
pib_tri$tx_poup <- pib_tri$poupanca / pib_tri$pib_merc
poup <- pib_tri[, c("datas", "tx_poup")]; poup$datas <- poup$datas %>% as.character
source(paste0(path,"data/FINAJUST0_sup_prim.R"))
sup <- sup[, c("datas", "result_prim_cons", "result_prim_ajust")]
source(paste0(path,"data/PLMCRED1_cred.R"))
cred <- cred[, c("datas", "cred_tot", "rec_liv_tot", "rec_dir_tot")]
source(paste0(path,"data/FINDBRT1_div_brut.R"))
div <- div[, c("datas", "div_brut")]
source(paste0(path,"data/MFIEMBI0_embi.R"))
embi <- embi[, c("datas", "embi_br")]
source(paste0(path,"data/SEXQTUM0_funcex.R"))
termos <- termos[, c("datas", "ind_termos")]


#Juro real americano ex post
source(paste0(path,"data/MFIJINT0_usa_rates.R"))
usa_rates <- usa_rates[, c("datas", "fed_funds_eff")]
source(paste0(path,"data/INTEUA00_usa_ind.R"))
usa_inf <- usa_ind <- usa_ind[, c("datas", "cpi")]
usa_inf$cpi <- NA
for (i in 13:nrow(usa_inf)){usa_inf$cpi[i] <- 100*(usa_ind$cpi[i] / usa_ind$cpi[i-12] -1)}
usa_rates <- merge(usa_rates, usa_inf, by=c("datas"))
usa_rates$ffer_post <- usa_rates$fed_funds_eff - usa_rates$cpi
usa_rates <- usa_rates[, c("datas", "ffer_post", "fed_funds_eff")]


df <- merge(sup,   cred,      by=c("datas"))
df <- merge(df,    div,       by=c("datas"))
df <- merge(df,    selic,     by=c("datas"))
df <- merge(df,    swap,      by=c("datas"))

df_mm <- df; df_mm[,-1] <- NA
for (i in 4:nrow(df)){ df_mm[i,-1] <- colMeans(df[i:(i-3),-1]) }


df_mm <- merge(df_mm, poup,      by=c("datas"))
df_mm <- merge(df_mm, embi,      by=c("datas"))
df_mm <- merge(df_mm, termos,    by=c("datas"))
df_mm <- merge(df_mm, usa_rates, by=c("datas"))
df_mm <- merge(df_mm, pib_pot,   by=c("datas")) 
df_mm$hiato <- df_mm$pib - df_mm$pib_pot

