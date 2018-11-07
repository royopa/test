#install.packages("dplyr")
library(dplyr)

rm(list=ls())
setwd("E:/Dissertacao/DADOS")

dataplace <- "04.Controles/03.BNDES(02-17)/"

files <- list.files(path = dataplace, pattern="ops_ind")
n_yrs <- length(files)
muns <- read.csv("base_cods.csv", sep =";")

for (i in 1:n_yrs){
  bndes <- read.csv(paste0(dataplace, files[i]), sep =";")
  bndes <- as.data.frame(bndes[,names(bndes) %in% c("Código.Município","Data.de.contratação",
                                                    "Valor.da.Operação.em.R.","Subsetor.CNAE.Agrupado")])
  names(bndes) <- c("cod_mun","ano","ops_auto","setor")
  bndes[,"ano"] <- as.numeric(substring(as.character(bndes[,"ano"]),7,11))
  if (i==1){base <- data.frame(matrix(vector(), 0, length(names(bndes)),
                                      dimnames=list(c(), names(bndes))), stringsAsFactors=F)}
  base <- rbind(base, bndes)
}

base[,"ops_auto"] <- as.numeric(sub(".","",sub(",","",
                                               as.character(base[,"ops_auto"]),fixed=TRUE),fixed=TRUE))/100
####### Warning message:
#######        NAs introduced by coercion
base[which(is.na(base$ops_auto)),"ops_auto"] <- 0

base <- base[,1:3] %>% group_by(cod_mun,ano) %>% select(ops_auto) %>% summarise(tops_auto=sum(ops_auto)) %>% as.data.frame
####### Adding missing grouping variables: `cod_mun`, `ano`
base$cod_mun <- trunc(base$cod_mun/10)

#### Balanceando a base
cod_mun <- rep(unique(muns$cod_mun), times =length(unique(base$ano)))
ano <- rep(unique(base$ano),         each =length(unique(muns$cod_mun)))
bal <- data.frame(cod_mun,ano)
base <- merge(bal, base, all.x=TRUE)
base$tops_auto[is.na(base$tops_auto)] <- 0

write.csv(base, "04.Controles/base_ops_auto.csv", row.names=FALSE)