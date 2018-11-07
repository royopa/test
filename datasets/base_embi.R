setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1994/4/1"), as.Date("2018/9/1"), by = "quarter")
#### Risco país EMBI - JP Morgan (MCM)
embi <- as.data.frame(read_excel("MFIEMBI0.xls", sheet = "Risco país - EMBI", skip = 2))
names(embi) <- c("date", "embi_br", "embi_br_end", "embi_arg", "embi_arg_end", 
                 "embi_mex", "embi_mex_end", "embi_peru", "embi_peru_end", "embi_col", 
                 "embi_col_end", "embi_ven", "embi_ven_end", "embi_equa", "embi_equa_end", 
                 "embi_chi", "embi_chi_end", "embi_pan", "embi_pan_end", "embi_rus", 
                 "embi_rus_end", "embi_tur", "embi_tur_end", "embi_pol", "embi_pol_end", 
                 "embi_bul", "embi_bul_end", "embi_fil", "embi_fil_end", "embi_mar", "embi_mar_end", 
                 "embi_nig", "embi_nig_end", "embi_indo", "embi_indo_end", "embi_egi", "embi_egi_end", 
                 "embi_mala", "embi_mala_end", "embi_afsul", "embi_afsul_end", "embi_ucr", 
                 "embi_ucr_end", "embi_chi", "embi_chi_end", "embi_sem_arg", "embi_sem_arg_end", 
                 "embi_strip", "embi_strip_end", "embi_latam", "embi_latam_end", 
                 "embi_sob", "embi_sob_end")
embi <- embi[1:(which(embi[,1] == "MÉDIA DO ANO")-1),]
for (i in 2:dim(embi)[2]){
  embi[which(embi[,i] == "-"),i] <- 0
  embi[which(embi[,i] == "nd"),i] <- 0
  embi[,i] <- as.numeric(embi[,i])}
embi$date <- seq(as.Date("1994/4/1"), as.Date("2018/9/1"), by = "month")
embi <- embi[which(embi$date %in% t), ]
