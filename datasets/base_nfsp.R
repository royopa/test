setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("2003/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Necessidade de Financiamento do Setor Público
nfsp <- as.data.frame(read_excel("FINNFSP0.xls", sheet="NFSP sem Câmbio Ac. 12 M  % PIB", skip=3))
names(nfsp) <- c("date", "def_prim_tot", "def_prim_gov_central_tot", "def_prim_gov_cent_fed", 
                 "def_prim_gov_cent_bacen", "def_prim_gov_cent_inss", "def_prim_gov_reg_tot",
                 "def_prim_gov_reg_est", "def_prim_gov_reg_mun", "def_prim_estatais_tot",
                 "def_prim_estatais_fed", "def_prim_estatais_est", "def_prim_estatais_mun",
                 "jur_nom_tot", "jur_nom_gov_central_tot", "jur_nom_gov_cent_fed", 
                 "jur_nom_gov_cent_bacen", "jur_nom_gov_reg_tot",
                 "jur_nom_gov_reg_est", "jur_nom_gov_reg_mun", "jur_nom_estatais_tot",
                 "jur_nom_estatais_fed", "jur_nom_estatais_est", "jur_nom_estatais_mun",
                 "def_nom_tot", "def_nom_gov_central_tot", "def_nom_gov_cent_fed",
                 "def_nom_gov_cent_bacen", "def_nom_gov_reg_tot",
                 "def_nom_gov_reg_est", "def_nom_gov_reg_mun", "def_nom_estatais_tot",
                 "def_nom_estatais_fed", "def_nom_estatais_est", "def_nom_estatais_mun",
                 "pib_nom")
nfsp <- nfsp[1:(which(nfsp[,1] == "TOTAIS ANUAIS")-1),]
nfsp$date <- seq(as.Date("2002/12/1"), as.Date("2018/9/1"), by = "quarter")
nfsp <- nfsp[which(nfsp$date %in% t), ]
