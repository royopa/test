#####################     INSTRUCOES
# Goal: essa funcao visa fazer uma regressao de janela movel de uma lista de variaveis de 
# interesse num mesmo grupo de variaveis explicativas
#
# Main Input: 
# dfY - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao
# e as outras são as variável de interesse semelhantes
# dfX - um data.frame cuja primeira coluna devem ser datas em formate de texto padrao
# e as outras são as variável de explicativas
#
# Main Output: 
# OUTS - uma lista de data.frames com o r quad da regressao, as correlacoes entre as variaveis, 
# os coeficientes, seus desvios padroes, estatisticas t e valores p
# 
# Secondary Input: 
# initial.date - data inicial para o início da regressao dos coeficientes da projecao
# out.path & filename determinam o caminho e o nome do arquivo aonde os outputs, projecao e 
# estatisticas descritivas da projecao, devem ser salvos em formate xlsx
####################################
library(dplyr)

rolling_reg <- function(dfY, dfX, window){
  OUTS <- list() 
  
  #iterando nas variaveis explicativas
  for (i in 2:ncol(dfY)){
    #setando o conjunto de dados para as regressoes e a formula
    fundo <- names(dfY)[i]
    df <- merge(dfY[, c(1,i)], dfX, by=c("datas"))
    form  <- paste0(names(df)[2], "~", paste0(names(df)[3:ncol(df)], collapse="+"))
  
    for (j in 1:(nrow(df) - window)){
      #setando a particao do data.frame a ser utilizada na regressao
      data  <- df[j:(j + window), ]
      model <- lm(as.formula(form), data)
    
      #coletando as informacoes de interesse da relloing regression (coef e desv pad)
      coef  <- summary(model)[[4]][-1, 1] %>% round(digits=3); names(coef) <- paste0(names(coef),"_coef")
      std   <- summary(model)[[4]][-1, 2] %>% round(digits=3); names(std)  <- paste0(names(std),"_std")
      
      #construindo a matriz que constituira cada elemente do output
      if (j == 1){ out <- c(coef, std) } else { out <- rbind(out, c(coef, std)) }}
    
    #formatando o data.frame que constituira cada elemente do output
    out <- out %>% as.data.frame
    out$datas <- tail(df$datas, (nrow(df) - window))
    out <- out[, c(ncol(out), 1:(ncol(out) -1))]
    rownames(out) <- seq(nrow(out))
    
    #adicionando a lista de outputs
    OUTS[[fundo]] <- out}
  
  return(OUTS)}
    
    
    

