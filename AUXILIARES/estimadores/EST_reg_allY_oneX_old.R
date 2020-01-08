library(stats)
library(dplyr)
library(forecast)
library(lubridate)

reg_all_one = function(df, lags = 0, initial.date = "1996-01-01", out.path = NULL, filename = NULL){

  #### Verificando se a variável lags tem tamanho adequado  
  if (length(lags) != 1) 
    stop("length of lags variable must equal to the number of explanatory variables")
  if (!is.Date(as.Date(initial.date))) 
    stop("initial.date must follow the format 'yyyy-mm-dd'")
  initial.date <- as.Date(initial.date)
  
  df <- df[which(df$datas >= initial.date), ]
  df <- df[!is.na(df$datas), ]
  
  #### Eliminando itens com poucas observacoes por causa de descontinuidade
  #### e substituindo o resto por zeros
  df <- df[, lapply(df, function(x){ length(which(!is.na(x)))}) %>% unlist > (nrow(df)/2 + 50)]
  for (i in 3:ncol(df)){ df[is.na(df[, i]), i] <- 0 }
  
  #### Criando espaco para armazenagem das variaveis
  corr <- coef <- std <- tstat <- pval <- rsq <- c()
  #coletando os nomes das colunas
  vars <- names(df)[-c(1,2)]
  
  for (i in 3:ncol(df)){
    y <- df[, i]; x <- df[, 2]; model <- lm(y ~ x)
    corr  <- c(corr,  cor(y,x, use = "complete.obs") %>% round(digits=3))
    coef  <- c(coef,  summary(model)[[4]][2] %>% round(digits=3))  #coef. angular da reg simples
    std   <- c(std,   summary(model)[[4]][4] %>% round(digits=3))  #desv. pad.
    tstat <- c(tstat, summary(model)[[4]][6] %>% round(digits=3))  #estatistica t
    pval  <- c(pval,  summary(model)[[4]][8] %>% round(digits=3))  #p valor
    rsq   <- c(rsq,   summary(model)[[8]]    %>% round(digits=3))} #r quadrado
  
  #### Agregando estatisticas para a exporatação
  stat <- as.data.frame(cbind(vars, corr, coef, std, tstat, pval, rsq))

  #### Guardando projecao 24 meses a frente e estatisticas do modelo, caso requisitado
  if (!is.null(out.path) & !is.null(filename)){
    write.table(stat, sep=";", dec=",", row.names = FALSE, paste0(out.path, "reg_all_one_", filename, ".csv"))}
  
  return(stat)}
  