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

base_ll <- base_ll[base_ll$ano %in% 2006:2014,]
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
vars.x_tab1 <- c("Log(ben. fam.)","Log(pop.)")
ord <- c(1,2)
out.path <- paste0(tables.dest,"tab1.tex")

stargazer(LREG,
          #notes = tit.name,  
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',30),diag),sqrt),
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
          add.lines = list(c("Fixed effects",        "Y","Y","Y","Y"),
                           c("Dummy: Year",          "N","Y","N","N"),
                           c("State Linear Trend",   "N","N","Y","N"),
                           c("Dummy: Year x State",  "N","N","N","Y")))

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
          se = lapply(lapply(lapply(LREG,'[[',30),diag),sqrt),
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
          add.lines = list(c("Fixed effects",       "Y","Y","Y","Y","Y","Y","Y","Y"),
                           c("Dummy: Year",         "N","N","Y","Y","N","N","N","N"),
                           c("State Linear Trend",  "N","N","N","N","Y","Y","N","N"),
                           c("Dummy: Year x State", "N","N","N","N","N","N","Y","Y")))

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
reg6 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

#######

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% 
                    summarise(X_med = mean(X_quint / pop), Y_med = mean(Y_quint / pop), pop_med = mean(pop))
base <- merge(base, base00, by=c("cod_mun"))

####### Dummies para a quebra por var X

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
base$D2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
base$D3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
base$D4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
base$D5[which(base$X_med>quantile(base$X_med, .8))] <- 1

reg2 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg7 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

####### Dummies para a quebra por var Y

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
base$D2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
base$D3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
base$D4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
base$D5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1

reg3 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg8 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

####### Dummies para a quebra por pib per capita

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
base$D2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
base$D3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
base$D4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
base$D5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1

reg4 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg9 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

####### Dummies para a quebra por população

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pop_med<=quantile(base$pop_med, .2))] <- 1
base$D2[which(base$pop_med>quantile(base$pop_med, .2) & base$pop_med<=quantile(base$pop_med, .4))] <- 1
base$D3[which(base$pop_med>quantile(base$pop_med, .4) & base$pop_med<=quantile(base$pop_med, .6))] <- 1
base$D4[which(base$pop_med>quantile(base$pop_med, .6) & base$pop_med<=quantile(base$pop_med, .8))] <- 1
base$D5[which(base$pop_med>quantile(base$pop_med, .8))] <- 1

reg5 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.factor(ANO):TEND|0|CLUS")),   base)
reg10 <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab,  "|ID+as.numeric(ANO):TEND|0|CLUS")),   base)

#######
# TABELA 2: Quebras com dummies (Tendência por Dummies)
#######

LREG <- lregs_2 <- list(reg1,reg2,reg3,reg4,reg5)
tit.name <- "Quebras com Dummies e Tendencia com Dummies"
col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.", "Population")
lab <- "dRXYP:dt"
vars.x_tab2 <- c("Log(ben. fam.)*D1","Log(ben. fam.)*D2","Log(ben. fam.)*D3","Log(ben. fam.)*D4","Log(ben. fam.)*D5","Log(pop.)")
ord <- c(2,3,4,5,6,1)
out.path <- paste0(tables.dest,"tab21.tex")

stargazer(LREG,
          #notes= tit.name,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',30),diag),sqrt),
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
          add.lines = list(c("Fixed effects",       "Y","Y","Y","Y","Y"),
                           c("Dummy: Year",         "N","N","N","N","N"),
                           c("State Linear Trend",  "N","N","N","N","N"),
                           c("Dummy: Year x State", "Y","Y","Y","Y","Y")))

#######
# TABELA 3: Quebras com dummies (Tendência Linear)
#######

#LREG <- lregs_3 <- list(reg6,reg7,reg8,reg9,reg10)

#tit.name <- "Quebras com Dummies e Tendencia Linear"
#col.labels <- c("Region", "Qts. Benefic.", "Qts. Employ.", "Qts. Pers. Inc.", "Population")
#lab <- "dRXYP:lt"
#vars.x_tab2 <- c("Log(fam.)*D1","Log(fam.)*D2","Log(fam.)*D3","Log(fam.)*D4","Log(fam.)*D5","Log(pop.)")
#ord <- c(2,3,4,5,6,1)
#out.path <- paste0(tables.dest,"tab22.tex")

#stargazer(LREG, 
#          #notes= tit.name,
#          float = FALSE,  #float.env = "sidewaystable",
#          ##### CONTENT
#          report = edit.rep, # report t stat instead of std error
#          se = lapply(lapply(lapply(LREG,'[[',30,diag),sqrt)),
#          omit = var.omit, omit.stat = NULL,
#          ##### AESTHETICS
#          star.cutoffs = c(0.05, 0.01, 0.001),
#          style = "default",
#          dep.var.caption = var.y_cap,
#          dep.var.labels.include = FALSE,
#          covariate.labels = vars.x_tab2, order = ord,
#          column.labels = col.labels,
#          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
#          model.numbers = FALSE, single.row = FALSE, # compress table text
#          ##### LABELS
#          label = lab, out=out.path,
#          ##### EXTRA INFO
#          add.lines = list(c("Fixed effects",       "Y","Y","Y","Y","Y"),
#                           c("Dummy: Year",         "N","N","N","N","N"),
#                           c("State Linear Trend",  "N","N","N","N","N"),
#                           c("Dummy: Year x State", "Y","Y","Y","Y","Y")))


#input: lista de regressões
#output: um data.frame com todos os coeficientes por quebra e por v. dependente
coef_matrix <- function(regs.list, x.axis=c("1st","2nd","3rd","4th","5th"),
                        cols=c("Region","Beneficiaries","Formal Employment","Personal Income","Population")){
        
        nc <- length(cols); nx <- length(x.axis)
        coef <- unlist(lapply(regs.list,'[[',7))
        se <- unlist(lapply(lapply(lapply(regs.list,'[[',31),diag),sqrt))
        se <- se[!se==0]
        
        id_pop <- (1+nc)*(1:nx)-nc; coef <- coef[-id_pop]; se <- se[-id_pop]
        vars <- rep(x.axis, times=nc); cl <- rep(cols, each=nx)
        up = coef + 2 * se
        lo = coef - 2 * se
        
        data.frame(vars, cl, coef, se, up, lo)
}


#input: um data.frame com todos os coeficientes por quebra e por v. dependente
#output: um grafico de linhas com todos os coeficientes
graphs <- function(df){
        
        ggplot(df) + 
                geom_errorbar(aes(x = vars, ymax = up, ymin = lo, group=1, color=1)) +
                geom_point(aes(x = vars, y = coef, color=1), shape=3) +
                geom_hline(aes(yintercept=0), linetype="dashed") +
                facet_grid( ~ cl, scales="free") +
                #ylim(-0.1, 0.2) +
                labs(x = "Dep. Variable", y = "Coefficients") +
                theme(legend.position="none")
}

df <- coef_matrix(lregs_2)
df$type <- "Overall"

df$cl = factor(df$cl,levels(df$cl)[c(5,1:4)])
levels(df$vars) <- c(levels(df$vars), c("N","NE","S","SE","CW"))
df$vars[df$cl == "Region"] <- as.factor(c("N","NE","SE","S","CW"))
df$vars = factor(df$vars, levels(df$vars)[c(1:5,6:7,10,9,8)])

ggsave(file ="Tabelas de Resultados/temp/graph_overall.png", graphs(df), scale=1.4)
