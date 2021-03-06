#####################     INSTRUCOES
# Goal: essa funcao visa fazer uma projecao em estrutura fixa de uma variavel de interesse,
# possuindo como output nao so a propria projecao mas tambem as estatisticas da projecao
#
# Main Input: 
# df - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao,
# a segunda coluna � a vari�vel de interesse e as outras s�o as vari�veis explicativas
# lags - � um vetor de n.os inteiros de tamanho equivalente ao n.o de variaveis explicativas
# que determina os lags de cada uma delas na regressao
# d.ahoc - vetor de 4 entradas que define pareiodo de dummies adicionais a serem inputadas no modelo
# (e.g. d.ahoc = c(2004,2,2005,3) define dummies de fev/2004 AT� mar/2005)
#
# Main Output: 
# proj - um data.frame com a projecao, o erro de projeca e os dados utilizados para seu calculo 
# stats - um data.frame com os coeficientes de projecao e seus desvios padroes e as significancias.
# Na ultima coluna, temos o R quadrado, stat AIC, stat BIC e stat Loglikelyhood em cada linha
# 
# Secondary Input: 
# year.ahead - qtd de periodos a frente para o qual a projecao � realizada 
# (e.g. o valor default 2 significa q a projecao sera feita ate o final do ano seguinte)
# initial.date - data inicial para o in�cio da regressao dos coeficientes da projecao
# saz.mensal - vetor com meses para dummies sazonais 
# (e.g. saz.mensal = c(2,3) define dummies para fev e mar)
# saz.pres = TRUE define um conjunto de dummeis representativas de cada per�odo presidencial
# saz.anual = TRUE define dummies para cada ano da amostra
# all.data = FALSE utiliza os dados ate o final do ano anterior para a regressao 
# que calcula os coeficientes da projecao
# out.path & filename determinam o caminho e o nome do arquivo aonde os outputs, projecao e 
# estatisticas descritivas da projecao, devem ser salvos em formate xlsx
####################################
library(stats)
library(dplyr)
library(forecast)
library(lubridate)
library(writexl)

proj_trimestral = function(df, lags = rep(0, (ncol(df)-2)), years.ahead = 2, 
                           initial.date = "1996-01-01", all.data = FALSE, 
                           out.path = NULL, filename = NULL){
  
  ###############################   VERIFICACOES & AJUSTES
  #### Verificando se a variavel lags tem tamanho adequado  
  if (length(lags) != (ncol(df) - 2)) 
    stop("length of lags variable must equal to the number of explanatory variables")
  if (!is.Date(as.Date(initial.date))) 
    stop("initial.date must follow the format 'yyyy-mm-dd'")
  initial.date <- as.Date(initial.date)

  ###############################   ARRUMANDO O DATA.FRAME PARA ESTIMACAO E PROJECAO
  df <- df[which(df$datas >= initial.date), ]
  df <- df[!is.na(df$datas), ]
  df$datas <- df$datas %>% as.Date %>% as.character
  #### Completando a ultima linha com zeros, caso haja informacao indisponivel
  if (length(which(is.na(df[nrow(df),]))) != 0){ 
    #flag_incomplete_data <- TRUE
    df[nrow(df), 2] <- 0
    df[nrow(df), is.na(df[nrow(df),])] <- 0}
  
  in_year  <- min(year(df$datas), na.rm = TRUE)
  end_year <- max(year(df$datas), na.rm = TRUE) - 1
  
  #### Criando o espaco de projecao 24 meses a frente
  df12m <- tail(df, years.ahead*4)
  df12m$datas <- df12m$datas %>% as.Date
  year(df12m$datas) <- year(df12m$datas) + years.ahead
  df12m$datas <- df12m$datas %>% as.character
  df12m[,-1] <- 0
  
  #### Empilhando na matriz de dados com a matriz de projecao
  df <- rbind(df, df12m)
  df <- df[which(year(df$datas) <= end_year + 2), ]
  # cortando o data.frame no final do ano seguinte
  
  #### Deslocando as vari�veis explicativas do DF para reproduzir os lags desejados 
  for (i in 1:(length(lags))){ 
    if (lags[i] != 0){ df[, i +2] <- c(rep(NA, lags[i]), df[-c(as.numeric(nrow(df)-lags[i]+1):nrow(df)), i +2]) } }

  names(df) <- paste0(names(df), c(rep("",2), paste0(rep("_", length(lags)), lags)))
  df <- df[complete.cases(df), ]

  ###############################   ESCOLHENDO SE QUEREMOS UTILIZAR PARTE OU TODOS OS DADOS PARA ESTIMACAO
  #### Criando as var indicadora para separar a matriz de estimacao e projecao
  #id_all indica a ultima informacao disponivel
  id_all=0 
  for (i in 1:10){
    id_all <- which(df[, 2] == 0)[i] 
    if (id_all >= (nrow(df) - (24 - month(today())))){break} }
  #id_fix indica a ultima informacao do ultimo ano
  id_fix <- which(year(df$datas) == (end_year+1))[1]
  
  #### Definir a matriz de projecao a partir do data.frame
  if (all.data == TRUE){ id <- id_all
  } else if (all.data == FALSE){ id <- id_fix }

  ###############################   SELECIONANDO DADOS PARA ESTIMACAO E PROJECAO
  #### Selecionando a parcela da matriz de dados construida para o output
  proj  <- df[id_fix:nrow(df), ]
  
  #### Coletando a vari�vel explicada
  yreg  <- df[1:(id-1), 2]           %>% ts(frequency=4, start=c(year(df$datas[1]), month(df$datas[1])/3))
  xreg  <- df[1:(id-1), -c(1,2)]     %>% ts(frequency=4, start=c(year(df$datas[1]), month(df$datas[1])/3))
  pxreg <- df[id:nrow(df), -c(1,2)]  %>% ts(frequency=4, start=c(year(df$datas[id]), month(df$datas[id])/3))

  #### Estimacao
  model <- auto.arima(yreg, xreg=xreg)

  #### Ajuste dos dados para exportacao
  if (all.data == TRUE){ 
    pos <- id_all - id_fix + 1
    prediction <- predict(model, n.ahead = (nrow(proj) - pos + 1), newxreg=pxreg)
    proj[, paste0(names(proj)[2], "_proj")]   <- c(proj[1:(pos-1), 2], prediction$pred %>% round(3))
    proj[, paste0(names(proj)[2], "_projse")] <- c(rep(0,(pos-1)), prediction$se       %>% round(3))      
  } else if (all.data == FALSE){ 
    #1para o caso que eu fixo os dados de estimacao ao final do ano anterior, 
    #decidi "jogar fora" as estimativas para o in�cio do ano corrente para as quais
    #os dados conrrentes j� foram disponibilizados
    #2ja nao jogo mais... agora crio duas colunas novas com projecao e erro padrao
    prediction <- predict(model, n.ahead = nrow(proj), newxreg=pxreg)
    proj[, paste0(names(proj)[2], "_proj")]   <- prediction$pred %>% round(3)
    proj[, paste0(names(proj)[2], "_projse")] <- prediction$se   %>% round(3)}
   
  ###############################   EXPORTANDO DADOS
  #### Verificando se a variavel dependente possiu alguma transformacao  
  split <- unlist(strsplit(names(df)[2], "_"))
  #### Transformando a variavel para nivel caso ela estaje em log ou dlog
  if (split[1] == "dl" | split[1] == "l"){
    var_dep <- paste0(split[-1], collapse="_")
    ids <- grep(var_dep, names(proj))
    #transformando a variavel dependente observada em nivel
    proj[, ids[1]] <- ((exp(proj[, ids[1]] %>% as.vector()) - 1) * 100) %>% round(3)
    #transformando a variavel dependente projetada em nivel
    proj[, ids[2]] <- ((exp(proj[, ids[2]] %>% as.vector()) - 1) * 100) %>% round(3)
    #transformando o erro padrao de projecao em nivel, a formula esta em:
    #https://stats.stackexchange.com/questions/123514/calculating-standard-error-after-a-log-transform
    proj[, ids[3]] <- ((proj[, ids[2]])*(1 + .5*(proj[, ids[3]] %>% as.vector())^2)) %>% round(3)
    names(proj)[ids] <- paste0(var_dep, c("", "_proj", "_projse"))}
  
  #### Reordenando as variaveis para exposicao do output
  proj <- proj[, c(1, (ncol(proj) -1):ncol(proj), 2:(ncol(proj) - 2))]
  
  ###############################   ESTATISTICAS DESCRITIVAS
  #### Coletando as estatisticas
  vars  <- model$coef     %>% names
  coefs <- model$coef     %>% round(3)
  stds  <- model$var.coef %>% diag %>% sqrt %>% round(3)
  sigs  <- (coefs / stds) %>% round(3)
  aic   <- model$aic      %>% round(3)
  bic   <- model$bic      %>% round(3)             
  lglk  <- model$loglik   %>% round(3)
  rsq   <- (1 - (t(model$residuals) %*% (model$residuals))/(t(model$x) %*% (model$x))) %>% round(3)
  R2.Aic.Bic.LL  <- c(rsq, aic, bic, lglk, rep(NA, (length(coefs)-4)))
  #agregando as estatisticas
  stat <- as.data.frame(cbind(vars, coefs, stds, sigs, R2.Aic.Bic.LL))

  ###############################   SALVANDO DADOS
  #### Guardando projecao 24 meses a frente e estatisticas do modelo, caso requisitado
  if (!is.null(out.path) & !is.null(filename)){
    write_xlsx(proj, paste0(out.path, "proj_", filename, ".xlsx"), col_names = TRUE)
    write_xlsx(stat, paste0(out.path, "stat_", filename, ".xlsx"), col_names = TRUE)}
  
  return(proj)}
  