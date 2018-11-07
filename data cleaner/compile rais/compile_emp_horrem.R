rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- (6+1)*(12+1)
# Hor1 - ate 12 hora     Hor2 - de 13 a 15 h     Hor3 - de 16 a 20 h 
# Hor4 - de 31 a 40 h    Hor5 - de 41 a 44 h     Hor6 - mais de 44 h + TOTAL
hors <- c(12,15,20,40,44,50)
#hors <- c(6,13,16,31,41,44)

# Rem1 - ate ,5 r$ p/ hora      Rem2 - de ,51 a 1 r$ p/h      Rem3 - de 1,01 a 1,50 r$ p/h 
# Rem4 - de 1,51 a 2 r$ p/h     Rem5 - de 2,01 a 3 r$ p/h     Rem6 - de 3,01 a 4 r$ p/h 
# Rem7 - de 4,01 a 5 r$ p/h     Rem8 - de 5,01 a 7 r$ p/h     Rem9 - de 7,01 a 10 r$ p/h 
# Rem10 - de 10,01 a 15 r$ p/h  Rem11 - de 15,01 a 20 r$ p/h  Rem12 - de 20,01 ou mais r$ p/h 
# Rem13 - {ñ class}             + TOTAL
rems <- c(.5,1,1.5,2,3,4,5,7,10,15,20,30)
#rems <- c(.25,.5,1,1.5,2,3,4,5,7,10,15,20)

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_horrem_")
i<-1
for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =2, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1),]
    ### Eliminando a classe rem13 - {ñ class}
    emp <- emp[,-grep("ñ.class",names(emp))]
    names(emp) <- c("nome",
                    paste0(rep(c("hor1","hor2","hor3","hor4","hor5","hor6","htot"), 
                               each=13), c("rem1","rem2","rem3","rem4","rem5",
                                           "rem6","rem7","rem8","rem9","rem10",
                                           "rem11","rem12","rtot")))
    emp$ano <- as.numeric(substring(datafiles[i], 12, 15))
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    emp <- emp[,c((n_class+3),(n_class+2),2:(n_class+1))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

### Forçando as variáveis para o formato numérico
for (j in 1:n_class){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
### Criando Massa de Salários
base$massa <- rowSums(base[,-c(1,2,grep("tot",names(base)))] * 
                      rep(4*rep(hors,each=12)*rems, each=nrow(base)))

write.csv(base, "base_emp_horrem.csv", row.names=FALSE)