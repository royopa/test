path <- "F:/DADOS/ASSET/MACROECONOMIA/1PIETRO/codes/Hiato_prod/"

source(paste0(path,"data/PIBTRIM1_contas_nacionais.R"), local = TRUE)
pib_tri <- pib_tri[,c("datas", "pib_merc")]
names(pib_tri) <- c("datas", "val_add")


source(paste0(path,"data/ATVMCM4_pnad.R"), local = TRUE)
pnad <- pnad[,c("datas", "tx_desemp")]
### coletando meses de final de trimestre
id_pnad <- which(as.numeric(unlist(lapply(strsplit(as.character(pnad$datas), "-"),"[[",2))) %in% c(3,6,9,12))
pnad <- pnad[id_pnad,]


source(paste0(path,"data/ATVFGV13_fgv.R"), local = TRUE)
conf <- conf[,c("datas", "nuci_dsz")]
### coletando meses de final de trimestre
id_conf <- which(as.numeric(unlist(lapply(strsplit(as.character(conf$datas), "-"),"[[",2))) %in% c(3,6,9,12))
conf <- conf[id_conf,]


source(paste0(path,"Data/PRCIPCA0_ipca_grupos.R"))
ipca <- ipca_mes <- ipca_mes[,c("datas", "ipca_geral")]
ipca$ipca_geral <- NA
### acumulando o IPCA
for (i in 13:nrow(ipca)){ipca$ipca_geral[i] <- 100*(ipca_mes$ipca_geral[i] / ipca_mes$ipca_geral[i-12] -1)}
### coletando os dados de fim de periodo
id_ipca <- which(as.numeric(unlist(lapply(strsplit(as.character(ipca$datas), "-"),"[[",2))) %in% c(3,6,9,12))
ipca <- ipca[id_ipca, ]


source(paste0(path,"Data/PRCCORE2_nuc_ipca.R"))
nuc_ipca <- nuc_ipca[,c("datas", "ipca_nuc_ex2")]
names(nuc_ipca) <- c("datas", "ipca")
nuc <- nuc_ipca
nuc$ipca <- NA
### acumulando o nucleo do IPCA
for (i in 13:nrow(nuc)){nuc$ipca[i] <- 100*(prod(nuc_ipca$ipca[i:(i-12)]/100 +1)-1)}
### coletando os dados de fim de periodo
id_nuc <- which(as.numeric(unlist(lapply(strsplit(as.character(nuc$datas), "-"),"[[",2))) %in% c(3,6,9,12))
nuc <- nuc[id_nuc, ]

initial_date <- 2001; end_date <- 2019
t <- seq(as.Date("2001-03-01"), as.Date("2019-05-01"), by = "quarter")

Y  <- ts(pib_tri$val_add, freq=4, start=c(2000, 1));        Y <- window(Y, start=2001, end=2019)
C  <- ts(conf$nuci_dsz, freq=4, start=c(2001,1));           C <- window(C, start=initial_date, end=end_date)
E  <- 100*(1- ts(pnad$tx_desemp, freq=4, start=c(1998,1))); E <- window(E, start=initial_date, end=end_date)

data = na.omit(cbind(E,C,Y))

Pi <- ts(ipca$ipca_geral, freq=4, start=c(1979,4));         Pi <- window(Pi, start=(initial_date-.25), end=end_date)
nuc_Pi <- ts(nuc$ipca,    freq=4, start=c(1996,1));         nuc_Pi <- window(Pi, start=(initial_date-.25), end=end_date)
