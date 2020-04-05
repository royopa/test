library(readxl)
library(dplyr)
library(lubridate)
library(forecast)

IPCA_15 <- TRUE

path <- "F:/DADOS/ASSET/MACROECONOMIA/DADOS/Inflação/1.IPCA/"
source(paste0(path,"R/AUX_ajuste_sazonal.R"), echo=TRUE)
initial_date <- c(2001,1)

if (IPCA_15 == TRUE){
  end_date0 <- c(year(today()), 2*month(today())-1)
  end_date1 <- c(year(today()), month(today()))
  end_date2 <- c(year(today()), month(today())-1)
} else {   
  end_date0 <- c(year(today()), 2*(month(today())-1))
  end_date1 <- end_date2 <- c(year(today()), month(today())-1)}


nucleos <- read_excel(paste0(path,"IPCA.xlsx"), sheet="Nuc_ResMensal", 
                      skip=5, col_names=TRUE) %>% as.data.frame

datas <- lapply(names(nucleos)[-c(1,2,3)], 
                function(x){as.Date(as.numeric(x), origin = "1899-12-30")})

for (i in 4:ncol(nucleos)){df[,i] <- as.numeric(df[,i])} 

start_date <- c(year(as.Date(head(unlist(datas),1),  origin="1970-1-1")),
                month(as.Date(head(unlist(datas),1), origin="1970-1-1")))
year_end  <- year(as.Date(tail(unlist(datas),1),     origin="1970-1-1"))
month_end <- month(as.Date(tail(unlist(datas),1),    origin="1970-1-1"))

names(nucleos) <- c("cod", "desc", "peso")

dsz_ipca <- function(x){
  core <- nucleos[nucleos$cod == x,][3,-c(1:3)] %>% t() %>% as.numeric() %>%
                    ts(start=start_date, frequency = 24) %>% window(start=c(2001,1), end=end_date0)
  dsz_15 <- core[seq(from=1, to=length(core), by=2)] %>% ts(start=initial_date, 
                      end=end_date1, frequency=12) %>% ajuste_sazonal
  dsz_30 <- core[seq(from=2, to=length(core), by=2)] %>% ts(start=initial_date, 
                      end=end_date2, frequency=12) %>% ajuste_sazonal
  dsz <- core
  for (i in 1:(length(core)/2)){
    dsz[c(2*i-1, 2*i)] <- c(round(dsz_15[i],3), round(dsz_30[i],3))}
  
  return(dsz)}

dsz_serv <- dsz_ipca("10000"); dsz_ind <- dsz_ipca("20000"); dsz_alim <- dsz_ipca("30000")

df <- data.frame(dsz_serv, dsz_ind, dsz_alim)
names(df) <- c("Serviços", "Industriais", "Alimentos")
#df <- sapply(df, function(x){gsub("\\.",",",x)})

write.table(t(df), dec= ",", paste0(path,"bases/outputR_inf_dessaz.csv"), row.names = FALSE, sep=";")
