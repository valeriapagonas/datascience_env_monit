library(readr)
library(dplyr)

keep <- c("TIMESTAMP_START", "TIMESTAMP_END", "TA_F", "SW_IN_F", "VPD_F", "P_F",
          "NETRAD", "G_F_MDS", "H_F_MDS", "H_F_MDS_QC", "LE_F_MDS", "LE_F_MDS_QC",
          "NEE_VUT_REF", "NEE_VUT_REF_QC", "GPP_NT_VUT_REF", "RECO_NT_VUT_REF")

zip_file <- list.files("data/raw", pattern = "\\.zip$", full.names = TRUE)[1]
hh_name  <- grep("FLUXMET_HH", unzip(zip_file, list = TRUE)$Name, value = TRUE)
unzip(zip_file, files = hh_name, exdir = "data/raw/unzipped")

hh <- read_csv(file.path("data/raw/unzipped", hh_name),
               na = "-9999",
               col_select = any_of(keep),
               col_types = cols(TIMESTAMP_START = "c", TIMESTAMP_END = "c", .default = "d")) |>
  mutate(time = as.POSIXct(TIMESTAMP_START, format = "%Y%m%d%H%M", tz = "UTC"))

nrow(hh)
range(hh$time)
mean(hh$NEE_VUT_REF_QC == 0, na.rm = TRUE)   # share of measured NEE