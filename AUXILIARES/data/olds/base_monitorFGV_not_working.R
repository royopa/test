#### Esta funcao usa a serie de variacoes do monitor da FGV para criar n.os indice de seus itens para observar 
#### o nivel dos preços
library(dplyr)

base.monitor = function(initial_date, itens, media = TRUE){
  ### x eh a data de início da serie de n.o criada a partir dos subitens Monitor
  ### itens sao os itens q queremos coletar do Monitor
  source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/functions/df_filler.R", echo=TRUE)
  if (media == TRUE){
    monitor <- read.csv("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/3.MonitorFGV/bases/base_monitor_fgv_media.csv")
  } else {
    monitor <- read.csv("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/3.MonitorFGV/bases/base_monitor_fgv_ponta.csv")}
  initial_date <- as.Date(initial_date, format="%Y-%m-%d")
  
  # coletando os codigos dos itens e as datas de observacao para montar a matriz final posteriormente
  cods <- paste0("c", monitor[,1])
  dts <- gsub("X","", names(monitor)[-c(1,2)]) %>% as.Date(format="%d.%m.%Y")
  
  # excluindo as colunas de codigo e descricao do data.frame
  monitor <- monitor[,-c(1,2)] %>% t() %>% as.data.frame() 
  # reincluindo os codigos dos itens e as datas de observacao
  names(monitor) <- cods; monitor$data <- dts
  monitor <- monitor[, c(ncol(monitor), (1:ncol(monitor)-1))]
  
  # preenchendo as datas que faltam no monitor e repetindo valores nos campos das observacoes
  monitor <- monitor[monitor$data > initial_date, ]
  full_dates <- data.frame(data=seq(from=initial_date, to=tail(monitor$data, 1), by = "day"))
  monitor <- merge(monitor, full_dates, by=c("data"), all=TRUE)
  monitor <- df_filler(monitor)

  return(monitor)}
