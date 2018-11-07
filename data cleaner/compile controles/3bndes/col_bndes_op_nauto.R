#install.packages("readxl")
#install.packages("dplyr")
library(readxl)
library(dplyr)

rm(list=ls())
setwd("E:/Dissertacao/DADOS")

muns <- read.csv("base_cods.csv", sep =";")

bndes <- read_xlsx("04.Controles/03.BNDES(02-17)/ops_dir_ind_nauto_02_17.xlsx", skip=4, sheet=1)
bndes <- as.data.frame(bndes[,names(bndes) %in% c("Município - código","Data da Contratação","Valor Contratado  R$",
                                                   "Subsetor CNAE Agrupado")])
names(bndes) <- c("cod_mun","ano","ops_nauto","setor")
bndes[,"ano"] <- as.numeric(substring(as.character(bndes[,"ano"]),1,4))
bndes$cod_mun <- as.numeric(bndes$cod_mun)
bndes <- bndes[-which(bndes$cod_mun == 0),]

base <- bndes %>% group_by(cod_mun,ano) %>% select(ops_nauto) %>% summarise(tops_nauto=sum(ops_nauto)) %>% as.data.frame
####### Adding missing grouping variables: `cod_mun`, `ano`
base$cod_mun <- trunc(base$cod_mun/10)

### É possível ainda construir a variável de financiamento por setor

#### Balanceando a base
cod_mun <- rep(unique(muns$cod_mun), times =length(unique(base$ano)))
ano <- rep(unique(base$ano),         each =length(unique(muns$cod_mun)))
bal <- data.frame(cod_mun,ano)
base <- merge(bal, base, all.x=TRUE)
base$tops_nauto[is.na(base$tops_nauto)] <- 0

write.csv(base, "base_ops_nauto.csv", row.names=FALSE)