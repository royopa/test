#install.packages("Hmisc")
library(Hmisc)
library(dplyr)
rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "02.PBF/"
datafiles <- list.files(path =dataplace, pattern ="pbf_")
pop <- read.csv(file ="base_pop.csv", header=TRUE, sep=",")
pop$pop <- as.numeric(as.character(pop$pop))
#### Warning message:
####  NAs introduced by coercion 
pop <- pop[complete.cases(pop),]
fam_med <- read.csv(file =paste0(dataplace,"base_med_fam.csv"), header=TRUE, sep=",")

for (i in 1: length(datafiles)){
    pbf <- read.csv(file=paste0(dataplace, datafiles[i]), skip = 7, header=FALSE, sep=";", dec = ",")
    pbf <- pbf[c(-dim(pbf)[1]),c(-1,-2,-4)]
    pbf$ano <- as.numeric(substring(datafiles[i], 5, 8))
    # Jogando a var ANO, craida por último, para a segunda coluna
    pbf <- pbf[, c(1, dim(pbf)[2], 2:(dim(pbf)[2]-1))]
    for (j in 1:dim(pbf)[2]){
    pbf[,j] <- as.numeric(sub(".","",sub(",00","",as.character(pbf[,j]),fixed=TRUE),fixed=TRUE))}
    # vars: cod_mun, ano, (fam, val)x(jan~dez)
    pbf <- pbf[ ,c(1,2,(dim(pbf)[2]-1),dim(pbf)[2])]
    names(pbf) <- c("cod_mun","ano","pbf_fam","pbf_val")
    if (i==1){base <- pbf} else {base <- rbind(base, pbf)}
    }

base <- merge(base, pop, by=c("cod_mun","ano"))
base <- merge(base, fam_med, by=c("cod_mun"))
base <- base[complete.cases(base),]

base$pbf_ind <- base$pbf_fam * base$fam_med
base <- base[,c("cod_mun","ano","pbf_fam","pbf_val","pop","pbf_ind")]

write.csv(base, "base_pbf.csv", row.names=FALSE)