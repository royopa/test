#install.packages("readstata13")
library(readstata13)
library(reshape2)

rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles")

base <- read.dta13("05.Programas de Saúde(93-14)/penetracaoPSF_anual.dta")[,1:3]
#### Warning message:
####   In read.dta13("05.Programas de Saúde(93-14)/penetracaoPSF_anual.dta") : 
####   mreg: Factor codes of type double or float detected - no labels assigned (...)
base <- base[,c("cod_mun","ano","d_eSF")]

base <- dcast(base, formula=cod_mun ~ ano, value=d_eSF)
#### Using d_eSF as value column: use value.var to override.
base[,c("2016")] <- base[,c("2015")] <- base[,c("2014")]
names(base)[2:dim(base)[2]] <- paste0("eSF_",names(base)[2:dim(base)[2]])

base <-reshape(base, varying =names(base)[2:dim(base)[2]],
                     direction="long", idvar="cod_mun", sep="_")

base$eSF[is.na(base$eSF)] <- 0
write.csv(base, "base_PSF.csv", row.names=FALSE)