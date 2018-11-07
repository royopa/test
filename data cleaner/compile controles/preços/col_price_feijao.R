#install.packages("readxl")
library(readxl)

rm(list=ls())
setwd("E:/Dissertacao/Dados/Controles")

dataplace <- "Preços/"

yrs <- list.files(path = dataplace, pattern="20")
n_yrs <- length(yrs)

state <- c("Rondônia","Acre","Amazonas","Roraima","Pará","Amapá","Tocantins","Maranhão","Piauí","Ceará",
            "Rio Grande do Norte","Paraíba","Pernambuco","Alagoas","Sergipe","Bahia","Minas Gerais",
            "Espírito Santo","Rio de Janeiro","São Paulo","Paraná","Santa Catarina","Rio Grande do Sul",
            "Mato Grosso do Sul","Mato Grosso","Goiás","Distrito Federal")
uf <- c(11:17,21:29,31:33,35,41:43,50:53)
leg <- data.frame(state,uf)

for (i in 1:n_yrs){
  path0 <- paste0(dataplace, yrs[i], "/")
  arch <- list.files(path = path0, pattern = "eij")
  price <- read_xls(paste0(path0, arch), skip=4, sheet=1)
  price <- as.data.frame(price[3:dim(price)[1],])
  names(price) <- c("state","area_plant","area_col","q_prod","rend",'value')
  price <- price[price$state %in% state,]
  price$ano <- as.numeric(yrs[i])
  price$price <- price$value / price$q_prod
  price <- merge(price, leg, by=c("state"))
  price <- price[,c("uf","ano","price")]
  if (i==1){base <- data.frame(matrix(vector(), 0, length(names(price)),
                                      dimnames=list(c(), names(price))), stringsAsFactors=F)}
  base <- rbind(base, price)
}

### Dados faltantes: uf = 11 para os anos 03
c1 <- c(11, 2003, base$price[base$uf == 12 & base$ano == 2003])
base <- rbind(base, c1)

write.csv(base, paste0(dataplace, "base_feijao.csv"), row.names=FALSE)
