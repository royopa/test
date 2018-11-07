#install.packages("dplyr")
#install.packages("ggplot2")
#install.packages("reshape2")
#install.packages("gtools")

library(dplyr)
library(ggplot2)
library(reshape2)
library(gtools)

setwd("E:/Dissertacao")
rm(list=ls())

###### EDIT

q <- 4
quebra_emp <- c("hor", "tam", "rem", "set")
qe <- quebra_emp[q]
levels <- c("1st Quint X","2nd Quint X","3rd Quint X","4th Quint X","5th Quint X")

###### END EDIT

base <- read.csv(file =paste0("Dados/base_emp_",qe,".csv"), header =TRUE, sep =",")
nvar <- dim(base)[2]
cont <- read.csv(file ="Dados/base_pbf.csv", header =TRUE, sep =",")
cont <- cont[,1:3]
base11 <- read.csv(file ="Dados/base_pop.csv", header =TRUE, sep =",")
base11 <- merge(base11, cont, by=c("cod_mun","ano"))
base00 <- base11 %>% group_by(cod_mun) %>% select(pbf_fam,pop) %>% summarise(fam_med=mean(pbf_fam/pop))
base <- merge(base, base00, by=c("cod_mun"))
base$fac_div <- quantcut(base$fam_med, q=5, na.rm=TRUE)

# Ativ1 - ext. mineral      Ativ2 - ind. transformaçao     Ativ3 - serv. industriais
# Ativ4 - const. civil      Ativ5 - comercio               Ativ6 - serviços
# Ativ7 - adm. publica      Ativ8 - agropecuaria
# Rem1 - ate ,5 r$ p/ hora        Rem2 - de ,51 a 1 r$ p/h     Rem3 - de 1,01 a 1,50 r$ p/h 
# Rem4 - de 1,51 a 2 r$ p/h       Rem5 - de 2,01 a 3 r$ p/h    Rem6 - de 3,01 a 4 r$ p/h 
# Rem7 - de 4,01 a 5 r$ p/h       Rem8 - de 5,01 a 7 r$ p/h    Rem9 - de 7,01 a 10 r$ p/h 
# Rem10 - de 10,01 a 15 r$ p/h    Rem11 - de 15,01 a 20 r$ p/h Rem12 - de 20,01 ou mais r$ p/h 
# Tam1 - 1 a 4 empregadoS   Tam2 - 5 a 9 emps        Tam3 - 10 a 19 emps
# Tam4 - 20 a 49 emps       Tam5 - 50 a 99 emps      Tam6 - 100 a 249 emps
# Tam7 - 250 a 499 emps     Tam8 - 500 a 999 emps    Tam9 - 1000 ou mais emps
# Hor1 - ate 12 hora     Hor2 - de 13 a 15 h     Hor3 - de 16 a 20 h 
# Hor4 - de 31 a 40 h    Hor5 - de 41 a 44 h     Hor6 - mais de 44 h
    
if (q==1) {base0 <- base %>% group_by(ano,fac_div) %>% select(names(base[,3:nvar])) %>%
                    summarise(Hor1=sum(emp_hor1),Hor2=sum(emp_hor2),Hor3=sum(emp_hor3),
                              Hor4=sum(emp_hor4),Hor5=sum(emp_hor5),Hor6=sum(emp_hor6))
}else{if(q==2) {base0 <- base %>% group_by(ano,fac_div) %>% select(names(base[,3:nvar])) %>%
                    summarise(Tam1=sum(emp_tam1),Tam2=sum(emp_tam2),Tam3=sum(emp_tam3),
                              Tam4=sum(emp_tam4),Tam5=sum(emp_tam5),Tam6=sum(emp_tam6),
                              Tam7=sum(emp_tam7),Tam8=sum(emp_tam8),Tam9=sum(emp_tam9))
}else{if(q==3) {base0 <- base %>% group_by(ano,fac_div) %>% select(names(base[,3:nvar])) %>%
                    summarise(Rem1=sum(emp_rem1),Rem2=sum(emp_rem2),Rem3=sum(emp_rem3),
                              Rem4=sum(emp_rem4),Rem5=sum(emp_rem5),Rem6=sum(emp_rem6),
                              Rem7=sum(emp_rem7),Rem8=sum(emp_rem8),Rem9=sum(emp_rem9),
                              Rem10=sum(emp_rem10),Rem11=sum(emp_rem11),Rem12=sum(emp_rem12))
}else{if(q==4) {base0 <- base %>% group_by(ano,fac_div) %>% select(names(base[,3:nvar])) %>%
                    summarise(Ext.Min=sum(emp_set1),Ind.Trans=sum(emp_set2),
                              Serv.Ind=sum(emp_set3),Cons.Civ=sum(emp_set4),
                              Com=sum(emp_set5),Serv=sum(emp_set6),Adm.Pub=sum(emp_set7),
                              Agro=sum(emp_set8))
}else{print("VOCÊ NÃO SELECIONOU UMA QUEBRA DE EMPREGO VALIDA!!!!!")}}}}

base0 <- as.data.frame(base0)
base2 <- base0
levels(base0$fac_div) <- levels 
base0[,3:nvar] <- lapply(base0[,3:nvar], function(x){x/rowSums(base0[,3:nvar])})
base0 <- melt(base0, id=c("fac_div","ano"))

# Evoluçao do emprego em diferentes setores para cada região 
reg <- ggplot(base0, aes(x = ano, y = value, color = variable)) +
    geom_line() +
    facet_grid(fac_div~variable) +
    ylab("Emprego") +
    xlab("Anos")
ggsave(paste0("FigGrafs/Quebra nas Colunas/Grafs_varX/varX_",qe,".png"), scale=2)

#base1 <- base %>% group_by(ano) %>% select(names(base[,3:nvar])) %>% 
#   summarise(Rem1=sum(emp_rem1),Rem2=sum(emp_rem2),Rem3=sum(emp_rem3),Rem4=sum(emp_rem4),
#             Rem5=sum(emp_rem5),Rem6=sum(emp_rem6),Rem7=sum(emp_rem7),Rem8=sum(emp_rem8),
#             Rem9=sum(emp_rem9),Rem10=sum(emp_rem10),Rem11=sum(emp_rem11),Rem12=sum(emp_rem12))
#    summarise(Ext.Min=sum(emp_set1),Ind.Trans=sum(emp_set2),Serv.Ind=sum(emp_set3),Cons.Civ=sum(emp_set4),
#              Com=sum(emp_set5),Serv=sum(emp_set6),Adm.Pub=sum(emp_set7),Agro=sum(emp_set8))
#base1 <- as.data.frame(base1)
#base1 <- base1[rep(seq_len(nrow(base1)), each=5),]
#base2[,3:nvar] <- base2[,3:nvar] / base1[,2:(nvar-1)]
#base2$re <- as.factor(base2$re)
#levels(base2$re) <- c("N","NE","SE","S","CO")
#base2 <- melt(base2, id=c("re","ano"))


# Evoluçao do emprego em diferentes regiões para cada setor 
#set <- ggplot(base2, aes(x = ano, y = value, color = re, group = re)) +
#    geom_line() +
#    facet_grid(~variable) +
#    ylab("Emprego") +
#    xlab("Anos")
#ggsave("FigGrafs/set.png", scale=2)  
