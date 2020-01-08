library(readxl)
library(dplyr)
library(lubridate)

#### Estoque de credito (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
cred <- as.data.frame(read_excel(paste0(path_data,"MCM/PLMCRED1.xls"), sheet="Crédito % PIB", skip=2))
cred <- cred[1:(which(cred[,1]=="Nome da Série: Crédito do sistema financeiro - % do PIB")-2), ]

nms <- c("datas", "cred_tot_pj", "cred_tot_pf", "cred_tot", "rec_liv_pj", "rec_liv_pf", "rec_liv_tot", 
         "rec_dir_pj", "rec_dir_pf", "rec_dir_tot")

names(cred) <- nms

cred$datas <- cred$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character
