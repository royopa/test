setwd("C:/Users/PIETCON/Documents/Data")
t <- seq(as.Date("1995/1/1"), as.Date("2018/9/1"), by = "quarter")
#### Swap Pre Di
swap <- as.data.frame(read_excel("MFISWAP0.xls", sheet = "Swap Pré-DI", skip = 2))
names(swap) <- c("date", "swap30_med", "swap30_end", "swap60_med", "swap60_end", 
               "swap90_med", "swap90_end", "swap180_med", "swap180_end", 
               "swap360_med", "swap360_end")
swap <- swap[2:(which(swap[,1] == "ANO")-1),]
swap <- as.data.frame(lapply(swap, as.numeric))
swap$date <- seq(as.Date("1995/1/1"), as.Date("2018/9/1"), by = "month")
swap <- swap[which(swap$date %in% t), ]
