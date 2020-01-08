#####################     INSTRUCOES
# Goal: essa funcao visa fazer uma projecao em estrutura fixa de uma variavel de interesse,
# possuindo como output nao so a propria projecao mas tambem as estatisticas da projecao
#
# Main Input: 
# df - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao,
# a segunda coluna é a variável de interesse e as outras são as variáveis explicativas
# lags - é um vetor de n.os inteiros de tamanho equivalente ao n.o de variaveis explicativas
# que determina os lags de cada uma delas na regressao
# d.ahoc - vetor de 4 entradas que define pareiodo de dummies adicionais a serem inputadas no modelo
# (e.g. d.ahoc = c(2004,2,2005,3) define dummies de fev/2004 ATÉ mar/2005)
#
# Main Output: 
# proj - um data.frame com a projecao, o erro de projeca e os dados utilizados para seu calculo 
# stats - um data.frame com os coeficientes de projecao e seus desvios padroes e as significancias.
# Na ultima coluna, temos o R quadrado, stat AIC, stat BIC e stat Loglikelyhood em cada linha
# 
# Secondary Input: 
# year.ahead - qtd de periodos a frente para o qual a projecao é realizada 
# (e.g. o valor default 2 significa q a projecao sera feita ate o final do ano seguinte)
# initial.date - data inicial para o início da regressao dos coeficientes da projecao
# saz.mensal - vetor com meses para dummies sazonais 
# (e.g. saz.mensal = c(2,3) define dummies para fev e mar)
# saz.pres = TRUE define um conjunto de dummeis representativas de cada período presidencial
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

proj_mensal = function(df, lags = rep(0, (ncol(df)-2)), years.ahead = 2, initial.date = "1996-01-01",
                       d.adhoc = c(), saz.mensal = c(), saz.pres = FALSE, saz.anual = TRUE, 
                       all.data = FALSE, out.path = NULL, filename = NULL){
  
  ###############################   VERIFICACOES & AJUSTES
  #### Verificando se a variavel lags tem tamanho adequado  
  if (length(lags) != (ncol(df) - 2)) 
    stop("length of lags variable must equal to the number of explanatory variables")
  if (!is.Date(as.Date(initial.date))) 
    stop("initial.date must follow the format 'yyyy-mm-dd'")
  initial.date <- as.Date(initial.date)
  #### Ajustando as dummies de sazonalidade mensal
  saz.mensal <- unique(saz.mensal)
  if (length(saz.mensal) == 12){
    saz.mensal <- saz.mensal[-which(saz.mensal > 11)]
  } else if (length(saz.mensal) < 12){
    saz.mensal <- saz.mensal[-which(saz.mensal > 12)]  }

  ###############################   ARRUMANDO O DATA.FRAME PARA ESTIMACAO E PROJECAO
  df <- df[which(df$datas >= initial.date), ]
  df <- df[!is.na(df$datas), ]
  #### Completando a ultima linha com zeros, caso haja informacao indisponivel
  if (length(which(is.na(df[nrow(df),]))) != 0){ 
    #flag_incomplete_data <- TRUE
    df[nrow(df), 2] <- 0
    df[nrow(df), is.na(df[nrow(df),])] <- 0}
  
  in_year  <- min(year(df$datas), na.rm = TRUE)
  end_year <- max(year(df$datas), na.rm = TRUE) - 1
  
  #### Criando o espaco de projecao 24 meses a frente
  df12m <- tail(df, years.ahead*12)
  df12m$datas <- df12m$datas %>% as.Date
  year(df12m$datas) <- year(df12m$datas) + years.ahead
  df12m$datas <- df12m$datas %>% as.character
  df12m[,-1] <- 0
  
  #### Empilhando na matriz de dados com a matriz de projecao
  df <- rbind(df, df12m)
  df <- df[which(year(df$datas) <= end_year + 2), ]
  # cortando o data.frame no final do ano seguinte
  
  #### Deslocando as variáveis explicativas do DF para reproduzir os lags desejados 
  for (i in 1:(length(lags))){ 
    if (lags[i] != 0){ df[, i +2] <- c(rep(NA, lags[i]), df[-c((nrow(df)-lags[i]+1):nrow(df)), i +2]) } }

  names(df) <- paste0(names(df), c(rep("",2), paste0(rep("_", length(lags)), lags)))
  df <- df[complete.cases(df), ]

  ###############################   CRIANDO DUMMIES
  #### Criando dummies para sazonalidade mensal
  if (length(saz.mensal) != 0){
    for (i in saz.mensal){
      df[, paste0("D_m", i)] <- 0
      df[month(df$datas) == i, paste0("D_m",i)] <- 1} }
  
  #### Criando dummies para sazonalidade presidencial  
  if (saz.pres == TRUE){
    pres <- c("D_FHC1", "D_FHC2", "D_LULA1", "D_LULA2", "D_DIL1", "D_DIL2", "D_TEMER")
    df[, pres] <- 0  
    df[year(df$datas) > 1994 & year(df$datas) <= 1998, "D_FHC1"]  <- 1
    df[year(df$datas) > 1998 & year(df$datas) <= 2002, "D_FHC2"]  <- 1
    df[year(df$datas) > 2002 & year(df$datas) <= 2006, "D_LULA1"] <- 1
    df[year(df$datas) > 2006 & year(df$datas) <= 2010, "D_LULA2"] <- 1
    df[year(df$datas) > 2010 & year(df$datas) <= 2014, "D_DIL1"]  <- 1
    df[year(df$datas) > 2014 & year(df$datas) <= 2016, "D_DIL2"]  <- 1
    df[year(df$datas) > 2016 & year(df$datas) <= 2018, "D_TEMER"] <- 1
    #excluindo as dummies criadas que ficaram zeradas devido ao spam de tempo,
    #para evitar multicolinearidade
    for (i in 1:lenth(pres)){ 
      pres_id <- which(names(df) == pres[i])
      if (length(which(df[, pres_id] == 1)) == 0) {df <- df[, -pres_id]} } }

  #### Criando dummies para sazonalidade anual
  if (saz.anual == TRUE & saz.pres == FALSE){
    end_year_loop <- end_year - 1
    #subtraimos 2 do ano final para evitar a multicolinearidade 
    #entre as variaveis e permitir q o ultimo seja inteiro projetado
    for (i in in_year:end_year_loop){
      df[, paste0("D_y", i)] <- 0
      df[year(df$datas) == i, paste0("D_y",i)] <- 1} }
  
  #### Criando dummies adhoc
  if (length(d.adhoc) != 0){
    d_year_init = d.ahoc[1]; d_month_end = d.ahoc[2]
    d_year_end = d.ahoc[3];  d_month_end = d.ahoc[4]

    df[year(df$datas) >= d_year_init & month(df$datas) >= d_month_init & 
         year(df$datas) <= d_year_end & month(df$datas) <= d_month_end, "D_adhoc"] <- 1 } 
  
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
  
  #### Coletando a variável explicada
  yreg  <- df[1:(id-1), 2]           %>% ts(frequency=12, start=c(year(df$datas[1]), month(df$datas[1])))
  xreg  <- df[1:(id-1), -c(1,2)]     %>% ts(frequency=12, start=c(year(df$datas[1]), month(df$datas[1])))
  pxreg <- df[id:nrow(df), -c(1,2)]  %>% ts(frequency=12, start=c(year(df$datas[id]), month(df$datas[id])))

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
    #decidi "jogar fora" as estimativas para o início do ano corrente para as quais
    #os dados conrrentes já foram disponibilizados
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
  
  #### Excluindo as dummies criadas do output final
  proj <- proj[, -grep("D_", names(proj))]
  
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
  