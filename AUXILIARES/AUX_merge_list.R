merge_list <- function(x, all=TRUE){
  df <- x[[1]]
  for (i in 2:length(x)){df <- merge(df, x[[i]], by=c("datas"), all=all)}
  return(df)}