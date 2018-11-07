rm(list=ls())
setwd("E:/Dissertacao/DADOS/04.Controles")

idade_max <- 28
elg <- read.csv(file="01.CadUnico(07)/elg_2007.csv", 
                header=TRUE, sep=";", dec = ",")
elg <- elg[, 1:(3+idade_max)]
n <- (dim(elg)[2] -3) /4

# ajusando o identificador de município
elg[, 1] <- trunc(elg[, 1]/10) 
elg1 <- elg[, 1:2]

for (i in 1: n){
  if (i ==1){elg1[, i+2] <- rowSums(elg[, (4*i-1):(4*i+3)])}
    else {elg1[, i+2] <- rowSums(elg[, (4*i):(4*i+3)])}}

elg1$pretreat <- rowSums(elg[,3:5])
elg1$postreat <- rowSums(elg[,7:9])
# Faixas etárias são: 0-4, 5-8, 9-12, 13-16...
#elg <- elg1[,1: (n+2)]
nomes<- c("cod_mun", "ano", "ft1", "ft2", "ft3", "ft4", "ft5", 
          "ft6", "ft7", "preft4", "posft4")
names(elg1) <- nomes

# empilhando para construir a matriz diagonal
anos <- 2004:2011
for (i in anos){
  elg1[,"ano"] <- i
  if (i ==anos[1]){
    elg <- elg1}
    else {elg <- rbind(elg,elg1)}}

j <- which(anos ==2008)
n <- (-j+1):(length(anos)-j)
n <- sub("-","_",n)
elg0 <- elg
for (t in 1:length(anos)){
  elg1 <- elg
  elg1[elg1$ano != anos[t], 3:dim(elg1)[2]] <- 0
  names(elg1)[3:length(elg1)] <- paste0(nomes[3:length(nomes)],n[t])
  elg0 <- cbind(elg0, elg1[,3:dim(elg1)[2]])}

write.csv(elg0, "base_elg.csv", row.names=FALSE)
write.csv(elg[elg$ano ==2007,], "CadUnico/ft_2007.csv", row.names=FALSE)
