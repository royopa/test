rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Controles/Preços/"

archs <- list.files(path = dataplace, pattern="base_")
n_archs <- length(archs)
prods <- sub("base_","",sub(".csv","",archs))

for (i in 1:n_archs){
  price <- read.csv(file=paste0(dataplace,archs[i]), header=TRUE, sep=",")
  names(price)[names(price)=="price"] <- paste0("price_",prods[i])
  if (i==1){base <- price}
  else{base <- merge(base, price, by=c("uf","ano"))}}

write.csv(base, "base_preco.csv", row.names=FALSE)