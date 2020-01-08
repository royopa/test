df_filler = function(x){
  #id <- rep(0, (length(names(x))-1))
  
  for (i in 2:ncol(x)){
    nNAs <- which(!is.na(x[,i])); first <- nNAs[1]
    NAs  <- which(is.na(x[first:length(x[,i]),i])); last  <- first + tail(NAs,1) -1
    
    if (length(NAs) != 0){
      spam <- first:last
      
      NAs     <- which(is.na(x[spam,i])) + first-1
      nNAs    <- which(!is.na(x[spam,i])) + first-1
      sub_NAs <- NAs
      
      for (j in 1:length(NAs)){ sub_NAs[j] <- tail(nNAs[nNAs < NAs[j]],1)}
      
      x[NAs, i] <- x[sub_NAs, i]}}
  return(x)}