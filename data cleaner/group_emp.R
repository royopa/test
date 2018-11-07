rm(list=ls())
setwd("E:/Dissertacao")

### Loding outcome variables
####################### POR SETOR #####

set_sex <- read.csv(file ="DADOS/base_emp_setsex.csv", header=TRUE, sep=",")
nc <- ncol(set_sex)+1
### Originalmente temos empregos formais discriminados por 8 setores e 3 gêneros (masc, fem e tot), ou seja 24 categorias
### Queremos agrupar os 8 setores em 5, mantendo a separação por gênero, ou seja, 15 categorias
### Os 5 setores agrupados serão: 
set_sex$emp_masc <- rowSums(set_sex[,grep("masc",names(set_sex))])
set_sex$emp_fem <- rowSums(set_sex[,grep("fem",names(set_sex))])
set_sex$emp_tot <- set_sex$emp_masc + set_sex$emp_fem

set_sex$emp_1set_masc <- set_sex$emp_set1_masc + set_sex$emp_set4_masc + set_sex$emp_set8_masc
set_sex$emp_1set_fem <- set_sex$emp_set1_fem + set_sex$emp_set4_fem + set_sex$emp_set8_fem
set_sex$emp_1set_tot <- set_sex$emp_1set_masc + set_sex$emp_1set_fem

set_sex$emp_2set_masc <- set_sex$emp_set2_masc + set_sex$emp_set3_masc
set_sex$emp_2set_fem <- set_sex$emp_set2_fem + set_sex$emp_set3_fem
set_sex$emp_2set_tot <- set_sex$emp_2set_masc + set_sex$emp_2set_fem

set_sex$emp_3set_masc <- set_sex$emp_set5_masc + set_sex$emp_set6_masc
set_sex$emp_3set_fem <- set_sex$emp_set5_fem + set_sex$emp_set6_fem
set_sex$emp_3set_tot <- set_sex$emp_3set_masc + set_sex$emp_3set_fem

set_sex$emp_apset_masc <- set_sex$emp_set7_masc
set_sex$emp_apset_fem <- set_sex$emp_set7_fem
set_sex$emp_apset_tot <- set_sex$emp_apset_masc + set_sex$emp_apset_fem

set <- set_sex[,c(1,2,nc:ncol(set_sex))]

####################### POR TAMANHO #####

tam_sex <- read.csv(file ="DADOS/base_emp_tamsex.csv", header=TRUE, sep=",")
nc <- ncol(tam_sex)+1
### Originalmente temos empregos formais discriminados por 9 tamanhos e 3 gêneros (masc, fem e tot), ou seja 27 categorias
### Queremos agrupar os 9 tamanhos em 3, mantendo a separação por gênero, ou seja, 9 categorias
### Os 4 tamanhos agrupados serão: 

tam_sex$emp_1tam_masc <- tam_sex$emp_tam1_masc + tam_sex$emp_tam2_masc
tam_sex$emp_1tam_fem <- tam_sex$emp_tam1_fem + tam_sex$emp_tam2_fem
tam_sex$emp_1tam_tot <- tam_sex$emp_1tam_masc + tam_sex$emp_1tam_fem

tam_sex$emp_2tam_masc <- tam_sex$emp_tam3_masc + tam_sex$emp_tam4_masc
tam_sex$emp_2tam_fem <- tam_sex$emp_tam3_fem + tam_sex$emp_tam4_fem
tam_sex$emp_2tam_tot <- tam_sex$emp_2tam_masc + tam_sex$emp_2tam_fem

tam_sex$emp_3tam_masc <- tam_sex$emp_tam5_masc + tam_sex$emp_tam6_masc
tam_sex$emp_3tam_fem <- tam_sex$emp_tam5_fem + tam_sex$emp_tam6_fem
tam_sex$emp_3tam_tot <- tam_sex$emp_3tam_masc + tam_sex$emp_3tam_fem

tam_sex$emp_4tam_masc <- tam_sex$emp_tam7_masc + tam_sex$emp_tam8_masc + tam_sex$emp_tam9_masc
tam_sex$emp_4tam_fem <- tam_sex$emp_tam7_fem + tam_sex$emp_tam8_fem + tam_sex$emp_tam9_fem
tam_sex$emp_4tam_tot <- tam_sex$emp_4tam_masc + tam_sex$emp_4tam_fem

tam <- tam_sex[,c(1,2,nc:ncol(tam_sex))]

####################### POR REMUNERAÇÃO #####

rem_sex <- read.csv(file ="DADOS/base_emp_remsex.csv", header=TRUE, sep=",")
nc <- ncol(rem_sex)+1
### Originalmente temos empregos formais discriminados por 12 remunerações e 3 gêneros (masc, fem e tot), ou seja 36 categorias
### Queremos agrupar os 12 remunerações em 3, mantendo a separação por gênero, ou seja, 15 categorias
### As 3 remunerações agrupados serão: 

rem_sex$emp_1rem_masc <- rem_sex$emp_rem1_masc + rem_sex$emp_rem2_masc + rem_sex$emp_rem3_masc
rem_sex$emp_1rem_fem <- rem_sex$emp_rem1_fem + rem_sex$emp_rem2_fem + rem_sex$emp_rem3_fem
rem_sex$emp_1rem_tot <- rem_sex$emp_1rem_masc + rem_sex$emp_1rem_fem

rem_sex$emp_2rem_masc <- rem_sex$emp_rem4_masc + rem_sex$emp_rem5_masc + rem_sex$emp_rem6_masc
rem_sex$emp_2rem_fem <- rem_sex$emp_rem4_fem + rem_sex$emp_rem5_fem + rem_sex$emp_rem6_fem
rem_sex$emp_2rem_tot <- rem_sex$emp_2rem_masc + rem_sex$emp_2rem_fem

rem_sex$emp_3rem_masc <- rem_sex$emp_rem7_masc + rem_sex$emp_rem8_masc + rem_sex$emp_rem9_masc
rem_sex$emp_3rem_fem <- rem_sex$emp_rem7_fem + rem_sex$emp_rem8_fem + rem_sex$emp_rem9_fem
rem_sex$emp_3rem_tot <- rem_sex$emp_3rem_masc + rem_sex$emp_3rem_fem

rem_sex$emp_4rem_masc <- rem_sex$emp_rem10_masc + rem_sex$emp_rem11_masc + rem_sex$emp_rem12_masc
rem_sex$emp_4rem_fem <- rem_sex$emp_rem10_fem + rem_sex$emp_rem11_fem + rem_sex$emp_rem12_fem
rem_sex$emp_4rem_tot <- rem_sex$emp_4rem_masc + rem_sex$emp_4rem_fem

rem <- rem_sex[,c(1,2,nc:ncol(rem_sex))]

####################### POR ESCOLARIDADE #####

esc_sex <- read.csv(file ="DADOS/base_emp_escsex.csv", header=TRUE, sep=",")
nc <- ncol(esc_sex)+1
### Originalmente temos empregos formais discriminados por 9 escolaridades e 3 gêneros (masc, fem e tot), ou seja 24 categorias
### Queremos agrupar as 9 escolaridades em 3, mantendo a separação por gênero, ou seja, 15 categorias
### As 3 escolaridades agrupados serão: 

esc_sex$emp_1esc_masc <- esc_sex$emp_esc1_masc + esc_sex$emp_esc2_masc
esc_sex$emp_1esc_fem <- esc_sex$emp_esc1_fem + esc_sex$emp_esc2_fem
esc_sex$emp_1esc_tot <- esc_sex$emp_1esc_masc + esc_sex$emp_1esc_fem

esc_sex$emp_2esc_masc <- esc_sex$emp_esc3_masc + esc_sex$emp_esc4_masc
esc_sex$emp_2esc_fem <- esc_sex$emp_esc3_fem + esc_sex$emp_esc4_fem
esc_sex$emp_2esc_tot <- esc_sex$emp_2esc_masc + esc_sex$emp_2esc_fem

esc_sex$emp_3esc_masc <- esc_sex$emp_esc5_masc + esc_sex$emp_esc6_masc
esc_sex$emp_3esc_fem <- esc_sex$emp_esc5_fem + esc_sex$emp_esc6_fem
esc_sex$emp_3esc_tot <- esc_sex$emp_3esc_masc + esc_sex$emp_3esc_fem

esc_sex$emp_4esc_masc <- esc_sex$emp_esc7_masc + esc_sex$emp_esc8_masc + esc_sex$emp_esc9_masc
esc_sex$emp_4esc_fem <- esc_sex$emp_esc7_fem + esc_sex$emp_esc8_fem + esc_sex$emp_esc9_fem
esc_sex$emp_4esc_tot <- esc_sex$emp_4esc_masc + esc_sex$emp_4esc_fem

esc <- esc_sex[,c(1,2,nc:ncol(esc_sex))]

###########################################################################################################

base <- merge(set, tam, by=c("cod_mun","ano"))
base <- merge(base, rem, by=c("cod_mun","ano"))
base <- merge(base, esc, by=c("cod_mun","ano"))

write.csv(base, "DADOS/base_RAIS.csv", row.names=FALSE)

