library(readxl)

#### DESEMPREGO PNAD (Serie retroagida MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
pnad <- as.data.frame(read_excel(paste0(path_data,"MCM/ATVMCM4.xls"),sheet="pnad_dessaz", skip = 2))

names <- c("datas", "pes_ocup", "pea", "tx_desemp", "pia", "massa_sal")
names(pnad) <- names

pnad <- pnad[1:(which(pnad[,1] == "Nome da Série: Séries Retroagidas PNAD Contínua")-1), ]

for (i in 2:dim(pnad)[2]){
  pnad[which(pnad[,i] == "-"),i] <- 0;    pnad[which(pnad[,i] == "nd"),i] <- 0
  pnad[which(pnad[,i] == "<NA>"),i] <- 0; pnad[is.na(pnad[,i]),i] <- 0
  pnad[,i] <- as.numeric(pnad[,i])}

pnad$datas <- pnad$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character