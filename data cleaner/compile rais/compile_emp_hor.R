rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "Rais/"
### Definindo a quantidade de categorias a variável tem
n_class <- 6
# Hor1 - ate 12 hora     Hor2 - de 13 a 15 h     Hor3 - de 16 a 20 h 
# Hor4 - de 31 a 40 h    Hor5 - de 41 a 44 h     Hor6 - mais de 44 h + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_hor_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =1, header=TRUE, sep=";", dec = ",")
    emp <- emp[1:(which(emp[,1] == "Total")-1),(1:(n_class+1))]
    names(emp) <- c("nome",paste0("emp_",c("hor1","hor2","hor3","hor4", 
                                  "hor5","hor6")))
    emp$ano <- as.numeric(substring(datafiles[i], 9, 12))
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    emp <- emp[, c((n_class + 3),(n_class + 2),2:(n_class+1))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

### Forçando as variáveis para o formato numérico
for (j in 1:n_class){base[,j+2] <- as.numeric(as.character(base[,j+2]))}
write.csv(base, "base_emp_hor.csv", row.names=FALSE)