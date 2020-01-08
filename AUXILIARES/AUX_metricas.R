library(lubridate)

#################################################################
#######################  CORE VARIATIONS  #######################
#################################################################


# variação month-over-month de numero indice com output em frequencia mensal
MoM <- function(df, yoy=FALSE){
  mom <- df;  mom[,-1] <- NA
  if (yoy == TRUE) {step <- 12} else {step <- 1}
  
  if (ncol(df) == 2){
    for (i in (step +1):nrow(df)){  
      mom[i,2] <- sum(df[i,2]) / sum(df[(i-step),2]) -1  }
  } else {
    for (i in (step +1):nrow(df)){  
      mom[i,-1] <- colSums(df[i,-1]) / colSums(df[(i-step),-1]) -1  }  }
  return(mom)}


# variação quarter-over-quarter (variacao das media trimestre) 
# de numero indice com output em frequencia trimestral
QoQ <- function(df, yoy=FALSE){
  lst_month <- tail(month(df$datas),1)
  
  # estendendo o tamanho do data.frame para gerar a media trimestral
  # parcial quando o trimestre ainda não acabou
  if (lst_month %in% c(1,4,7,10)){
    df <- df[c(1:nrow(df),nrow(df),nrow(df)),]
    df$datas <- seq(as.Date(df$datas[1]), by="month", length.out = nrow(df))
  } else if (lst_month %in% c(2,5,8,11)){
    df <- df[c(1:nrow(df),nrow(df)),]
    df$datas <- seq(as.Date(df$datas[1]), by="month", length.out = nrow(df))}
  
  qoq <- df;  qoq[,-1] <- NA
  if (yoy == TRUE) {step <- 14} else {step <- 5}
  if (ncol(df) == 2){
    for (i in (step +1):nrow(df)){  
      qoq[i,2] <- mean(df[c(i:(i-2)),2]) / mean(df[c((i-(step -2)):(i-step)),2]) -1  }
  } else {
    for (i in (step +1):nrow(df)){  
      qoq[i,-1] <- colMeans(df[c(i:(i-2)),-1]) / colMeans(df[c((i -(step -2)):(i-step)),-1]) -1  }  }
  
  # selecionando apenas os meses de fim de trimestre
  id_dts <- which(month(qoq$datas) %in% c(3,6,9,12))
  qoq <- qoq[id_dts, ]
  
  # reajustando a última data do data.frame para considerar o caso da media trimestral parcial 
  if (lst_month %in% c(1,4,7,10)){ month(qoq$datas[nrow(qoq)]) <- tail(month(qoq$datas),1) - 2
  } else if (lst_month %in% c(2,5,8,11)){ month(qoq$datas[nrow(qoq)]) <- tail(month(qoq$datas),1) - 1}

  return(qoq)}


# variacao YTD de dados mensais em nivel ou em taxa
YTD <- function(df, rate=FALSE){
  dts <- as.Date(df[,1], format="%Y-%m-%d"); ids <- which(month(dts) == 1)
  ytd <- df;  ytd[,-1] <- NA
  if (rate == FALSE){
    for (i in 1:nrow(df)){ ytd[i,-1] <- df[i, -1] / df[(ids[max(which(i >= ids))]), -1] -1  }
  } else {
    for (i in 1:nrow(df)){ 
      ytd[i,-1] <- apply(df[c(i:(ids[max(which(i >= ids))])), -1], 2, function(x){prod(x+1)}) -1  }  }
  return(ytd)}



#################################################################
#################################################################
#################################################################


#################################################################
###################  CORE MOVING AVERAGES  ######################
#################################################################


# media movel X periodos de dados mensais com output em frequencia diaria
MM <- function(df, periods=30){
  mm <- df;  mm[,-1] <- NA
  if (ncol(df) == 2){    
    for (i in periods:nrow(df)){  mm[i,2] <- mean(df[c(i:(i-(periods-1))),2])  }
  } else {    
    for (i in periods:nrow(df)){  mm[i,-1] <- colMeans(df[c(i:(i-(periods-1))),-1])  }  }
  return(mm)}


#################################################################
#################################################################
#################################################################


#mm3mMoM <- function(df){
#  mm3mmom <- df;  mm3mmom[,-1] <- NA
#  if (ncol(df) == 2){
#    for (i in 4:nrow(df)){  
#      mm3mmom[i,2] <- sum(df[c(i:(i-2)),2]) / sum(df[c((i-1):(i-3)),2]) -1  }
#  } else {
#    for (i in 4:nrow(df)){  
#      mm3mmom[i,-1] <- colSums(df[c(i:(i-2)),-1]) / colSums(df[c((i-1):(i-3)),-1]) -1  }  }
#  return(mm3mmom)}


#mm12mMoM <- function(df){
#  mm12mmom <- df;  mm12mmom[,-1] <- NA
#  if (ncol(df) == 2){
#    for (i in 13:nrow(df)){  
#      mm12mmom[i,2] <- sum(df[c(i:(i-11)),2]) / sum(df[c((i-1):(i-12)),2]) -1  }
#  } else {
#    for (i in 13:nrow(df)){  
#      mm12mmom[i,-1] <- colSums(df[c(i:(i-11)),-1]) / colSums(df[c((i-1):(i-12)),-1]) -1  }  }
#  return(mm12mmom)}


#mm3mYoY <- function(df){
#  mm3myoy <- df;  mm3myoy[,-1] <- NA
#  if (ncol(df) == 2){
#    for (i in 13:nrow(mm3myoy)){  
#      mm3myoy[i,2] <- sum(df[c(i:(i-2)),2]) / sum(df[c((i-12):(i-14)),2]) -1  }
#  } else {
#    for (i in 15:nrow(mm3myoy)){  
#      mm3myoy[i,-1] <- colSums(df[c(i:(i-2)),-1]) / colSums(df[c((i-12):(i-14)),-1]) -1  }  }
#  return(mm3myoy)}


#mm12mYoY <- function(df){
#  mm12myoy <- df;  mm12myoy[,-1] <- NA
#  if (ncol(df) == 2){
#    for (i in 24:nrow(mm12myoy)){  
#      mm12myoy[i,2] <- sum(df[c(i:(i-11)),2]) / sum(df[c((i-12):(i-23)),2]) -1  }
#  } else {
#    for (i in 24:nrow(mm12myoy)){  
#      mm12myoy[i,-1] <- colSums(df[c(i:(i-11)),-1]) / colSums(df[c((i-12):(i-23)),-1]) -1  }  }
#  return(mm12myoy)}


################### CORRIJO PARA NOVA FORMATACAO DEPOIS
#######################################################################################
#######################################################################################
# valor acumulado por X periodos
Acum <- function(df, periods=12){
  acum <- df;  acum[,-1] <- NA
  for (i in periods:nrow(acum)){  
    acum[i,-1] <- apply(df[c(i:(i-(periods-1))), -1], 2, function(x){prod(x+1)}) -1  }
  return(acum)}


# media do ano ate o mes em questao
AnAve <- function(df){
  dts <- as.Date(df[,1], format="%Y-%m-%d"); ids <- which(month(dts) == 1)
  myear <- df;  myear[,-1] <- NA
  if (ncol(df) == 2){
    for (i in 1:nrow(myear)){  
      myear[i,-1] <- mean(df[c(i:(ids[max(which(i >= ids))])), -1])  }
  } else {
    for (i in 1:nrow(myear)){  
      myear[i,-1] <- colMeans(df[c(i:(ids[max(which(i >= ids))])), -1])  }  }
  return(myear)}


ytd_ave <- function(df){
  dts <- as.Date(df[,1], format="%Y-%m-%d"); ids <- which(month(dts) == 1)
  ytd_ave <- df; ytd_ave[,-1] <- NA
  for (i in 13:nrow(ytd_ave)){  
    ytd_ave[i,-1] <- df[i, -1] / df[ids[max(which(i >= ids))]-1, -1]  -1}
return(ytd_ave)}




n_ind <- function(df, data="2010-01-01"){
  id <- which(df[,1] == data)
  n_ind <- df;  n_ind[,-1] <- NA
  for (i in 1:nrow(n_ind)){  
    n_ind[i,-1] <- df[i, -1] / df[id,-1]  }
  return(n_ind)}