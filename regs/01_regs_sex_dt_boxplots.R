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
library(ggplot2)
rm(list=ls())
setwd("E:/Dissertacao")
tables.dest <- "Tabelas de Resultados/temp/" 

base <- read.csv(file ="BASES/00_base.csv", header=TRUE, sep=",")
#base <- base[base$ano > 2005 & base$ano < 2015,]
facs <- c("cod_mun","ano","re","uf","meso","micro","cod_ibge")
base[,facs] <- lapply(base[,facs],as.factor)

### Seleciona as variáveis a serem Utilizadas nas regressões
base$ID                   <- base$cod_mun
base$TEND <- base$CLUS    <- base$micro
base$ANO                  <- as.factor(base$ano)

base$Y <- log(1 + base$emp_tot)
base$YM <- log(1 + base$emp_masc)
base$YF <- log(1 + base$emp_fem)
base$X <- log(1 + base$pbf_fam)
base$Y_quint <- exp(base$Y) -1
base$X_quint <- exp(base$X) -1

controls_tab1 <- controls_tab2 <- "+ log(1 + pop)"
var.y_cap <- "Log(employ.)"

### Editores do STARGAZER
var.omit <- NULL
edit.rep <- c("vc*s") # report t stat instead of std error

#######
# TABELA 2: Quebras com dummies (Dummy Estado x Tempo)
#######

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$re==1)] <- 1
base$D2[which(base$re==2)] <- 1
base$D3[which(base$re==3)] <- 1
base$D4[which(base$re==4)] <- 1
base$D5[which(base$re==5)] <- 1

reg1  <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",    controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg1m <- felm(as.formula(paste0("YM ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg1f <- felm(as.formula(paste0("YF ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)

#######

base00 <- base %>% group_by(cod_mun) %>% select(X_quint,Y_quint,pop) %>% 
  summarise(X_med = mean(X_quint / pop), Y_med = mean(Y_quint / pop), pop_med = mean(pop))
#### Adding missing grouping variables: `cod_mun`
base <- merge(base, base00, by=c("cod_mun"))

####### Dummies para a quebra por var X

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$X_med<=quantile(base$X_med, .2))] <- 1
base$D2[which(base$X_med>quantile(base$X_med, .2) & base$X_med<=quantile(base$X_med, .4))] <- 1
base$D3[which(base$X_med>quantile(base$X_med, .4) & base$X_med<=quantile(base$X_med, .6))] <- 1
base$D4[which(base$X_med>quantile(base$X_med, .6) & base$X_med<=quantile(base$X_med, .8))] <- 1
base$D5[which(base$X_med>quantile(base$X_med, .8))] <- 1

reg2  <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",    controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg2m <- felm(as.formula(paste0("YM ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg2f <- felm(as.formula(paste0("YF ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por var Y

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$Y_med<=quantile(base$Y_med, .2))] <- 1
base$D2[which(base$Y_med>quantile(base$Y_med, .2) & base$Y_med<=quantile(base$Y_med, .4))] <- 1
base$D3[which(base$Y_med>quantile(base$Y_med, .4) & base$Y_med<=quantile(base$Y_med, .6))] <- 1
base$D4[which(base$Y_med>quantile(base$Y_med, .6) & base$Y_med<=quantile(base$Y_med, .8))] <- 1
base$D5[which(base$Y_med>quantile(base$Y_med, .8))] <- 1

reg3  <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",    controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg3m <- felm(as.formula(paste0("YM ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg3f <- felm(as.formula(paste0("YF ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por pib per capita

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pibpc2010<=quantile(base$pibpc2010, .2))] <- 1
base$D2[which(base$pibpc2010>quantile(base$pibpc2010, .2) & base$pibpc2010<=quantile(base$pibpc2010, .4))] <- 1
base$D3[which(base$pibpc2010>quantile(base$pibpc2010, .4) & base$pibpc2010<=quantile(base$pibpc2010, .6))] <- 1
base$D4[which(base$pibpc2010>quantile(base$pibpc2010, .6) & base$pibpc2010<=quantile(base$pibpc2010, .8))] <- 1
base$D5[which(base$pibpc2010>quantile(base$pibpc2010, .8))] <- 1

reg4  <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",    controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg4m <- felm(as.formula(paste0("YM ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg4f <- felm(as.formula(paste0("YF ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)

####### Dummies para a quebra por população

base$D1 <- base$D2 <- base$D3 <- base$D4 <- base$D5 <- 0
base$D1[which(base$pop_med<=quantile(base$pop_med, .2))] <- 1
base$D2[which(base$pop_med>quantile(base$pop_med, .2) & base$pop_med<=quantile(base$pop_med, .4))] <- 1
base$D3[which(base$pop_med>quantile(base$pop_med, .4) & base$pop_med<=quantile(base$pop_med, .6))] <- 1
base$D4[which(base$pop_med>quantile(base$pop_med, .6) & base$pop_med<=quantile(base$pop_med, .8))] <- 1
base$D5[which(base$pop_med>quantile(base$pop_med, .8))] <- 1

reg5  <- felm(as.formula(paste0("Y ~ D1:X + D2:X + D3:X + D4:X + D5:X",    controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg5m <- felm(as.formula(paste0("YM ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)
reg5f <- felm(as.formula(paste0("YF ~ D1:X + D2:X + D3:X + D4:X + D5:X",   controls_tab2,  "|ID+ANO:TEND|0|CLUS")),   base)

#######
# TABELA 3.1: Quebra por Região (Total - Homens - Mulheres)
#######

table_out <- function(LREG, vars.x_tab = c("Log(ben. fam.)*D1(1= 1st fifth)","Log(ben. fam.)*D2(1= 2nd fifth)","Log(ben. fam.)*D3(1= 3rd fifth)",
                            "Log(ben. fam.)*D4(1= 4th fifth)","Log(ben. fam.)*D5(1= 5th fifth)","Log(pop.)"),
                            tab.name){

col.labels <- c("Overall", "Men", "Women")
ord <- c(2,3,4,5,6,1)
out.path <- paste0(tables.dest, tab.name)

stargazer(LREG,
          #notes = tit.name,
          #no.space = TRUE,
          float = FALSE,  #float.env = "sidewaystable",
          ##### CONTENT
          report = edit.rep, # report t stat instead of std error
          se = lapply(lapply(lapply(LREG,'[[',30),diag),sqrt),
          omit = var.omit, omit.stat = NULL,
          ##### AESTHETICS
          star.cutoffs = c(0.05, 0.01, 0.001),
          style = "default",
          dep.var.labels.include = FALSE,
          dep.var.caption = var.y_cap, 
          covariate.labels = vars.x_tab, order = ord,
          column.labels = col.labels,
          digits = 3, digits.extra = 2, initial.zero = FALSE, df = FALSE,
          model.numbers = FALSE, single.row = FALSE, # compress table text
          ##### LABELS
          out=out.path,
          ##### EXTRA INFO
          add.lines = list(c("Fixed effects",       "Y","Y","Y"),
                           c("Dummy: Year",         "N","N","N"),
                           c("State Linear Trend",  "N","N","N"),
                           c("Dummy: Year x State", "Y","Y","Y")))
}

lregs_31 <- list(reg1, reg1m, reg1f)
lregs_32 <- list(reg2, reg2m, reg2f)
lregs_33 <- list(reg3, reg3m, reg3f)
lregs_34 <- list(reg4, reg4m, reg4f)
lregs_35 <- list(reg5, reg5m, reg5f)

table_out(lregs_31, tab.name = "tab31dt.tex",
          vars.x_tab = c("Log(ben. fam.)*D1(1= North)","Log(ben. fam.)*D2(1= Northeast)","Log(ben. fam.)*D3(1= Southeast)",
                "Log(ben. fam.)*D4(1= South)","Log(ben. fam.)*D5(1= Middle-West)","Log(pop.)"))
table_out(lregs_32, tab.name = "tab32dt.tex")
table_out(lregs_33, tab.name = "tab33dt.tex")
table_out(lregs_34, tab.name = "tab34dt.tex")
table_out(lregs_35, tab.name = "tab35dt.tex")

#######
# Grafico Coeficientes 4
#######

LREGO <- list(reg1, reg2, reg3, reg4, reg5)
LREGM <- list(reg1m, reg2m, reg3m, reg4m, reg5m)
LREGF <- list(reg1f, reg2f, reg3f, reg4f, reg5f)

#input: lista de regressões
#output: um data.frame com todos os coeficientes por quebra e por v. dependente
coef_matrix <- function(regs.list, 
                        x.axis=c("1st","2nd","3rd","4th","5th"),
                        cols=c("Region","Beneficiaries","Formal Employment","Personal Income","Population")){
        
        nc <- length(cols); nx <- length(x.axis); nd <- nx - nc
        coef <- unlist(lapply(regs.list,'[[',7))
        se <- unlist(lapply(lapply(lapply(regs.list,'[[',30),diag),sqrt))
        se <- se[!se==0]
                
        id_pop <- (1+nx)*(1:nc)-nx; coef <- coef[-id_pop]; se <- se[-id_pop]
        vars <- rep(x.axis, times=nc)#; vars[nd:(nd+nc)] <- c("N","NE","SE","S","CW")
        cl <- rep(cols, each=nx)
        up = coef + 2 * se
        lo = coef - 2 * se
        
        data.frame(vars, cl, coef, se, up, lo)
}

#input: um data.frame com todos os coeficientes por quebra e por v. dependente
#output: um grafico de linhas com todos os coeficientes
graphs <- function(df){
       
        ggplot(df) + 
                geom_errorbar(aes(x = vars, ymax = up, ymin = lo, color=type), position = position_dodge(0.55)) +
                geom_point(aes(x = vars, y = coef, color=type), position = position_dodge(0.55), shape=3) +
                geom_point(aes(x = vars, y = coef.overall), shape=18) +
                geom_hline(aes(yintercept=0), linetype="dashed") +
                facet_grid( ~ cl, scales="free") + 
                #ylim(-0.1, 0.2) +
                labs(x = "Dep. Variable", y = "Coefficients", color = "Employment") + 
                theme(legend.position = "bottom")
        
}

df_base <- coef_matrix(LREGO); df_man <- coef_matrix(LREGM); df_fem <- coef_matrix(LREGF)

#df_base <- df_base[,c("vars","cl","coef")]
df_man$type <- "Male"; df_fem$type <- "Female"

df1 <- rbind(df_man, df_fem)
df1 <- merge(df1, df_base[,c("vars","cl","coef")], by=c("cl","vars"), suffixes=c("",".overall"))

#df <- merge(df_base, df_man, by=c("vars","cl"), suffixes=c("",".man"))
#df <- merge(df, df_fem, by=c("vars","cl"), suffixes=c("",".fem"))

df1$cl = factor(df1$cl,levels(df1$cl)[c(5,1:4)])
levels(df1$vars) <- c(levels(df1$vars), c("N","NE","S","SE","CW"))
df1$vars[df1$cl == "Region"] <- as.factor(rep(c("N","NE","SE","S","CW"), each=2))
df1$vars = factor(df1$vars, levels(df1$vars)[c(1:5,6:7,10,9,8)])

ggsave(file ="Tabelas de Resultados/temp/graph_sex.png", graphs(df1), scale=1.3)
