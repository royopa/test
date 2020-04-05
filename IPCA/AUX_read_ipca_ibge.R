read.ipca.ibge <- function(x, dia){
  meses <- c("01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12")
  df <- read.table(paste0(path, "historico/", x), fill=TRUE, header=TRUE, 
                   sep=";", skip=3)
  df[,3:ncol(df)] <- sapply(df[,3:ncol(df)], function(x){x <- as.numeric(gsub(",", "\\.", as.character(x)))})
  
  if (dia != 15){
    df <- df[1:(which(df$X == "Fonte: IBGE - Ã\u008dndice Nacional de PreÃ§os ao Consumidor Amplo")-1),]
  } else {df <- df[1:(which(df$X == "Fonte: IBGE - Ã\u008dndice Nacional de PreÃ§os ao Consumidor Amplo 15")-1),]} 
  
  cods <- lapply(strsplit(as.character(df[,2]), "\\."), '[', 1) %>% unlist
  prod <- lapply(strsplit(as.character(df[,2]), "\\."), '[', 2) %>% unlist
  cods[1] <- 0; df[,1] <- cods; df[,2] <- prod
  
  nms <- strsplit(names(df), "\\.")
  locs <- lapply(nms, length) %>% unlist
  names <- c(); for (i in 3:length(nms)){names[i-2] <- nms[[i]][locs[i]]}
  q <- length(which(names == unique(names)[1]))
  m <- c(tail(meses, q), rep(meses, 12))[1:length(names)]
  names <- c("cods", "prods",paste0(dia, "/", m, "/", names))
  
  names(df) <- names
  df$prods <- iconv(df$prod, from="UTF-8", to="LATIN1")
  df$prods[1] <- "IPCA"
  return(df)}