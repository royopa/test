library(ggplot2)
library(mFilter)
library(dplyr)

source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Juro_Neutro_BR/Natural_Rate_OLS/compile_df.R")
#source("F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/functions/lag.R")

#### Dummies de Presidente (para representar credibilidade do BC no periodo)
df_mm$D_reces <- df_mm$D_dilma <- df_mm$D_lula <- 0
id_L <- which(year(df_mm$datas) %in% c(2008:2010)); df_mm$D_lula[id_L] <- 1
id_D <- which(year(df_mm$datas) %in% c(2011:2016)); df_mm$D_dilma[id_D] <- 1
id_R <- which(year(df_mm$datas) %in% c(2015,2016)); df_mm$D_reces[id_R] <- 1
############################################################################


adj.fitted = function(model){  est <- model$fitted.values - model$coefficients[2]*df_mm$D_reces[-c(1,2,3)]}
ext.coefs  = function(model){  coefs <- model$coefficients[3:6]  }

estimation = function(regressores){  
          reg <- lm(as.formula(paste0("jrr_ante ~ D_reces + ", paste0(regressores, collapse="+"))), data=df_mm)  }

all.ests <- function(fiscal, usa){
  reg11 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "pib_pot") %>% estimation
  reg12 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "tx_poup") %>% estimation
  reg13 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "ind_termos") %>% estimation
  reg14 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "hiato", "tx_poup") %>% estimation
  reg15 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "hiato", "ind_termos") %>% estimation 
  reg16 <- c(fiscal, usa, "rec_liv_tot_2", "rec_dir_tot_2", "D_dilma", "D_lula", "ind_termos", "tx_poup") %>% estimation

  est11 <- reg11 %>% adj.fitted; est12 <- reg12 %>% adj.fitted; est13 <- reg13 %>% adj.fitted; est14 <- reg14 %>% adj.fitted
  coef11 <- reg11 %>% ext.coefs; coef12 <- reg12 %>% ext.coefs; coef13 <- reg13 %>% ext.coefs; coef14 <- reg14 %>% ext.coefs
  
  est15 <- reg15 %>% adj.fitted; est16 <- reg16 %>% adj.fitted
  coef15 <- reg15 %>% ext.coefs; coef16 <- reg16 %>% ext.coefs

  ests <- cbind(est11, est12)#, est13)#, est14, est15, est16) 
  coefs <- cbind(coef11, coef12)#, coef13)#, coef14, coef15, coef16) %>% apply(MARGIN=1, FUN=mean)

  return(list(ests, coefs))}

df_mm <- df_mm[-c(nrow(df_mm), (nrow(df_mm)-1))]


df_mm$div_brut_1           <- c(NA, df_mm$div_brut[-nrow(df_mm)])
df_mm$result_prim_cons_1   <- c(NA, df_mm$result_prim_cons[-nrow(df_mm)])
df_mm$result_prim_ajust_1  <- c(NA, df_mm$result_prim_ajust[-nrow(df_mm)])

df_mm$rec_liv_tot_2  <- c(NA, NA, df_mm$result_prim_cons[-c(nrow(df_mm)-1, nrow(df_mm))])
df_mm$rec_dir_tot_2  <- c(NA, NA, df_mm$result_prim_cons[-c(nrow(df_mm)-1, nrow(df_mm))])

#df_mm$ffer_post      <- lag(df_mm$ffer_post,-2)
#df_mm$fed_funds_eff  <- lag(df_mm$fed_funds_eff,-3)


est1 <- all.ests("result_prim_ajust_1", "ffer_post")[[1]]
est2 <- all.ests("result_prim_ajust_1", "fed_funds_eff")[[1]]
coefs1 <- all.ests("result_prim_ajust_1", "ffer_post")[[2]]
coefs2 <- all.ests("result_prim_ajust_1", "fed_funds_eff")[[2]]

### Divida Bruta esta com sinal trocado
#est3 <- all.ests("div_brut_1", "ffer_post")[[1]]
#est4 <- all.ests("div_brut_1", "fed_funds_eff")[[1]]
#coefs3 <- all.ests("div_brut_1", "ffer_post")[[2]]
#coefs4 <- all.ests("div_brut_1", "fed_funds_eff")[[2]]

estimates <- cbind(est1, est2)#, est3, est4) 
datas <- df_mm$datas[-c(1,2,3)]
med <- max <- min <- df_mm$jrr_ante[-c(1,2,3)]

for (i in 1:nrow(estimates)){med[i] <- median(estimates[i,]); max[i] <- max(estimates[i,]); min[i] <- min(estimates[i,])}

plot_data <- data.frame(datas=datas, med=med, 
                        min=hpfilter(min,freq=4)$trend, max=hpfilter(max,freq=4)$trend)

plot_data$datas <- plot_data$datas %>% as.Date(origin="1970-01-01")
plot_data$suav <- hpfilter(plot_data$med,freq=4)$trend

windows()
ggplot(plot_data, aes(x=datas)) + geom_line(aes(y=med), linetype="dashed") + 
  geom_line(aes(y=suav), color="orange", size=1) + 
  geom_ribbon(aes(ymin=min, ymax=max), alpha=.2) + theme_bw() +
  labs(x="", y="Mediana das Estimações", title=paste0("Estimativa da Taxa Neutra de Juros (", 
                                round(tail(hpfilter(med,freq=4)$trend,1),2)," na ponta)"),
       caption="Fonte: Safra Asset Management") 
