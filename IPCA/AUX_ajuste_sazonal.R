library(stats)
library(base)
library(utils)
library(seasonal)

   # Criando uma função do R:
   # Função será rseas(ts), terá como imput uma time series e vai cuspir
   # uma outra time series com o dado dessazonalizado.
   # Dessazonalização será PADRÃO: utilizará o carnaval, mas vai deixar
   # o modelo em aberto para o programa selecionar o melhor fit e retirar
   # outliers.

ajuste_sazonal = function(ts){
   # Pega o arquivo de carnaval
   carnaval = read.delim("F:/DADOS/ASSET/MACROECONOMIA/DADOS/Atividade/Dessazonalizacao/X12/carnaval.txt",
                         sep = "", header = FALSE)
   
   seg = ts(carnaval$V3, start=1990, frequency = 12)
   ter = ts(carnaval$V4, start=1990, frequency = 12)
   qua = ts(carnaval$V5, start=1990, frequency = 12)
   qui = ts(carnaval$V6, start=1990, frequency = 12)
   sex = ts(carnaval$V7, start=1990, frequency = 12)
   sab = ts(carnaval$V8, start=1990, frequency = 12)

   ts_sa = seas(ts, regression.aictest = NULL, xreg = cbind(seg,ter,qua,qui,sex,sab),
   regression.usertype = "td")$data[,"seasonaladj"]
   return(ts_sa)}
