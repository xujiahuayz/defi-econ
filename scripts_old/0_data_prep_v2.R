
library(data.table)
library(ggplot2)
library(stringr)
library(bit64)
library(reshape2)
library(lubridate)
library(readxl)
library(padr)
library(zoo)
library(dplyr)
########################
### set up directory ###
########################
dir_main <- "/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/"

dir_output <- paste0(dir_main, '3_cleaned_data/')
dir_in <- paste0(dir_main,'2_raw_data/data_network/v2/inflow_centrality/')
dir_out <- paste0(dir_main,'2_raw_data/data_network/v2/outflow_centrality/')
dir_aave <- paste0(dir_main, '2_raw_data/data_aave/')
dir_compound <- paste0(dir_main, '2_raw_data/data_compound')
dir_gas <- '/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/2_raw_data/data_global/gas_fee/gas_volatility.csv'
dir_global <- paste0(dir_main, '2_raw_data/data_global/')
dir_gas_eth <- '/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/2_raw_data/data_global/gas_fee/gas_volatility_ETH.csv'
### Functions ###
#################

clean_global_level_data <- function(df) {
  df[,1] <- NULL
  df <- melt(df, id.vars = "Date")
  colnames(df)[1] <- "date"
  colnames(df)[2] <- "token"
  return(df)
}

### Loop in uniswap data ###
############################

### Inflow Centrality

list_day <- list()

for (file in list.files(dir_in)){
  
    dir_file <-  paste0(dir_in,file)
    df_day <- fread(dir_file)
    df_day <- df_day[,-1]
    df_day[,date := substr(file,15,22)]
    names(df_day)[4:7] <- c("eigencentrality_in","trading_volume_total","trading_volume_in","trading_volume_out")
    
    list_day[[file]] <- df_day
    print(paste0("I am doing ",file))
}

df_uniswap_1 <- rbindlist(list_day)


### Outflow Centrality

list_day <- list()

for (file in list.files(dir_out)){
  
  dir_file <-  paste0(dir_out,file)
  df_day <- fread(dir_file)
  df_day <- df_day[,c(2,5)]
  df_day[,date := substr(file,15,22)]
  names(df_day)[2] <- c("eigencentrality_out")
  
  list_day[[file]] <- df_day
  print(paste0("I am doing ",file))
}

df_uniswap_2 <- rbindlist(list_day)

## Clean the date
df_uniswap <- merge(df_uniswap_1,df_uniswap_2,by = c("token",'date'))
df_uniswap[,date := as.Date(date,"%Y%m%d")]

######################################
### Loop in aave and compound data ###
######################################

## Load in Avve 
df_aave <- fread(paste0(dir_aave,"aave_all_token_historical_data.csv"))
df_aave <- df_aave[,c("day",'token','total_borrow_in_usd','total_supply_in_usd')]

df_aave[,date := as.Date(day)]
df_aave$day <- NULL


## Load in Compound 

compound_list <- list.dirs(dir_compound)
compound_list <- compound_list[-1]


compound_all <- list()

for (file in compound_list){
  df_compound_list <- list()
  for (token in list.files(file)){
    df <- fread(paste0(file,'/',token))

    if (nrow(df) != 1){
      df <- df[,-1]
      df_compound_list[[token]] <- df
    }
    print(paste0("I am doing ",token))
  }
  compound_all[[file]] <- rbindlist(df_compound_list)
}

df_compound <- rbindlist(compound_all)
df_compound[,date := as.Date(date)]
df_compound[ctoken_symbol == "ETH", ctoken_symbol := "WETH"]


### Cleaning 
names(df_compound)[c(1,3,4)] <- c("token","lend_compound","borrow_compound")
names(df_aave)[2:3] <- c("borrow_aave","lend_aave")

df_defi <- merge(df_compound,df_aave, by = c("token","date"), all = T)


######################################
### Loop in global level data ########
######################################


## Market Cap
df_mcap <- fread(paste0(dir_global,'/token_market/',"primary_token_marketcap.csv"))
df_mcap2 <- fread(paste0(dir_global,'/token_market/',"primary_token_marketcap_2.csv"))
df_mcap <- clean_global_level_data(df_mcap)
df_mcap2 <- clean_global_level_data(df_mcap2)

df_mcap <- rbind(df_mcap,df_mcap2)
colnames(df_mcap)[3] <- "mcap"

## Token Price USD
df_price <- fread(paste0(dir_global,'/token_market/',"primary_token_price.csv"))
df_price2 <- fread(paste0(dir_global,'/token_market/',"primary_token_price_2.csv"))

df_price <- clean_global_level_data(df_price)
df_price2 <- clean_global_level_data(df_price2)

df_price <- rbind(df_price,df_price2)

colnames(df_price)[3] <- "price_USD"

## Token Price ETH

df_price_eth <- fread(paste0(dir_global,'/token_market/',"primary_token_price_ETH.csv"))
df_price2_eth <- fread(paste0(dir_global,'/token_market/',"primary_token_price_ETH_2.csv"))


df_price_eth <- clean_global_level_data(df_price_eth)
df_price2_eth <- clean_global_level_data(df_price2_eth)

df_price_eth <- rbind(df_price_eth,df_price2_eth)

colnames(df_price_eth)[3] <- "price_ETH"

## Token Volatility_USD

df_vol_eth <- fread(paste0(dir_global,'/token_market/',"primary_token_volatility_ETH.csv"))
df_vol2_eth <- fread(paste0(dir_global,'/token_market/',"primary_token_volatility_ETH_2.csv"))

df_vol_eth <- clean_global_level_data(df_vol_eth)
df_vol2_eth <- clean_global_level_data(df_vol2_eth)

df_vol_eth <- rbind(df_vol_eth,df_vol2_eth)
colnames(df_vol_eth)[3] <- "price_volatility_ETH"

## Token Volatility_USD

df_vol <- fread(paste0(dir_global,'/token_market/',"primary_token_volatility.csv"))
df_vol2 <- fread(paste0(dir_global,'/token_market/',"primary_token_volatility_2.csv"))

df_vol <- clean_global_level_data(df_vol)
df_vol2 <- clean_global_level_data(df_vol2)

df_vol <- rbind(df_vol,df_vol2)
colnames(df_vol)[3] <- "price_volatility_USD"


## Gas
df_gas <- fread(dir_gas)
df_gas <- df_gas[,-1] 
names(df_gas) <- c('date','gas_fee','gas_fee_volatility')
df_gas[,date := as.Date(date, "%m/%d/%Y")]

## Gas_ETH
df_gas_eth <- fread(dir_gas_eth)
df_gas_eth <- df_gas_eth[,-1] 
names(df_gas_eth) <- c('date','gas_fee_eth','gas_fee_volatility_eth')
df_gas_eth[,date := as.Date(date, "%m/%d/%Y")]

## SNP index
df_snp <- read_xls('/Users/yuantian/123 Dropbox/Yuan Tian/dominant_defi/data/2_raw_data/global_data/snp_Index.xls')
names(df_snp) <- c("date","S&P_digital_Market_Index")
setDT(df_snp)[,date := as.Date(date)]
df_snp <- pad(df_snp)

df_snp$`_digital_Market_Index` <- na.approx(df_snp$`S&P_digital_Market_Index`)

### Merge in everything ###
###########################

df_uniswap <- merge(df_uniswap,df_gas, by = "date",all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap,df_gas_eth, by = "date",all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_vol_eth, by = c("token","date"), all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_price_eth, by = c("token","date"), all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_vol, by = c("token","date"), all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_price, by = c("token","date"), all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_mcap, by = c("token","date"), all.x = T, all.y = F)

df_uniswap <- merge(df_uniswap, df_defi, by = c("token","date"), all.x = T,
                      all.y = F)
df_uniswap <- merge(df_uniswap, df_snp, by = c("date"), all.x = T,
                    all.y = F)


### Construct additional variables ###
######################################

df_uniswap[,log_price_usd := log(price_USD)]
df_uniswap[,log_gas_price_usd := log(gas_fee)]
names(df_uniswap)[10:11] <- c("gas_price_usd","gas_price_volatility_usd")
names(df_uniswap)[12:13] <- c("gas_price_eth","gas_price_volatility_eth")


df_uniswap[is.na(borrow_compound), borrow_compound := 0]
df_uniswap[is.na(borrow_aave), borrow_aave := 0]
df_uniswap[is.na(lend_compound), lend_compound := 0]
df_uniswap[is.na(lend_aave), lend_aave := 0]

df_uniswap[,borrow_total := borrow_compound + borrow_aave]
df_uniswap[,lend_total := lend_compound + lend_aave]

df_uniswap[,borrow_total_relative := borrow_total/mcap]
df_uniswap[,lend_total_relative := lend_total/mcap]

## Some post-merge cleanings

df_uniswap <- df_uniswap[token != '',]

write.table(df_uniswap, file = paste0(dir_output,"defi_data_v2_20220829.csv"),
            row.names = F,col.names = T, sep = ",")
