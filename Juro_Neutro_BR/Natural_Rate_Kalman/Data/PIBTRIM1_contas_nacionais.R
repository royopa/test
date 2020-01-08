library(readxl)
library(dplyr)
library(lubridate)
#### PIB IBGE (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
pib <- as.data.frame(read_excel(paste0(path_data,"MCM/PIBTRIM1.xls"), 
                                    sheet="Série Encadeada - Dessaz", skip=3))


nms <- c("datas", "val_add", "imp_liq", "pib_merc", "agro_tot", "ind_tot", "ind_ext_min", "ind_trans", "ind_cons_civ", 
         "ind_energia", "serv_tot", "serv_com", "serv_transp", "serv_info", "serv_fin", "serv_outros", "serv_imov",
         "serv_adm_pub", "desp_cons", "desp_cons_adm_pub", "fbkf", "exp", "imp")
names(pib) <- nms

pib_tri <- pib[1:(which(pib$datas == "MÉDIAS ANUAIS")-1),]
pib_ano <- pib[which(pib$datas == "MÉDIAS ANUAIS"):(which(pib$datas == 
   "Nome da Série: Produto Interno Bruto Trimestral por Setor de Atividade - Série Encadeada - Dados Originais")-2),]

per <- strsplit(pib_tri$datas, "[.]")
per <- data.frame(ano=sapply(per,'[[',1) %>% as.character %>% as.numeric, 
                  tri=sapply(per,'[[',2) %>% as.character)
per$mes <- NA
per$mes[which(per$tri == "I")] <- 3;   per$mes[which(per$tri == "II")] <- 6
per$mes[which(per$tri == "III")] <- 9; per$mes[which(per$tri == "IV")] <- 12

pib_tri$datas <- as.Date(paste0(per$ano,"-",per$mes,"-01"), format="%Y-%m-%d")