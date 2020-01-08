library(readxl)
#### Nome "Indice nacional de precos ao consumidor amplo (IPCA) - Grandes grupos - Brasil - IBGE (DEZ/1993=100)"
#### Origem MCM
#### codigo: "PRCIPCA0.xls"
#### Ref: http://www.mcmconsultores.com.br/arearestrita/bancodedadositem/download/90
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 

ipca <- as.data.frame(read_excel(paste0(path_data,"MCM/PRCIPCA0.xls"), 
                                sheet = "Nº. Índice - Grupos", skip = 1))
nms <- c("datas", "ipca_geral", "ipca_alim_beb", "ipca_habit", "ipca_art_resid", 
         "ipca_vest", "ipca_trans", "ipca_saude", "ipca_desp_pes", "ipca_educ",
         "ipca_comunic", "ipca_transp_comunic")
names(ipca) <- nms

ipca_mes <- ipca[1:(which(ipca[,1] == "NÚMERO ÍNDICE EM FINAL DE PERÍODO (BASE: DEZ/93 = 100)") -1),]
ipca_ano <- ipca[(which(ipca[,1] == "NÚMERO ÍNDICE EM FINAL DE PERÍODO (BASE: DEZ/93 = 100)") +1):
                         (which(ipca[,1] == "Nome da Série: Índice Nacional de Preços ao Consumidor Amplo (IPCA) - Grandes Grupos - Brasil - IBGE") -2),]
                          
for (i in 2:ncol(ipca)){
  ipca_mes[which(ipca_mes[,i] == "-"),i] <- 0;    ipca_ano[which(ipca_ano[,i] == "-"),i] <- 0
  ipca_mes[which(ipca_mes[,i] == "nd"),i] <- 0;   ipca_ano[which(ipca_ano[,i] == "nd"),i] <- 0
  ipca_mes[which(ipca_mes[,i] == "<NA>"),i] <- 0; ipca_ano[which(ipca_ano[,i] == "<NA>"),i] <- 0
  ipca_mes[is.na(ipca_mes[,i]),i] <- 0          ; ipca_ano[is.na(ipca_ano[,i]),i] <- 0
  ipca_mes[,i] <- as.numeric(ipca_mes[,i]);       ipca_ano[,i] <- as.numeric(ipca_ano[,i])}

ipca_mes$datas <- ipca_mes$datas %>% as.numeric %>% as.Date(origin="1899-12-30")
