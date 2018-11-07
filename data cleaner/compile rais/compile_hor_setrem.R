rm(list=ls())
setwd("F:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_set <- 8; n_rems <- 12
n_class <- n_set*n_rems
# Ativ1 - ext. mineral      Ativ2 - ind. transformaçao     Ativ3 - serv. industriais
# Ativ4 - const. civil      Ativ5 - comercio               Ativ6 - serviços
# Ativ7 - adm. publica      Ativ8 - agropecuaria           + TOTAL

# Rem1 - ate ,5 r$ p/ hora      Rem2 - de ,51 a 1 r$ p/h      Rem3 - de 1,01 a 1,50 r$ p/h 
# Rem4 - de 1,51 a 2 r$ p/h     Rem5 - de 2,01 a 3 r$ p/h     Rem6 - de 3,01 a 4 r$ p/h 
# Rem7 - de 4,01 a 5 r$ p/h     Rem8 - de 5,01 a 7 r$ p/h     Rem9 - de 7,01 a 10 r$ p/h 
# Rem10 - de 10,01 a 15 r$ p/h  Rem11 - de 15,01 a 20 r$ p/h  Rem12 - de 20,01 ou mais r$ p/h 
# Rem13 - {ñ class}             + TOTAL
rems <- c(.5,1,1.5,2,3,4,5,7,10,15,20,30)
#rems <- c(.25,.5,1,1.5,2,3,4,5,7,10,15,20)

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "hor_setrem_")

for (i in 1: length(datafiles)){
    hor <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =2, header=TRUE, sep=";", dec = ",")
    hor <- hor[1:(which(hor[,1] == "Total")-1), 1:which(names(hor)=="Total.7")]
    ### Eliminando a classe rem13 - {ñ class}
    hor <- hor[,-grep("ñ.class",names(hor))]
    hor <- hor[,-grep("Total",names(hor))]
    names(hor) <- c("nome",
                    paste0(rep(c("set1","set2","set3","set4","set5","set6",
                                 "set7","set8"),each=12), 
                           c("rem1","rem2","rem3","rem4","rem5","rem6","rem7",
                             "rem8","rem9","rem10","rem11","rem12")))
    hor$ano <- as.numeric(substring(datafiles[i], 12, 15))
    hor <- merge(hor, cod, by=c("nome"))
    ### Reorganizando as colunas
    hor <- hor[,c((n_class+3),(n_class+2),2:(n_class+1))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(hor)),
                    dimnames=list(c(), names(hor))), stringsAsFactors=F)}
    base <- rbind(base, hor)
}

### Forçando as variáveis para o formato numérico
for (j in 1:n_class){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
### Criando Massa de Salários
mas <- t(t(base[,-c(1,2)]) * rep(rems,times=n_set))
massa <- base[,1:2]

### A base massa agrega apenas a massa de salários por setor
massa$mas_set1 <- rowSums(mas[,1:12]); massa$mas_set2 <- rowSums(mas[,13:24])
massa$mas_set3 <- rowSums(mas[,25:36]); massa$mas_set4 <- rowSums(mas[,37:48])
massa$mas_set5 <- rowSums(mas[,49:60]); massa$mas_set6 <- rowSums(mas[,61:72])
massa$mas_set7 <- rowSums(mas[,73:84]); massa$mas_set8 <- rowSums(mas[,85:96])

#write.csv(base, "base_emp_horrem.csv", row.names=FALSE)
write.csv(massa, "base_mas_set.csv", row.names=FALSE)
