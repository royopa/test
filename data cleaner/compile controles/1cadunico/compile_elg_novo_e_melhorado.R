#install.packages("reshape2")
library(reshape2)
rm(list=ls())
setwd("E:/Dissertacao/Dados/Controles/01.CadUnico(07)/")

datafiles <- list.files(path = "CSV", pattern = "uf_")

for (i in 1:length(datafiles)){
  elg <- read.csv(paste0("CSV/",datafiles[i]))
  if (i==1){base <- data.frame(matrix(vector(), 0, length(names(elg)),
                                      dimnames=list(c(), names(elg))), stringsAsFactors=F)}
  base <- rbind(base, elg)
}

base <- dcast(base, codigo_ibge ~ idade , value= "elegiveis")
base[is.na(base)] <- 0

base$cod_mun <- trunc(base$codigo_ibge/10)
base$eleg_tot <- rowSums(base[,2:159])
base1 <- base[,160:161]

