library(readxl); library(dplyr); library(lubridate)

readbase_bbg <- function(wb, sheet, initial.date="2018-12-01", return=FALSE){
  #wb <- "bbg_assets_day"; sheet <- "PX_FxInc_BZ"
  path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/BBG/"
  initial_date <- as.Date(initial.date, format="%Y-%m-%d")
  
  df <- read_excel(paste0(path, wb, ".xlsx"), sheet=sheet) %>% as.data.frame
  #eliminando as primeiras linhas que ficam cagadas na planilha da bbg
  df <- df[-c(1,2),]

  if (is.POSIXct(df$datas[3])){  df$datas <- as.Date(df$datas, tryformat=c("%d/%m/%y","%d/%m/%Y"))
  } else if (is.character(df$datas[3])) { df$datas <- as.Date(as.numeric(df$datas), origin = "1899-12-30") }
  
  for (i in 2:ncol(df)){
    df[which(df[,i] == "#N/A N/A"),i] <- 0; df[,i] <- as.numeric(df[,i])}

  all_col <- 1:ncol(df); rates <- grep("_tx", names(df)); assets <- all_col[!all_col %in% c(1, rates)]
  if (return == TRUE){
    ret <- df[-nrow(df),]; ret[,-1] <- NA
    ret[,rates]  <- df[-1,rates]       - df[-nrow(df),rates]
    ret[,assets] <- log(df[-1,assets]) - log(df[-nrow(df),assets]) 
    df <- ret}
  
  df <- df[df$datas > initial.date,]
  
  return(df)}