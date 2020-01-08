source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEAGESP.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_CEPEA.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_MonitorFGV.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/estimadores/EST_reg_allY_multX.R", echo=TRUE)
library(lubridate)

horizonte_max <- 55
itens_monitor <- c(1101002, 1101073, 1102, 1103003, 1103028, 1103043, 1103044, 1106003, 
                   1106008, 1106039, 1106018, 1106028, 1110009, 1110010, 1110044, 1111004)

itens_atacado <- c("arroz", "feijao", "trigo", "batata", "tomate", "cebola", "cenoura", "abacaxi", 
                   "banana", "laranja", "mamao", "uva", "frango", "frango", "ovo", "leite")

itens_cepea <- c("arroz", "trigo", "frango", "leite")

for (k in 1:length(itens_monitor)){
  it_m <- itens_monitor[k]
  it_a <- itens_atacado[k]
  dfY <- readbase_monitor(itens=it_m, media=TRUE, end=FALSE, last=FALSE, tri=FALSE, 
                            initial.date="2012-01-01")
  
  if (it_a %in% itens_cepea){ 
    dfX_all <- readbase_cepea(prods=it_a, initial.date="2012-01-01", mm.days=30, varp30=TRUE)
  } else {dfX_all <- readbase_ceagesp(prods=it_a, initial.date="2012-01-01", mm.days=30, varp30=TRUE)}

  for (j in 1:horizonte_max){
  
    for (i in 2:ncol(dfX_all)){
      dfX <- dfX_all[, c(1,i)]
      alt <- reg_all_mult(dfY, dfX, lag=j+6, initial.date = "2012-01-31")
      varX <- gsub("corr_v1_", "", names(alt)[3])
      names(alt) <- c("varX", "rsq", "corr", "coef", "std", "tstat", "pval")
      alt$varX <- varX
      
      if (j==1 & i==2) {out <- alt} else {out <- rbind(out,alt)}}}
  
  out <- out[out$coef > 0, ]
  
  if (k == 1){  optimal <- out[which.max(out$rsq), c("varX","rsq","coef")]
  } else {  optimal <- rbind(optimal, out[which.max(out$rsq), c("varX","rsq","coef")])}}
  
write_xlsx(optimal, 
           "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/rotinas juliano/prev_monitfgv_media_atac.xlsx", 
           col_names = TRUE)
