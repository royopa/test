correls <- function(dfY, dfX, window=15, ordY, ordX, type="cross"){
  #dfY=ret_mm; dfX=ret_corr
  #invertendo precos de ativos para a variacao representar momentos bull e bear  
  inv <- grep("_tx|_brl", names(dfX));  dfX[, inv] <- -dfX[, inv]
  df <- merge(dfY, dfX, by="datas"); nX <- (ncol(dfX)-1); nY <- (ncol(dfY)-1)

  #calculando as correlacoes
  cor <- matrix(NA, nrow=(ncol(df)-1), ncol=(ncol(df)-1), dimnames=list(names(df)[-1], names(df)[-1]))

  #calculando a matriz de correlacoes
  for (i in 2:ncol(df)){  for (j in 2:ncol(df)){
    cor[i-1,j-1] <- cor(as.numeric(df[,i]), as.numeric(df[,j])) }}
  
  #ordenando as correlacoes
  cor_Y <- cor[1:nY, 1:nY]
  ord_Y <- order(cor_Y[,which(rownames(cor_Y) == ordY)], decreasing = TRUE)
  cor_Y <- round(cor_Y[ord_Y, ord_Y], 2)
  
  cor_X <- cor[(nY + 1):(nY + nX), (nY + 1):(nY + nX)]
  ord_X <- order(cor_X[,which(rownames(cor_X) == ordX)], decreasing = TRUE)
  cor_X <- round(cor_X[ord_X, ord_X], 2)
  
  cor_cross <- cor[1:nY, (nY+1):(nY+nX)]
  cor_cross <- round(cor_cross[ord_Y,], 2)
  cor_cross <- cbind(cor_cross, rowSums(cor_cross[,c("odf23_tx","ibov","spx","usd_brl")])/4)
  colnames(cor_cross)[8] <- "Agreg."
  
  #escolhendo a correlacao output
  if (type == "Y") {out <- cor_Y} else if (type == "X") {out <- cor_X} else {out <- cor_cross}
  
  return(out)}

