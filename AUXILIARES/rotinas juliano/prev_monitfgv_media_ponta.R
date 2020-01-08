source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/data/DATA_MonitorFGV.R", echo=TRUE)
source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/estimadores/EST_reg_allY_multX.R", echo=TRUE)
library(lubridate)
library(writexl)

horizonte_max <- 15

itens <- c(1101:1116, 1101051, 1101052, 1101053, 1101073, 1103004, 1103005, 1103017, 1103026, 1103027,
           1103046, 1106001, 1106005, 1106019, 1106020, 1106021, 1106023, 1106027, 1106051, 1111008,
           1111009, 1111011, 1111019, 1111031)

for (k in 1:length(itens)){
  it_m <- itens[k]
  dfY     <- readbase_monitor(itens=it_m, media=TRUE, end=FALSE, last=FALSE, tri=FALSE, 
                              initial.date="2012-01-01")
  dfX_all <- readbase_monitor(itens=it_m, media=FALSE, end=FALSE, last=FALSE, tri=FALSE, 
                              initial.date="2012-01-01")

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
           "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/AUXILIARES/rotinas juliano/prev_monitfgv_media_ponta.xlsx", 
           col_names = TRUE)
