library(readxl)
library(dplyr)
library(lubridate)
#### PIB IBGE (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
pib <- as.data.frame(read_excel(paste0(path_data,"MCM/PIBTRIM1.xls"), 
                                    sheet="PIB, PNB, Renda Nacional e FBKF", skip=1))


nms <- c("datas", "pib_merc", "rem_emprego", "renda_prop", "rnb", "tranfs", "renda_disp_bruta", "desp_cons", 
         "poupanca", "fbkf", "cessao_ativos_nfin", "transf_capital", "necess_fin_rm")
names(pib) <- nms

pib_tri <- pib[1:(which(pib$datas == "TOTAIS ANUAIS")-1),]

pib_tri$datas <- pib_tri$datas %>% as.numeric %>% as.Date(origin="1899-12-30")
