rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "01.RAIS/"
### Definindo a quantidade de categorias a variável tem
# Tam1 - 1 a 4 empregadoS   Tam2 - 5 a 9 emps        Tam3 - 10 a 19 emps
# Tam4 - 20 a 49 emps       Tam5 - 50 a 99 emps      Tam6 - 100 a 249 emps
# Tam7 - 250 a 499 emps     Tam8 - 500 a 999 emps    Tam9 - 1000 ou mais emps + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_tamsex_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =3, header=FALSE, sep=";", dec = ",")
    emp$ano <- as.numeric(as.character(emp[which(emp[,1] == "Ano"),3]))
    emp <- emp[1:(which(emp[,1] == "Total")-1),]
    names(emp) <- c("nome",paste0("emp_",paste0(rep(c("tam1", "tam2", "tam3", "tam4", 
                                  "tam5", "tam6", "tam7", "tam8", "tam9","tot"),each=3),c("_masc","_fem","_tot"))),"ano")
    emp <- merge(emp, cod, by=c("nome"))
    ### Reorganizando as colunas
    n <- ncol(emp)
    emp <- emp[, c(n,n-1,2:(n-2))]
    if (i==1){base <- data.frame(matrix(vector(), 0, length(names(emp)),
                    dimnames=list(c(), names(emp))), stringsAsFactors=F)}
    base <- rbind(base, emp)
}

base <- na.omit(base)
base <- base[,-grep("tot",names(base))]

### Forçando as variáveis para o formato numérico
for (j in 3:ncol(base)){base[,j] <- as.numeric(as.character(base[,j]))}
write.csv(base, "base_emp_tamsex.csv",row.names=FALSE)
