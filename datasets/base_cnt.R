setwd("C:/Users/PIETCON/Documents/Data")
#### PIB IBGE (retirado da MCM)
pib_dsz <- as.data.frame(read_excel("PIB IBGE Completo.xls", sheet="Série com Ajuste Sazonal", skip=3))
names(pib_dsz) <- c("date", "agro_tot", "ind_extrat", "ind_transf", "ind_eletr", "ind_const", 
                    "ind_tot", "serv_com", "serv_transp", "serv_info", "serv_fin", "serv_imob", 
                    "serv_outros", "serv_admpub", "serv_tot", "val_ad", "pib", "cons_fam", 
                    "cons_gov", "fbkf", "exp", "imp")
pib_dsz$date <- seq(as.Date("1996/1/1"), as.Date("2018/6/30"), by = "quarter")