library(reshape2)

rm(list=ls())
setwd("E:/Dissertacao/DADOS")

muns <- read.csv("base_cods.csv", sep =";")
muns <- muns[,c("cod_mun","meso")]

nat <- read.csv("04.Controles/08.DataSus(00-16)/nat_tot.csv", sep=";", skip=4)
names(nat)[2:dim(nat)[2]] <- gsub("X","nat_",names(nat)[2:dim(nat)[2]])
nat <- nat[,c(1,6:dim(nat)[2])]
nat[,1] <- as.numeric(substring(nat[,1],0,6))
#### Warning message:
#### NAs introduced by coercion
nat_edmae <- read.csv("04.Controles/08.DataSus(00-16)/nat_tot_educmae4.csv", sep=";", skip=4)
names(nat_edmae)[2:dim(nat_edmae)[2]] <- gsub("X","nat.educmae_",names(nat_edmae)[2:dim(nat_edmae)[2]])
nat_edmae <- nat_edmae[,-dim(nat_edmae)[2]]
nat_edmae[,1] <- as.numeric(substring(nat_edmae[,1],0,6))
#### Warning message:
#### NAs introduced by coercion 

names(nat)[1] <- names(nat_edmae)[1] <- "cod_mun"

base <- merge(nat, nat_edmae, by="cod_mun")
for (i in 1:dim(base)[2]){base[,i] <- as.numeric(as.character(base[,i]))}
#### There were 34 warnings (use warnings() to see them)
base <- merge(base, muns, by="cod_mun")
base <- base[,-dim(base)[2]]

base <- reshape(base, varying =names(base)[2:dim(base)[2]],
                      direction="long", idvar="cod_mun", sep="_")
base$p_educ <- base$nat.educmae / base$nat
base <- base[,c(1,2,5)]

names(base) <- c("cod_mun","ano","p_educ8")

write.csv(base, "04.Controles/base_nat.csv", row.names=FALSE)
