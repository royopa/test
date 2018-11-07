rm(list=ls())
setwd("E:/Dissertacao/Dados")

dataplace <- "01.RAIS/"
### Categorias a variável tem
# Esc1 - analfabeto      Esc2 - 4.a ser incomp   Esc3 - 4.a ser comp 
# Esc4 - 8.a ser incomp  Esc5 - 8.a ser comp     Esc6 - 2.o grau incomp
# Esc7 - 2.o grau comp   Esc8 - mestrado         Esc9 - doutorado + TOTAL

cod <- read.csv(file=paste0(dataplace,"cod_rais.csv"), 
                header=TRUE, sep=";", dec = ",")
datafiles <- list.files(path = dataplace, pattern = "emp_escsex_")

for (i in 1: length(datafiles)){
    emp <- read.csv(file=paste0(dataplace,datafiles[i]), 
                    skip =3, header=FALSE, sep=";", dec = ",")
    ano <- as.numeric(as.character(emp[which(emp[,1] == "Ano"),3]))
    emp$ano <- ano
    emp <- emp[1:(which(emp[,1] == "Total")-1),]
    ### Aqui temos q fazer um ajuste, pois a classificação das veriáveis muda depois de 2005
    ### A partir de 2006 começam a ser contabilizados aqueles que tem Mestrado ou Doutorado Completos
    ### Antes disso, não existe esta classificação, concentrando tais indivíduos em Superior Completo
    if (ano > 2005){
              emp$V20 <- emp$V20 + emp$V23 + emp$V26
              emp$V21 <- emp$V21 + emp$V24 + emp$V27
              emp$V22 <- emp$V22 + emp$V25 + emp$V28
              emp <- emp[,-c(23:28)]}
    names(emp) <- c("nome",paste0("emp_",paste0(rep(c("esc1","esc2","esc3","esc4", 
                                  "esc5","esc6","esc7","esc8","esc9","tot"),each=3),c("_masc","_fem","_tot"))),"ano")
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
write.csv(base, "base_emp_escsex.csv",row.names=FALSE)
