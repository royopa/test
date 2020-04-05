library(dplyr)

path <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/1.IPCA/"

source(paste0(path, "rotinas/AUX_read_ipca_ibge.R"), echo=TRUE)

### definindo variaveis para filtrar quais observacoes queremos dentro do historico
dia <- c("15", "28")
mes <- c("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12")
ano <- 1996:2019
bases <- c("var", "peso")

for (k in 1:length(bases)){
  df_ipca_1  <- read.ipca.ibge(paste0(bases[k],"_ipca_89_90.csv"), 28)
  df_ipca_2  <- read.ipca.ibge(paste0(bases[k],"_ipca_91_99.csv"), 28)
  df_ipca_3  <- read.ipca.ibge(paste0(bases[k],"_ipca_99_06.csv"), 28)
  df_ipca_4  <- read.ipca.ibge(paste0(bases[k],"_ipca_06_11.csv"), 28)
  df_ipca_5  <- read.ipca.ibge(paste0(bases[k],"_ipca_12.csv"),    28)

  df_ipca15_1  <- read.ipca.ibge(paste0(bases[k],"_ipca15_00_06.csv"), 15)
  df_ipca15_2  <- read.ipca.ibge(paste0(bases[k],"_ipca15_06_12.csv"), 15)
  df_ipca15_3  <- read.ipca.ibge(paste0(bases[k],"_ipca15_12.csv"),    15)

  df_ipca <- merge(df_ipca_1, df_ipca_2,   by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca_3,   by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca_4,   by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca_5,   by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca15_1, by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca15_2, by=c("cods"), all=TRUE)
  df_ipca <- merge(df_ipca,   df_ipca15_3, by=c("cods"), all=TRUE)
####Warning message:
####  In merge.data.frame(df_ipca, df_ipca15_3, by = c("cods"), all = TRUE) :
####  column names 'prods.x', 'prods.y', 'prods.x', 'prods.y', 'prods.x', 'prods.y' are duplicated in the result

  ### aqui elimino as colunas de produtos sobressalentes q vem das outras planilhas q sao fundidas 
  pp <- c("prods.x","prods.y")
  ### guardo todos os itens de todas as bases para reconstruir o vetor de itens, 
  ### caso algum seja descontinuado ou incluido
  prods   <- df_ipca[, which(names(df_ipca) %in% pp)]
  df_ipca <- df_ipca[,-which(names(df_ipca) %in% pp)]

  ### reconstruindo o vetor de itens, completando com todos os itens em todos os períodos
  locs <- c()
  for (i in 1:ncol(prods)){  locs[!is.na(prods[,i])] <- i    }
  prods$prods <- NA; for (i in 1:nrow(prods)){ prods$prods[i] <- prods[i,locs[i]]}
  df_ipca$prods <- prods$prods
  df_ipca <- df_ipca[,c(1, ncol(df_ipca), 2:(ncol(df_ipca)-1))]

  ### ordernando as colunas do data.frame porque o merge caga a ordem delas
  dts <- as.Date(names(df_ipca)[3:ncol(df_ipca)], format = "%d/%m/%Y")
  df_ipca <- df_ipca[,c(1, 2, (order(dts) + 2))]

  filter <- c("cods", "prods", paste0(dia, "/", rep(mes, each=2), "/", rep(ano, each=24)))
  df_ipca <- df_ipca[,which(names(df_ipca) %in% filter)]
  df_ipca[is.na(df_ipca)] <- ""

  ### substituindo ponto por virgula para o excel ler
  #df_ipca <- sapply(df_ipca, function(x){gsub("\\.",",",x)})

  #ATENCAO: coloquei o delimitador de decimal como ponto pois esta dando alguma cagada no exce
  write.table(df_ipca, paste0(path,"bases/base_old/IPCA_base_", bases[k], ".csv"), sep=";", dec=",", row.names = FALSE)}