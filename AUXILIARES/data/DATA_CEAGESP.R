library(readxl)
library(lubridate)
library(dplyr)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/AUX_df_filler.R", echo=TRUE)
#### Nome "PRECOS CEAGESP"
#### Origem EMAIL
#### codigo: "CEAGESP_base.xlsx"

readbase_ceagesp = function(itens, prods, initial.date="2012-01-01", 
                            carrego=FALSE, mm.days=NULL, varp30=FALSE){
  path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/4.Ceagesp/"
  initial_date <- as.Date(initial.date, format="%Y-%m-%d")
  
  ceagesp <- read_excel(paste0(path_data, "bases/CEAGESP_base.xlsx")) %>% as.data.frame

  #### Guardando as datas para construir o data.frame
  dts <- names(ceagesp)[-c(1,2)] %>% as.Date(format="%Y-%m-%d") %>% as.character

  if (length(prods) != 0){
    #### Selecionando da base os produtoes a serem coletados através do nome por extenso
    indexes <- c()
    for (i in 1:length(prods)){indexes <- c(indexes, grep(prods[i], ceagesp$name, ignore.case=TRUE))}
    nms <- c("datas", ceagesp$name[indexes])
    df <- as.data.frame(cbind(datas=dts, t(ceagesp[indexes, -c(1,2)])))
  } else if (length(itens) != 0){
    #### Incluindo um chave para coletar todos os itens disponíveis na base
    if (itens == "all"){itens <- 1000000:10000000}
    #### Selecionando os itens da base a serem coletados atraves do codigo do produto
    itens <- intersect(ceagesp$cod, itens)
    nms <- c("datas", paste0("cod", itens))
    indexes <- which(ceagesp$cod %in% itens)
    df <- as.data.frame(cbind(datas=dts, t(ceagesp[indexes, -1])))
  } else stop('choose either a product index or a product name')

  for (i in 1:ncol(df)){
    if (i == 1){ df[,i] <- gsub(",", ".", df[,i] %>% as.character) 
    } else {     df[,i] <- gsub(",", ".", df[,i] %>% as.character) %>% as.numeric } }
  
  #### Formatando o output
  rownames(df) <- seq(nrow(df))
  names(df)    <- nms

  #### Preenchendo o data.frame para as datas faltantes
  fill_dates <- data.frame(datas = seq(from=as.Date(head(df$datas, 1)), 
                                       to=as.Date(tail(df$datas, 1)), by="day"))
  fill_dates$datas <- fill_dates$datas %>% as.character
  df <- merge(fill_dates, df, by=c("datas"), all=TRUE)
  df <- df_filler(df)
  
  #### Repetindo o ultimo valor de preco do atacado para calcular o carrego da variacao de preco
  if (carrego == TRUE){ 
    car_df <- tail(df, 30) 
    car_df$datas <- car_df$datas %>% as.Date
    car_df$datas <- car_df$datas + 30
    car_df$datas <- car_df$datas %>% as.character
    for (i in 2:ncol(df)){ car_df[,i] <- tail(car_df[,i],1) }
    df <- rbind(df, car_df)}
  
  #### Extraindo a media movel dos precos
  if (length(mm.days) != 0){
    mmdf <- df;  mmdf[,-1] <- NA
    for (i in mm.days:nrow(mmdf)){  
      if (ncol(mmdf) == 2) { mmdf[i, -1] <- mean(df[c(i:(i-mm.days+1)), -1])
      } else {mmdf[i, -1] <- colMeans(df[c(i:(i-mm.days+1)), -1])  }}
    df <- mmdf}
  
  #### Extraindo diferenca de 30 dias da media movel dos precos
  if (length(mm.days) != 0 & varp30==TRUE){
    var30df <- df;  var30df[,-1] <- NA
    days <- mm.days + 30
    for (i in days:nrow(var30df)){  var30df[i, -1] <- 100*(df[i, -1] - df[(i-days+1), -1])/df[(i-days+1), -1]  }
    df <- var30df}
  
  df <- df[which(as.character(df$datas) > initial.date), ]
  return(df)}
