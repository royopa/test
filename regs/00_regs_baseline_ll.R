#install.packages("lfe")
#install.packages("stargazer")
#install.packages("sandwich")
#install.packages("dplyr")
#install.packages("reshape2")
#install.packages("readxl")
#install.packages("Hmisc")
library(lfe)
library(stargazer)
library(dplyr)
rm(list=ls())
setwd("E:/Dissertacao")
tables.dest <- "Tabelas de Resultados/temp/" 

base <- read.csv(file ="BASES/00_base.csv", header=TRUE, sep=",")
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge")
base[,facs] <- lapply(base[,facs],as.factor)

### Seleciona as variáveis a serem Utilizadas nas regressões
base$ID                   <- base$cod_mun
base$TEND <- base$CLUS    <- base$micro
base$ANO                  <- base$ano

base$Y <- log(1 + base$emp_tot)
base$X <- log(1 + base$pbf_fam)
base$Y_quint <- exp(base$Y) -1
base$X_quint <- exp(base$X) -1

##### Aplicar leads e lags na var_X pbf_fam
#install.packages("DataCombine")
library(DataCombine)
base_ll <- base
base_ll <- slide(base_ll, Var = "X", GroupVar = "cod_mun", slideBy = -2)
base_ll$X_2 <- base_ll[,"X-2"] 
base_ll <- slide(base_ll, Var = "X", GroupVar = "cod_mun", slideBy = -1)
base_ll$X_1 <- base_ll[,"X-1"]
base_ll <- slide(base_ll, Var = "X", GroupVar = "cod_mun", slideBy = 1)
base_ll <- slide(base_ll, Var = "X", GroupVar = "cod_mun", slideBy = 2)
####Remember to order base by cod_mun and the time variable before running.
####Lagging X by 2 time units.

### Editores do STARGAZER
controls_tab <- "+ log(1 + pop)"
var.y_cap <- "Log(employ.)"
var.omit <- NULL
edit.rep <- c("vc*s") # report t stat instead of std error

#######
# TABELA 1: Estrutura Básica
#######

reg1 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID|0|CLUS")),                      base)
reg2 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.factor(ANO)|0|CLUS")),       base)
reg3 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.numeric(ANO):TEND|0|CLUS")), base)
reg4 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.factor(ANO):TEND|0|CLUS")),  base)

LREG <- lregs_1 <- list(reg1, reg2, reg3, reg4)
tit.name <- "Regressoes das Formas Funcionais"
lab <- "ff"
vars.x_tab1 <- c("Log(fam.)","Log(pop.)")
ord <- c(1,2)
out.path <- paste0(tables.dest,"tab1.tex")

stargazer(LREG,
          #notes = tit.name,  
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt),
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.caption = var.y_cap, 
          dep.var.labels.include = FALSE,
          covariate.labels = vars.x_tab1, order = ord,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = TRUE, single.row = FALSE, # compress table text
          ##### LABELS
          label = lab, out = out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",        "y","y","y","y"),
                           c("Dummy: Year",          "n","y","n","n"),
                           c("State Linear Trend",   "n","n","y","n"),
                           c("Dummy: Year x State",  "n","n","n","y")))

#######
# TABELA 1.1: Estrutura Básica com Leads & Lags
#######

reg1 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID|0|CLUS")),                      base_ll)
reg2 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.factor(ANO)|0|CLUS")),       base_ll)
reg3 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.numeric(ANO):TEND|0|CLUS")), base_ll)
reg4 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "|ID+as.factor(ANO):TEND|0|CLUS")),  base_ll)

reg5 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "+ X_1 + X_2 + X1 + X2   |ID|0|CLUS")),                     base_ll)
reg6 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "+ X_1 + X_2 + X1 + X2   |ID+as.factor(ANO)|0|CLUS")),      base_ll)
reg7 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "+ X_1 + X_2 + X1 + X2   |ID+as.numeric(ANO):TEND|0|CLUS")),base_ll)
reg8 <- felm(as.formula(paste0("Y ~ X",   controls_tab,   "+ X_1 + X_2 + X1 + X2   |ID+as.factor(ANO):TEND|0|CLUS")), base_ll)

LREG <- lregs_leadlag <- list(reg1, reg5, reg2, reg6, reg3, reg7, reg4, reg8)
tit.name <- "Regressoes das Formas Funcionais com Leads e Lags"
lab <- "ff:ll"
vars.x_tabll <- c("Log(fam.) on t","Log(fam.) on t-1","Log(fam.) on t-2",
                  "Log(fam.) on t+1","Log(fam.) on t+2","Log(pop.)")
ord <- c(1,3,4,5,6,2)
out.path <- paste0(tables.dest,"tab11.tex")

stargazer(LREG,
          #notes = tit.name,  
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt),
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.caption = var.y_cap,
          dep.var.labels.include = FALSE,
          covariate.labels = vars.x_tabll, order = ord,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = TRUE, single.row = FALSE, # compress table text
          ##### LABELS
          label = lab, out = out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",       "y","y","y","y","y","y","y","y"),
                           c("Dummy: Year",         "n","n","y","y","n","n","n","n"),
                           c("State Linear Trend",  "n","n","n","n","y","y","n","n"),
                           c("Dummy: Year x State", "n","n","n","n","n","n","y","y")))

#######
# TABELA 2: Quebras com dummies (Dummy Estado x Tempo)
#######

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$re==1)] <- 1
base$D2[which(base$re==2)] <- 1
base$D3[which(base$re==3)] <- 1
base$D4[which(base$re==4)] <- 1
base$D5[which(base$re==5)] <- 1

reg1 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg5 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

#######

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% summarise(X_med=mean(X_quint/pop),Y_med=mean(Y_quint/pop))
base <- merge(base, base00, by=c("cod_mun"))

####### Dummies para a quebra por var X

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
base$D2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
base$D3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
base$D4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
base$D5[which(base$X_med>quantile(base$X_med, .8))] <- 1

reg2 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg6 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

####### Dummies para a quebra por var Y

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
base$D2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
base$D3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
base$D4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
base$D5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1

reg3 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg7 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

####### Dummies para a quebra por pib per capita

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
base$D2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
base$D3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
base$D4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
base$D5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1

reg4 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg8 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

#######
# TABELA 2: Quebras com dummies (Tendência por Dummies)
#######

LREG <- lregs_2 <- list(reg1,reg2,reg3,reg4)
tit.name <- "Quebras com Dummies e Tendencia com Dummies"
col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.")
lab <- "dRXYP:dt"
vars.x_tab2 <- c("Log(fam.)*D1","Log(fam.)*D2","Log(fam.)*D3","Log(fam.)*D4","Log(fam.)*D5","Log(pop.)")
ord <- c(2,3,4,5,6,1)
out.path <- paste0(tables.dest,"tab21.tex")

stargazer(LREG,
          #notes= tit.name,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt),
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.caption = var.y_cap,
          dep.var.labels.include = FALSE,
          covariate.labels = vars.x_tab2, order = ord,
          column.labels = col.labels,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = FALSE, single.row = FALSE, # compress table text
          ##### LABELS
          label = lab, out=out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",       "y","y","y","y"),
                           c("Dummy: Year",         "n","n","n","n"),
                           c("State Linear Trend",  "n","n","n","n"),
                           c("Dummy: Year x State", "y","y","y","y")))

#######
# TABELA 3: Quebras com dummies (Tendência Linear)
#######

LREG <- lregs_3 <- list(reg5,reg6,reg7,reg8)

tit.name <- "Quebras com Dummies e Tendencia Linear"
col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.")
lab <- "dRXYP:lt"
vars.x_tab2 <- c("Log(fam.)*D1","Log(fam.)*D2","Log(fam.)*D3","Log(fam.)*D4","Log(fam.)*D5","Log(pop.)")
ord <- c(2,3,4,5,6,1)
out.path <- paste0(tables.dest,"tab22.tex")

stargazer(LREG, 
          #notes= tit.name,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',31),diag),sqrt),
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.caption = var.y_cap,
          dep.var.labels.include = FALSE,
          covariate.labels = vars.x_tab2, order = ord,
          column.labels = col.labels,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = FALSE, single.row = FALSE, # compress table text
          ##### LABELS
          label = lab, out=out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",       "y","y","y","y"),
                           c("Dummy: Year",         "n","n","n","n"),
                           c("State Linear Trend",  "n","n","n","n"),
                           c("Dummy: Year x State", "y","y","y","y")))