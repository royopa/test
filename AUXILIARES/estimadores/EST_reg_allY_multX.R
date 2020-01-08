#####################     INSTRUCOES
# Goal: essa funcao visa fazer uma estimacao de um serie de variaveis de interesse semelhantes 
# em estrutura fixa de variaveis explicativas
#
# Main Input: 
# dfY - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao
# e as outras são as variável de interesse semelhantes
# dfX - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao
# e as outras são as variável de explicativas
# lags - é um vetor de n.os inteiros de tamanho equivalente ao n.o de variaveis explicativas
# que determina os lags de cada uma delas na regressao
#
# Main Output: 
# stats - um data.frame com o r quad da regressao, as correlacoes entre as variaveis, 
# os coeficientes, seus desvios padroes, estatisticas t e valores p
# 
# Secondary Input: 
# initial.date - data inicial para o início da regressao dos coeficientes da projecao
# out.path & filename determinam o caminho e o nome do arquivo aonde os outputs, projecao e 
# estatisticas descritivas da projecao, devem ser salvos em formate xlsx
####################################
library(stats)
library(dplyr)
library(forecast)
library(lubridate)
library(writexl)

reg_all_mult = function(dfY, dfX, lags = rep(0, (ncol(dfX)-1)), 
                        initial.date = "1996-01-01", out.path = NULL, filename = NULL){
  spec_char <- "\\.|\\-|\\/|\\(|\\)| |\\^|\\$|\\?|\\*|\\+|\\[|\\]|\\{|\\}"
  names(dfY) <- gsub(spec_char, "", names(dfY))
  names(dfX) <- gsub(spec_char, "", names(dfX))
  nvar_indep = ncol(dfX)-1
  #### Verificando se a variável lags tem tamanho adequado  
  if (length(lags) != nvar_indep) 
    stop("length of lags variable must equal to the number of explanatory variables in dfX")
  if (!is.Date(as.Date(initial.date))) 
    stop("initial.date must follow the format 'yyyy-mm-dd'")
  initial.date <- as.Date(initial.date)
  
  #### Tomando os valores das variaveis de interesse a partir de uma data inicial
  dfY <- dfY[which(dfY$datas >= initial.date), ];  dfY <- dfY[!is.na(dfY$datas), ]
  dfX <- dfX[which(dfX$datas >= initial.date), ];  dfX <- dfX[!is.na(dfX$datas), ]
  #df <- df[complete.cases(df), ]
  
  #### Eliminando itens com poucas observacoes (<60%) por causa de descontinuidade
  #### e substituindo o resto por zeros
  dfY <- dfY[, lapply(dfY, function(x){ length(which(!is.na(x)))}) %>% unlist > 0.6*(nrow(dfY))]
  for (i in 2:ncol(dfY)){ dfY[is.na(dfY[, i]), i] <- 0 }
  
  #### Deslocando as variáveis explicativas do DF para reproduzir os lags desejados 
  for (i in 1:(length(lags))){ 
    if (lags[i] != 0){ dfX[, i +1] <- c(rep(NA, lags[i]), dfX[-c((nrow(dfX)-lags[i]+1):nrow(dfX)), i +1]) } }
  names(dfX) <- paste0(names(dfX), c(rep("",1), paste0(rep("_", length(lags)), lags)))
  
  #coletando das linhas e das colunas
  var_indep <- names(dfX)[-1]
  vars <- names(dfY)[-1]
  
  #### Gerando as estatisticas para a analise
  for (i in 2:ncol(dfY)){
    df <- merge(dfY[, c(1, i)], dfX, by=c("datas"));   names(df)[2] <- "y"
    model <- lm(as.formula(paste0("y ~ ", paste0(var_indep, collapse="+"))), data=df)
    
    corr  <- cor(df[, 2], df[, 3:ncol(df)], use = "complete.obs") %>% round(digits=3)
    coef  <- summary(model)[[4]][-1, 1] %>% round(digits=3)  #coef. angular da reg simples
    std   <- summary(model)[[4]][-1, 2] %>% round(digits=3)  #desv. pad.
    tstat <- summary(model)[[4]][-1, 3] %>% round(digits=3)  #estatistica t
    pval  <- summary(model)[[4]][-1, 4] %>% round(digits=3)  #p valor
    rsq   <- summary(model)[[8]]        %>% round(digits=3)  #r quadrado
    
    info <- c(rsq, corr, coef, std, tstat, pval)
    
    #### Criando e armazenando as estatísticas  
    if (i == 2) { stat <- matrix(data=info, nrow=1, ncol=length(info))
    } else {      stat <- rbind(stats, info) } }
  
  #### Agregando estatisticas para a exporatação
  stat <- stat %>% as.data.frame
  names(stat) <- c("rsq", paste0(rep(c("corr_", "coef_", "std_", "tstat_", "pval_"), each=nvar_indep), 
                                 rep(paste0("v", 1:nvar_indep, "_"), times=5),
                                 rep(var_indep, times=5)))
  stat <- data.frame(variable=vars, stat)

  #### Guardando projecao 24 meses a frente e estatisticas do modelo, caso requisitado
  if (!is.null(out.path) & !is.null(filename)){
    write_xlsx(stat, paste0(out.path, "reg_all_mult_", filename, ".csv"), col_names = TRUE)}
  
  return(stat)}
  