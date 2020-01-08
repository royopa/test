library(readxl)
library(dplyr)
library(lubridate)

#### Resultado Primario do Governo Federal (retirado da MCM)
path_data <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Base de Dados/" 
sup <- as.data.frame(read_excel(paste0(path_data,"MCM/FINAJUST0.xls"), sheet="Resultado Primario Ajustado", skip=1))
sup <- sup[1:(which(sup[,1]==
          "Nome da Série: Resultado Primário Ajustado por Receitas e Despesas Extraordinárias - Em % do PIB")-2),]

names(sup) <- c("datas", "result_prim_cons", "result_prim_ajust")
sup$result_prim_cons  <- 100*sup$result_prim_cons
sup$result_prim_ajust <- 100*sup$result_prim_ajust

sup$datas <- sup$datas %>% as.numeric %>% as.Date(origin="1899-12-30") %>% as.character

