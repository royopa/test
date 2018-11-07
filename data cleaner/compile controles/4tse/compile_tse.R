#install.packages("foreign")
#install.packages("readstata13")
#install.packages("dplyr"")

library(foreign)
library(readstata13)
library(dplyr)
library(reshape2)
rm(list=ls())
setwd("E:/Dissertacao/DADOS")

data <- read.dta13("04.Controles/04.RDEleitorais(05-18)/votacao_candidato_munzona.dta")
data <- data[data$cod_cargo == 11 & data$cod_resul == 1,]
uf <- c("AC","AL","AM","AP","BA","CE","ES","GO","MA","MG","MS","MT","PA","PB",
          "PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO")
uf_c <- c(12,27,13,16,29,23,32,52,21,31,50,51,15,25,
          26,22,41,33,24,11,14,43,42,28,35,17)
cod <- data.frame(uf,uf_c)
data <- merge(data, cod, by=c("uf"))
data$uf <- data$uf_c

data <- data %>% group_by(cod_mun,uf,ano,turno,cod_sit,desc_sit,npart) %>% select(votos) %>% 
        summarise(tvotos =sum(votos)) %>% as.data.frame()

#### Elimina observações de 1.o turno de cidades que tiveram 2.o turno
turn2 <- which(data$turno ==2)
for (i in length(turn2):1){
        mun <- data$nome_mun[turn2[i]]
        ano <- data$ano[turn2[i]]
        uf <- data$uf[turn2[i]]
        if (length(which(data$nome_mun == mun & data$ano == ano & data$uf == uf & data$turno == 1)) != 0){
        data <- data[-which(data$nome_mun == mun & data$ano == ano & data$uf == uf & data$turno == 1),]}}

#### Elimina candidatos com menos votos de cada eleição... o filtro da base de dados do TSE é cagado
dup <- which(duplicated(data[,1:3]))
for (i in length(dup):1){
        if (data$tvotos[dup[i]] >= data$tvotos[dup[i]-1]) {data <- data[-(dup[i]-1),]}
        else {data <- data[-(dup[i]),]}}

#### Mescla a base com a legenda dos códigos de municipios do TSE/IBGE feita na FUCKING MÃO
cod_tse <- read.csv("Controles/RDEleitorais/cod_tse.csv", header=TRUE, sep=";")
cod_tse <- cod_tse[,c("cod_mun","cod_ibge")]
data <- merge(cod_tse,data, by=c("cod_mun"))
base <- data[,c("cod_ibge","ano","npart","tvotos")]
base$mpart <- 0
base$mpart[which(base$npart == 13)] <- 1
base <- base[order(base$ano),]
base1 <- base2 <- base3 <- base
base1$ano <- base1$ano + 1
base2$ano <- base2$ano + 2
base3$ano <- base3$ano + 3

base <- rbind(base,base1,base2,base3)
base$ano <- base$ano +1

write.csv(base, "base_tse.csv", row.names=FALSE)