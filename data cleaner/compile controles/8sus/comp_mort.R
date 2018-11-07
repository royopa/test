library(reshape2)

rm(list=ls())
setwd("E:/Dissertacao/DADOS")

muns <- read.csv("base_cods.csv", sep =";")
muns <- muns[,c("cod_mun","meso")]

nat <- read.csv("04.Controles/08.DataSus(00-16)/nat_tot.csv", sep=";", skip=4)
nat <- nat[,-dim(nat)[2]]
names(nat)[2:dim(nat)[2]] <- gsub("X","nat_",names(nat)[2:dim(nat)[2]])
nat[,1] <- as.numeric(substring(nat[,1],0,6))
#### Warning message:
#### NAs introduced by coercion
mort <- read.csv("04.Controles/08.DataSus(00-16)/mtinf_tot.csv", sep=";", skip=3)
names(mort)[2:dim(mort)[2]] <- gsub("X","mort_",names(mort)[2:dim(mort)[2]])
mort[,1] <- as.numeric(substring(mort[,1],0,6))
#### Warning message:
#### NAs introduced by coercion

names(nat)[1] <- names(mort)[1] <- "cod_mun"

base <- merge(nat, mort, by="cod_mun")
for (i in 1:dim(base)[2]){base[,i] <- as.numeric(as.character(base[,i]))}
#### There were 32 warnings (use warnings() to see them)
base <- merge(base, muns, by="cod_mun")
base <- base[,-dim(base)[2]]

base <- reshape(base, varying =names(base)[2:dim(base)[2]],
                      direction="long", idvar="cod_mun", sep="_")
base$mort[is.na(base$mort)] <- 0
base$p_mtinf <- base$mort / (base$nat + base$mort)
base <- base[,c(1,2,5)]

names(base) <- c("cod_mun","ano","p_mtinf")

write.csv(base, "04.Controles/base_mort.csv", row.names=FALSE)
