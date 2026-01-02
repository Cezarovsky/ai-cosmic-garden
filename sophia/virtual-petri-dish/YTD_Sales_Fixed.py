# YTD_Sales_Fixed.py
# Production-ready PySpark ETL with intelligent merge strategy
# Fixes the duplicate record issue in original YTD_Sales.py
# JIRA: DP-6386 - YTD_Sales Data mismatch resolution

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Widget parameters for production flexibility
dbutils.widgets.text("bronze_catalog_name", "catalog_30_bronze", "Bronze Catalog Name")
dbutils.widgets.text("silver_catalog_name", "catalog_20_silver", "Silver Catalog Name")
dbutils.widgets.text("target_schema", "reporting_all", "Target Schema")
dbutils.widgets.text("target_table", "ytd_sales", "Target Table")
dbutils.widgets.dropdown("write_mode", "overwrite", ["overwrite", "append"], "Write Mode")
dbutils.widgets.text("gold_source_system", "GOLD", "Gold Source System Filter")
dbutils.widgets.text("generation_source_system", "GENERATION", "Generation Source System Filter")

# Get parameter values
BRONZE_CATALOG = dbutils.widgets.get("bronze_catalog_name")
SILVER_CATALOG = dbutils.widgets.get("silver_catalog_name")
TARGET_SCHEMA = dbutils.widgets.get("target_schema")
TARGET_TABLE = dbutils.widgets.get("target_table")
WRITE_MODE = dbutils.widgets.get("write_mode")
GOLD_SOURCE = dbutils.widgets.get("gold_source_system")
GENERATION_SOURCE = dbutils.widgets.get("generation_source_system")

# Gold branch data extraction
orders_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.ORDER").filter(F.col("sourceSystemname") == GOLD_SOURCE)
order_lines_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.ORDER_LINE").filter(F.col("sourceSystemname") == GOLD_SOURCE)
trading_partners_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.TRADING_PARTNER")
packaged_items_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.PACKAGED_ITEM")
items_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.ITEM")
sub_groups_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.SUB_GROUP")
main_groups_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.MAIN_GROUP")
persons_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.PERSON")
classes_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.CLASS")
pricing_grid_df = spark.table(f"{BRONZE_CATALOG}.gold_delta.PRICING_GRID")

gold_df = orders_df.alias("o") \
    .join(order_lines_df.alias("ol"), F.col("o.ORDER_NUMBER") == F.col("ol.ORDER_NUMBER"), "inner") \
    .join(trading_partners_df.alias("tp"), F.col("o.TRADING_PARTNER_NUMBER") == F.col("tp.TRADING_PARTNER_NUMBER"), "left") \
    .join(packaged_items_df.alias("pi"), F.col("ol.PACKAGED_ITEM_NUMBER") == F.col("pi.PACKAGED_ITEM_NUMBER"), "left") \
    .join(items_df.alias("itm"), F.col("pi.ITEM_NUMBER") == F.col("itm.ITEM_NUMBER"), "left") \
    .join(sub_groups_df.alias("sg"), F.col("pi.SUBGROUP_NUMBER") == F.col("sg.SUBGROUP_NUMBER"), "left") \
    .join(main_groups_df.alias("mg"), F.col("sg.GROUP_NUMBER") == F.col("mg.GROUP_NUMBER"), "left") \
    .join(persons_df.alias("p"), F.col("ol.REPRESENTATIVE") == F.col("p.PERSON_NUMBER"), "left") \
    .join(classes_df.alias("cls"), F.col("pi.CLASS_NUMBER") == F.col("cls.CLASS_NUMBER"), "left") \
    .join(pricing_grid_df.alias("pg"), F.col("ol.PRICING_GRID_HEADER_NUMBER") == F.col("pg.PRICING_GRID_HEADER_NUMBER"), "left") \
    .select(
        F.col("tp.TRADING_PARTNER_NUMBER"), F.col("tp.TRADING_PARTNER_TYPE_NUMBER"), F.col("tp.ACCOUNT_REFERENCE"),
        F.col("ol.ORDER_LINE_NUMBER"), F.col("o.ORDER_NUMBER"), F.col("p.PERSON_NUMBER"), F.col("cls.CLASS_NUMBER"),
        F.col("pi.PACKAGE_NUMBER"), F.col("pi.PACKAGED_ITEM_NUMBER"), F.col("ol.PAYMENT_SCHEME_NUMBER"),
        F.col("ol.PAYMENT_TERMS_NUMBER"), F.col("ol.PGL_PAYMENT_TERMS_NUMBER"), F.col("ol.PRICING_GRID_HEADER_NUMBER"),
        F.col("ol.DEPARTMENT_NUMBER"), F.col("mg.GROUP_NUMBER"), F.col("ol.FORWARDING_REGION_NUMBER"),
        F.col("tp.TRADING_PARTNER_CATEGORY_NUMBER"), F.col("ol.LOCATION_NUMBER"), F.col("ol.STOCK_LOCATION_NUMBER"),
        F.col("ol.FINANCE_SCHEME_NUMBER"), F.col("ol.FORECAST_HEADER_NUMBER"), F.col("ol.FORECAST_SALES_TEAM_NUMBER"),
        F.col("ol.TEAM_NUMBER"), F.col("ol.TRANSPORT_TERMS_NUMBER"), F.col("ol.RISK_TYPE_NUMBER"), F.col("itm.ITEM_NUMBER"),
        F.lit(None).cast(IntegerType()).alias("MIXTURE_NUMBER"), F.col("ol.TRADING_SEASON_NUMBER"),
        F.col("mg.GROUP_NUMBER").alias("MAIN_GROUP_NUMBER"), F.col("sg.SUBGROUP_NUMBER"),
        F.col("o.ORDER_REFERENCE"), F.col("pi.PACKAGED_ITEM_REFERENCE"), F.col("pi.PACKAGE_REFERENCE"),
        F.col("tp.TRADING_PARTNER_REFERENCE"), F.col("ol.ORDER_INTERNAL_REFERENCE"), F.col("itm.ITEM_REFERENCE"),
        F.lit(None).cast(StringType()).alias("MIXTURE_REFERENCE"), F.col("tp.LEDGER_BALANCE"), F.col("tp.MAXIMUM_CREDIT_LIMIT"),
        F.col("p.CUSTOMER_REPRESENTATIVE"), F.col("o.ORDER_TYPE"), F.col("ol.ORDER_STATUS_NUMBER"), F.col("o.PREPAYMENT_ORDER"),
        F.col("ol.ORDER_STATUS_DESCRIPTION"), F.col("ol.ORDER_LINE_STATUS_NUMBER"), F.col("ol.ORDER_LINE_STATUS_DESCRIPTION"),
        F.col("p.PERSON_NAME"), F.col("p.OPERATOR"), F.col("p.REPRESENTATIVE"), F.col("tp.INSTITUTION_NAME"),
        F.col("tp.TRADING_PARTNER_SHORT_NAME"), F.col("tp.ACCOUNT_TYPE"), F.col("tp.VAT_REGISTRATION_NUMBER"),
        F.col("tp.TRADING_PARTNER_STATUS_NUMBER"), F.col("tp.TRADING_LIMIT"), F.col("tp.TRADING_PARTNER_TYPE_DESCRIPTION"),
        F.col("ol.TRADING_SEASON_CODE"), F.col("ol.DEPARTMENT_NAME"), F.col("ol.ENTITY_MNEMONIC"), F.col("ol.TRANSPORT_TERMS_CODE"),
        F.col("p.REPS_CODE"), F.col("cls.CLASS_CODE"), F.col("cls.CLASS_DESCRIPTION"), F.col("ol.LOCATION_DESCRIPTION"),
        F.lit(None).cast(StringType()).alias("GRADE_CODE"), F.lit(None).cast(StringType()).alias("GRADE_DESCRIPTION"),
        F.lit(None).cast(StringType()).alias("GRADE_GROUP_CODE"), F.lit(None).cast(StringType()).alias("GRADE_GROUP_DESCRIPTION"),
        F.col("ol.MULTIPLE_ACCOUNTS_NUMBER"), F.col("ol.MULTIPLE_ACCOUNT_DESCRIPTION"), F.col("ol.MACHINE"),
        F.col("tp.ADDRESS_COUNTY"), F.col("tp.ADDRESS_LOCALITY"), F.col("tp.ADDRESS_NAME"), F.col("tp.ADDRESS_POSTTOWN"),
        F.col("tp.ADDRESS_STREET"), F.col("tp.ADDRESS_POSTCODE_AREA"), F.col("tp.ADDRESS_POSTCODE_DISTRICT"),
        F.col("mg.MAIN_GROUP_CODE"), F.col("mg.MAIN_GROUP_DESCRIPTION"), F.col("sg.SUBGROUP_CODE"), F.col("sg.SUBGROUP_DESCRIPTION"),
        F.col("ol.LOCATION_CODE"), F.col("ol.LOCATION_NAME"), F.col("ol.LOCATION_SHORT_NAME"), F.col("pi.PACKAGE_SHORT_NAME"),
        F.col("pi.PACKAGE_DESCRIPTION"), F.col("pi.PACKAGE_WEIGHT"), F.col("pi.PACKAGED_ITEM_DESCRIPTION"), F.col("pi.MAX_PRICE"),
        F.col("pi.PACKAGED_ITEM_SHORTNAME"), F.col("itm.ITEM_DESCRIPTION"), F.lit(None).cast(StringType()).alias("MIXTURE_DESCRIPTION"),
        F.col("ol.RISK_TYPE_DESCRIPTION"), F.col("o.SALE_OR_PURCHASE"), F.col("ol.CONTRACT_FORM_NUMBER"),
        F.col("ol.CONTRACT_OR_ORDER"), F.lit(None).cast(IntegerType()).alias("TREATMENT_NUMBER"), F.lit(None).cast(StringType()).alias("TREATMENT_DESCRIPTION"),
        F.col("ol.DEFERRED_PAYMENT_DATE"), F.col("ol.DEFERRED_PAYMENT_TIME"), F.col("o.ORDER_DATE"), F.col("o.ORDER_TIME"),
        F.col("o.ORDER_DATE_ENTERED"), F.col("o.ORDER_TIME_ENTERED"), F.col("ol.PAYMENT_DUE_DATE"), F.col("ol.PAYMENT_DUE_TIME"),
        F.col("ol.PAYMENT_DATE"), F.col("ol.PAYMENT_TIME"), F.col("ol.PSP_PAYMENT_DATE"), F.col("ol.PSP_PAYMENT_TIME"),
        F.col("ol.PROVIDE_TRANSPORT"), F.col("ol.COST_PRICE"), F.col("ol.REQUIRED_ARRIVAL_FROM_DATE"),
        F.col("ol.REQUIRED_ARRIVAL_FROM_TIME"), F.col("ol.REQUIRED_ARRIVAL_TO_DATE"), F.col("ol.REQUIRED_ARRIVAL_TO_TIME"),
        F.col("ol.DELIVERED_QUANTITY"), F.col("ol.GROUP_CUSTOMER_NUMBER"), F.col("ol.HAULAGE_ESTIMATE"),
        F.col("ol.ORDERED_QUANTITY"), F.col("ol.UNIT_PRICE"), F.col("ol.NET_PRICE"), F.col("ol.BASE_PRICE_NUMBER"),
        F.col("ol.DISCOUNT_PERCENTAGE"), F.col("ol.INVOICED_QUANTITY"), F.col("ol.FREE_OF_CHARGE"),
        F.col("ol.PAYMENT_SCHEME_CODE"), F.col("ol.PAYMENT_SCHEME_DESCRIPTION"), F.col("ol.PAYMENT_TERMS_CODE"),
        F.col("ol.PAYMENT_TERMS_DESCRIPTION"), F.col("ol.DAY_NUMBER"), F.col("ol.NUMBER_OF_DAYS"), F.col("ol.NUMBER_OF_MONTHS"),
        F.col("ol.TEAM_DESCRIPTION"), F.col("ol.COMMERCIAL_TEAM"), F.col("ol.COMMERCIAL_REGION"), F.col("ol.UOM_MNEMONIC"),
        F.col("ol.TRADING_SEASON_DESCRIPTION"), F.col("ol.FORECAST_DESCRIPTION"), F.col("ol.FORECAST_SALES_TEAM_DESC"),
        F.current_timestamp().alias("INSERT_TS"), F.lit("Gold").alias("SOURCE")
    )

# Generation branch data extraction  
gen_orders_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.ORDER").filter(F.col("sourceSystemname") == GENERATION_SOURCE)
gen_order_lines_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.ORDER_LINE").filter(F.col("sourceSystemname") == GENERATION_SOURCE)
gen_trading_partners_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.TRADING_PARTNER")
mixtures_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.MIXTURE")
gen_items_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.ITEM")
gen_sub_groups_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.SUB_GROUP")
gen_main_groups_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.MAIN_GROUP")
gen_persons_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.PERSON")
treatments_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.TREATMENT")
grades_df = spark.table(f"{BRONZE_CATALOG}.generation_delta.GRADE")

generation_df = gen_orders_df.alias("o") \
    .join(gen_order_lines_df.alias("ol"), F.col("o.ORDER_NUMBER") == F.col("ol.ORDER_NUMBER"), "inner") \
    .join(gen_trading_partners_df.alias("tp"), F.col("o.TRADING_PARTNER_NUMBER") == F.col("tp.TRADING_PARTNER_NUMBER"), "left") \
    .join(mixtures_df.alias("mx"), F.col("ol.MIXTURE_NUMBER") == F.col("mx.MIXTURE_NUMBER"), "left") \
    .join(gen_items_df.alias("itm"), F.col("mx.ITEM_NUMBER") == F.col("itm.ITEM_NUMBER"), "left") \
    .join(gen_sub_groups_df.alias("sg"), F.col("mx.SUBGROUP_NUMBER") == F.col("sg.SUBGROUP_NUMBER"), "left") \
    .join(gen_main_groups_df.alias("mg"), F.col("sg.GROUP_NUMBER") == F.col("mg.GROUP_NUMBER"), "left") \
    .join(gen_persons_df.alias("p"), F.col("ol.REPRESENTATIVE") == F.col("p.PERSON_NUMBER"), "left") \
    .join(treatments_df.alias("tr"), F.col("ol.TREATMENT_NUMBER") == F.col("tr.TREATMENT_NUMBER"), "left") \
    .join(grades_df.alias("gr"), F.col("ol.GRADE_NUMBER") == F.col("gr.GRADE_NUMBER"), "left") \
    .select(
        F.col("tp.TRADING_PARTNER_NUMBER"), F.col("tp.TRADING_PARTNER_TYPE_NUMBER"), F.col("tp.ACCOUNT_REFERENCE"),
        F.col("ol.ORDER_LINE_NUMBER"), F.col("o.ORDER_NUMBER"), F.col("p.PERSON_NUMBER"), F.lit(None).cast(IntegerType()).alias("CLASS_NUMBER"),
        F.lit(None).cast(IntegerType()).alias("PACKAGE_NUMBER"), F.lit(None).cast(IntegerType()).alias("PACKAGED_ITEM_NUMBER"), F.col("ol.PAYMENT_SCHEME_NUMBER"),
        F.col("ol.PAYMENT_TERMS_NUMBER"), F.col("ol.PGL_PAYMENT_TERMS_NUMBER"), F.lit(None).cast(IntegerType()).alias("PRICING_GRID_HEADER_NUMBER"),
        F.col("ol.DEPARTMENT_NUMBER"), F.col("mg.GROUP_NUMBER"), F.col("ol.FORWARDING_REGION_NUMBER"),
        F.col("tp.TRADING_PARTNER_CATEGORY_NUMBER"), F.col("ol.LOCATION_NUMBER"), F.col("ol.STOCK_LOCATION_NUMBER"),
        F.col("ol.FINANCE_SCHEME_NUMBER"), F.col("ol.FORECAST_HEADER_NUMBER"), F.col("ol.FORECAST_SALES_TEAM_NUMBER"),
        F.col("ol.TEAM_NUMBER"), F.col("ol.TRANSPORT_TERMS_NUMBER"), F.col("ol.RISK_TYPE_NUMBER"), F.col("itm.ITEM_NUMBER"),
        F.col("mx.MIXTURE_NUMBER"), F.col("ol.TRADING_SEASON_NUMBER"),
        F.col("mg.GROUP_NUMBER").alias("MAIN_GROUP_NUMBER"), F.col("sg.SUBGROUP_NUMBER"),
        F.col("o.ORDER_REFERENCE"), F.lit(None).cast(StringType()).alias("PACKAGED_ITEM_REFERENCE"), F.lit(None).cast(StringType()).alias("PACKAGE_REFERENCE"),
        F.col("tp.TRADING_PARTNER_REFERENCE"), F.col("ol.ORDER_INTERNAL_REFERENCE"), F.col("itm.ITEM_REFERENCE"),
        F.col("mx.MIXTURE_REFERENCE"), F.col("tp.LEDGER_BALANCE"), F.col("tp.MAXIMUM_CREDIT_LIMIT"),
        F.col("p.CUSTOMER_REPRESENTATIVE"), F.col("o.ORDER_TYPE"), F.col("ol.ORDER_STATUS_NUMBER"), F.col("o.PREPAYMENT_ORDER"),
        F.col("ol.ORDER_STATUS_DESCRIPTION"), F.col("ol.ORDER_LINE_STATUS_NUMBER"), F.col("ol.ORDER_LINE_STATUS_DESCRIPTION"),
        F.col("p.PERSON_NAME"), F.col("p.OPERATOR"), F.col("p.REPRESENTATIVE"), F.col("tp.INSTITUTION_NAME"),
        F.col("tp.TRADING_PARTNER_SHORT_NAME"), F.col("tp.ACCOUNT_TYPE"), F.col("tp.VAT_REGISTRATION_NUMBER"),
        F.col("tp.TRADING_PARTNER_STATUS_NUMBER"), F.col("tp.TRADING_LIMIT"), F.col("tp.TRADING_PARTNER_TYPE_DESCRIPTION"),
        F.col("ol.TRADING_SEASON_CODE"), F.col("ol.DEPARTMENT_NAME"), F.col("ol.ENTITY_MNEMONIC"), F.col("ol.TRANSPORT_TERMS_CODE"),
        F.col("p.REPS_CODE"), F.lit(None).cast(StringType()).alias("CLASS_CODE"), F.lit(None).cast(StringType()).alias("CLASS_DESCRIPTION"), F.col("ol.LOCATION_DESCRIPTION"),
        F.col("gr.GRADE_CODE"), F.col("gr.GRADE_DESCRIPTION"), F.col("gr.GRADE_GROUP_CODE"), F.col("gr.GRADE_GROUP_DESCRIPTION"),
        F.col("ol.MULTIPLE_ACCOUNTS_NUMBER"), F.col("ol.MULTIPLE_ACCOUNT_DESCRIPTION"), F.col("ol.MACHINE"),
        F.col("tp.ADDRESS_COUNTY"), F.col("tp.ADDRESS_LOCALITY"), F.col("tp.ADDRESS_NAME"), F.col("tp.ADDRESS_POSTTOWN"),
        F.col("tp.ADDRESS_STREET"), F.col("tp.ADDRESS_POSTCODE_AREA"), F.col("tp.ADDRESS_POSTCODE_DISTRICT"),
        F.col("mg.MAIN_GROUP_CODE"), F.col("mg.MAIN_GROUP_DESCRIPTION"), F.col("sg.SUBGROUP_CODE"), F.col("sg.SUBGROUP_DESCRIPTION"),
        F.col("ol.LOCATION_CODE"), F.col("ol.LOCATION_NAME"), F.col("ol.LOCATION_SHORT_NAME"), F.lit(None).cast(StringType()).alias("PACKAGE_SHORT_NAME"),
        F.lit(None).cast(StringType()).alias("PACKAGE_DESCRIPTION"), F.lit(None).cast(DoubleType()).alias("PACKAGE_WEIGHT"), F.lit(None).cast(StringType()).alias("PACKAGED_ITEM_DESCRIPTION"), F.lit(None).cast(DoubleType()).alias("MAX_PRICE"),
        F.lit(None).cast(StringType()).alias("PACKAGED_ITEM_SHORTNAME"), F.col("itm.ITEM_DESCRIPTION"), F.col("mx.MIXTURE_DESCRIPTION"),
        F.col("ol.RISK_TYPE_DESCRIPTION"), F.col("o.SALE_OR_PURCHASE"), F.col("ol.CONTRACT_FORM_NUMBER"),
        F.col("ol.CONTRACT_OR_ORDER"), F.col("tr.TREATMENT_NUMBER"), F.col("tr.TREATMENT_DESCRIPTION"),
        F.col("ol.DEFERRED_PAYMENT_DATE"), F.col("ol.DEFERRED_PAYMENT_TIME"), F.col("o.ORDER_DATE"), F.col("o.ORDER_TIME"),
        F.col("o.ORDER_DATE_ENTERED"), F.col("o.ORDER_TIME_ENTERED"), F.col("ol.PAYMENT_DUE_DATE"), F.col("ol.PAYMENT_DUE_TIME"),
        F.col("ol.PAYMENT_DATE"), F.col("ol.PAYMENT_TIME"), F.col("ol.PSP_PAYMENT_DATE"), F.col("ol.PSP_PAYMENT_TIME"),
        F.col("ol.PROVIDE_TRANSPORT"), F.col("ol.COST_PRICE"), F.col("ol.REQUIRED_ARRIVAL_FROM_DATE"),
        F.col("ol.REQUIRED_ARRIVAL_FROM_TIME"), F.col("ol.REQUIRED_ARRIVAL_TO_DATE"), F.col("ol.REQUIRED_ARRIVAL_TO_TIME"),
        F.col("ol.DELIVERED_QUANTITY"), F.col("ol.GROUP_CUSTOMER_NUMBER"), F.col("ol.HAULAGE_ESTIMATE"),
        F.col("ol.ORDERED_QUANTITY"), F.col("ol.UNIT_PRICE"), F.col("ol.NET_PRICE"), F.col("ol.BASE_PRICE_NUMBER"),
        F.col("ol.DISCOUNT_PERCENTAGE"), F.col("ol.INVOICED_QUANTITY"), F.col("ol.FREE_OF_CHARGE"),
        F.col("ol.PAYMENT_SCHEME_CODE"), F.col("ol.PAYMENT_SCHEME_DESCRIPTION"), F.col("ol.PAYMENT_TERMS_CODE"),
        F.col("ol.PAYMENT_TERMS_DESCRIPTION"), F.col("ol.DAY_NUMBER"), F.col("ol.NUMBER_OF_DAYS"), F.col("ol.NUMBER_OF_MONTHS"),
        F.col("ol.TEAM_DESCRIPTION"), F.col("ol.COMMERCIAL_TEAM"), F.col("ol.COMMERCIAL_REGION"), F.col("ol.UOM_MNEMONIC"),
        F.col("ol.TRADING_SEASON_DESCRIPTION"), F.col("ol.FORECAST_DESCRIPTION"), F.col("ol.FORECAST_SALES_TEAM_DESC"),
        F.current_timestamp().alias("INSERT_TS"), F.lit("Generation").alias("SOURCE")
    )
# Intelligent merge instead of UNION ALL
merged_df = gold_df.alias("g").join(generation_df.alias("gen"), ["ORDER_NUMBER", "ORDER_LINE_NUMBER"], "full_outer")

final_df = merged_df.select(
    # Business Key Columns
    F.coalesce(F.col("g.TRADING_PARTNER_NUMBER"), F.col("gen.TRADING_PARTNER_NUMBER")).alias("TRADING_PARTNER_NUMBER"),
    F.coalesce(F.col("g.TRADING_PARTNER_TYPE_NUMBER"), F.col("gen.TRADING_PARTNER_TYPE_NUMBER")).alias("TRADING_PARTNER_TYPE_NUMBER"),
    F.coalesce(F.col("g.ACCOUNT_REFERENCE"), F.col("gen.ACCOUNT_REFERENCE")).alias("ACCOUNT_REFERENCE"),
    F.coalesce(F.col("g.ORDER_LINE_NUMBER"), F.col("gen.ORDER_LINE_NUMBER")).alias("ORDER_LINE_NUMBER"),
    F.coalesce(F.col("g.ORDER_NUMBER"), F.col("gen.ORDER_NUMBER")).alias("ORDER_NUMBER"),
    F.coalesce(F.col("g.PERSON_NUMBER"), F.col("gen.PERSON_NUMBER")).alias("PERSON_NUMBER"),
    F.col("g.CLASS_NUMBER").alias("CLASS_NUMBER"),
    F.col("g.PACKAGE_NUMBER").alias("PACKAGE_NUMBER"),
    F.col("g.PACKAGED_ITEM_NUMBER").alias("PACKAGED_ITEM_NUMBER"),
    F.coalesce(F.col("g.PAYMENT_SCHEME_NUMBER"), F.col("gen.PAYMENT_SCHEME_NUMBER")).alias("PAYMENT_SCHEME_NUMBER"),
    F.coalesce(F.col("g.PAYMENT_TERMS_NUMBER"), F.col("gen.PAYMENT_TERMS_NUMBER")).alias("PAYMENT_TERMS_NUMBER"),
    F.coalesce(F.col("g.PGL_PAYMENT_TERMS_NUMBER"), F.col("gen.PGL_PAYMENT_TERMS_NUMBER")).alias("PGL_PAYMENT_TERMS_NUMBER"),
    F.col("g.PRICING_GRID_HEADER_NUMBER").alias("PRICING_GRID_HEADER_NUMBER"),
    F.coalesce(F.col("g.DEPARTMENT_NUMBER"), F.col("gen.DEPARTMENT_NUMBER")).alias("DEPARTMENT_NUMBER"),
    F.coalesce(F.col("g.GROUP_NUMBER"), F.col("gen.GROUP_NUMBER")).alias("GROUP_NUMBER"),
    F.coalesce(F.col("g.FORWARDING_REGION_NUMBER"), F.col("gen.FORWARDING_REGION_NUMBER")).alias("FORWARDING_REGION_NUMBER"),
    F.coalesce(F.col("g.TRADING_PARTNER_CATEGORY_NUMBER"), F.col("gen.TRADING_PARTNER_CATEGORY_NUMBER")).alias("TRADING_PARTNER_CATEGORY_NUMBER"),
    F.coalesce(F.col("g.LOCATION_NUMBER"), F.col("gen.LOCATION_NUMBER")).alias("LOCATION_NUMBER"),
    F.coalesce(F.col("g.STOCK_LOCATION_NUMBER"), F.col("gen.STOCK_LOCATION_NUMBER")).alias("STOCK_LOCATION_NUMBER"),
    F.coalesce(F.col("g.FINANCE_SCHEME_NUMBER"), F.col("gen.FINANCE_SCHEME_NUMBER")).alias("FINANCE_SCHEME_NUMBER"),
    F.coalesce(F.col("g.FORECAST_HEADER_NUMBER"), F.col("gen.FORECAST_HEADER_NUMBER")).alias("FORECAST_HEADER_NUMBER"),
    F.coalesce(F.col("g.FORECAST_SALES_TEAM_NUMBER"), F.col("gen.FORECAST_SALES_TEAM_NUMBER")).alias("FORECAST_SALES_TEAM_NUMBER"),
    F.coalesce(F.col("g.TEAM_NUMBER"), F.col("gen.TEAM_NUMBER")).alias("TEAM_NUMBER"),
    F.coalesce(F.col("g.TRANSPORT_TERMS_NUMBER"), F.col("gen.TRANSPORT_TERMS_NUMBER")).alias("TRANSPORT_TERMS_NUMBER"),
    F.coalesce(F.col("g.RISK_TYPE_NUMBER"), F.col("gen.RISK_TYPE_NUMBER")).alias("RISK_TYPE_NUMBER"),
    F.coalesce(F.col("g.ITEM_NUMBER"), F.col("gen.ITEM_NUMBER")).alias("ITEM_NUMBER"),
    F.col("gen.MIXTURE_NUMBER").alias("MIXTURE_NUMBER"),
    F.coalesce(F.col("g.TRADING_SEASON_NUMBER"), F.col("gen.TRADING_SEASON_NUMBER")).alias("TRADING_SEASON_NUMBER"),
    F.coalesce(F.col("g.MAIN_GROUP_NUMBER"), F.col("gen.MAIN_GROUP_NUMBER")).alias("MAIN_GROUP_NUMBER"),
    F.coalesce(F.col("g.SUBGROUP_NUMBER"), F.col("gen.SUBGROUP_NUMBER")).alias("SUBGROUP_NUMBER"),

    # Reference Columns
    F.coalesce(F.col("g.ORDER_REFERENCE"), F.col("gen.ORDER_REFERENCE")).alias("ORDER_REFERENCE"),
    F.col("g.PACKAGED_ITEM_REFERENCE").alias("PACKAGED_ITEM_REFERENCE"),
    F.col("g.PACKAGE_REFERENCE").alias("PACKAGE_REFERENCE"),
    F.coalesce(F.col("g.TRADING_PARTNER_REFERENCE"), F.col("gen.TRADING_PARTNER_REFERENCE")).alias("TRADING_PARTNER_REFERENCE"),
    F.coalesce(F.col("g.ORDER_INTERNAL_REFERENCE"), F.col("gen.ORDER_INTERNAL_REFERENCE")).alias("ORDER_INTERNAL_REFERENCE"),
    F.coalesce(F.col("g.ITEM_REFERENCE"), F.col("gen.ITEM_REFERENCE")).alias("ITEM_REFERENCE"),
    F.col("gen.MIXTURE_REFERENCE").alias("MIXTURE_REFERENCE"),
    F.coalesce(F.col("g.LEDGER_BALANCE"), F.col("gen.LEDGER_BALANCE")).alias("LEDGER_BALANCE"),
    F.coalesce(F.col("g.MAXIMUM_CREDIT_LIMIT"), F.col("gen.MAXIMUM_CREDIT_LIMIT")).alias("MAXIMUM_CREDIT_LIMIT"),

    # Descriptive Columns
    F.coalesce(F.col("g.CUSTOMER_REPRESENTATIVE"), F.col("gen.CUSTOMER_REPRESENTATIVE")).alias("CUSTOMER_REPRESENTATIVE"),
    F.coalesce(F.col("g.ORDER_TYPE"), F.col("gen.ORDER_TYPE")).alias("ORDER_TYPE"),
    F.coalesce(F.col("g.ORDER_STATUS_NUMBER"), F.col("gen.ORDER_STATUS_NUMBER")).alias("ORDER_STATUS_NUMBER"),
    F.coalesce(F.col("g.PREPAYMENT_ORDER"), F.col("gen.PREPAYMENT_ORDER")).alias("PREPAYMENT_ORDER"),
    F.coalesce(F.col("g.ORDER_STATUS_DESCRIPTION"), F.col("gen.ORDER_STATUS_DESCRIPTION")).alias("ORDER_STATUS_DESCRIPTION"),
    F.coalesce(F.col("g.ORDER_LINE_STATUS_NUMBER"), F.col("gen.ORDER_LINE_STATUS_NUMBER")).alias("ORDER_LINE_STATUS_NUMBER"),
    F.coalesce(F.col("g.ORDER_LINE_STATUS_DESCRIPTION"), F.col("gen.ORDER_LINE_STATUS_DESCRIPTION")).alias("ORDER_LINE_STATUS_DESCRIPTION"),
    F.coalesce(F.col("g.PERSON_NAME"), F.col("gen.PERSON_NAME")).alias("PERSON_NAME"),
    F.coalesce(F.col("g.OPERATOR"), F.col("gen.OPERATOR")).alias("OPERATOR"),
    F.coalesce(F.col("g.REPRESENTATIVE"), F.col("gen.REPRESENTATIVE")).alias("REPRESENTATIVE"),
    F.coalesce(F.col("g.INSTITUTION_NAME"), F.col("gen.INSTITUTION_NAME")).alias("INSTITUTION_NAME"),
    F.coalesce(F.col("g.TRADING_PARTNER_SHORT_NAME"), F.col("gen.TRADING_PARTNER_SHORT_NAME")).alias("TRADING_PARTNER_SHORT_NAME"),
    F.coalesce(F.col("g.ACCOUNT_TYPE"), F.col("gen.ACCOUNT_TYPE")).alias("ACCOUNT_TYPE"),
    F.coalesce(F.col("g.VAT_REGISTRATION_NUMBER"), F.col("gen.VAT_REGISTRATION_NUMBER")).alias("VAT_REGISTRATION_NUMBER"),
    F.coalesce(F.col("g.TRADING_PARTNER_STATUS_NUMBER"), F.col("gen.TRADING_PARTNER_STATUS_NUMBER")).alias("TRADING_PARTNER_STATUS_NUMBER"),
    F.coalesce(F.col("g.TRADING_LIMIT"), F.col("gen.TRADING_LIMIT")).alias("TRADING_LIMIT"),
    F.coalesce(F.col("g.TRADING_PARTNER_TYPE_DESCRIPTION"), F.col("gen.TRADING_PARTNER_TYPE_DESCRIPTION")).alias("TRADING_PARTNER_TYPE_DESCRIPTION"),
    F.coalesce(F.col("g.TRADING_SEASON_CODE"), F.col("gen.TRADING_SEASON_CODE")).alias("TRADING_SEASON_CODE"),
    F.coalesce(F.col("g.DEPARTMENT_NAME"), F.col("gen.DEPARTMENT_NAME")).alias("DEPARTMENT_NAME"),
    F.coalesce(F.col("g.ENTITY_MNEMONIC"), F.col("gen.ENTITY_MNEMONIC")).alias("ENTITY_MNEMONIC"),
    F.coalesce(F.col("g.TRANSPORT_TERMS_CODE"), F.col("gen.TRANSPORT_TERMS_CODE")).alias("TRANSPORT_TERMS_CODE"),
    F.coalesce(F.col("g.REPS_CODE"), F.col("gen.REPS_CODE")).alias("REPS_CODE"),
    F.col("g.CLASS_CODE").alias("CLASS_CODE"),
    F.col("g.CLASS_DESCRIPTION").alias("CLASS_DESCRIPTION"),
    F.coalesce(F.col("g.LOCATION_DESCRIPTION"), F.col("gen.LOCATION_DESCRIPTION")).alias("LOCATION_DESCRIPTION"),
    F.col("gen.GRADE_CODE").alias("GRADE_CODE"),
    F.col("gen.GRADE_DESCRIPTION").alias("GRADE_DESCRIPTION"),
    F.col("gen.GRADE_GROUP_CODE").alias("GRADE_GROUP_CODE"),
    F.col("gen.GRADE_GROUP_DESCRIPTION").alias("GRADE_GROUP_DESCRIPTION"),

    # Transactional Columns
    F.when((F.col("g.DELIVERED_QUANTITY").isNotNull()) & (F.col("g.DELIVERED_QUANTITY") != 0.0), 
           F.col("g.DELIVERED_QUANTITY")).otherwise(F.col("gen.DELIVERED_QUANTITY")).alias("DELIVERED_QUANTITY"),
    F.coalesce(F.col("g.UNIT_PRICE"), F.col("gen.UNIT_PRICE")).alias("UNIT_PRICE"),
    F.col("g.NET_PRICE").alias("NET_PRICE"),
    F.col("g.DISCOUNT_PERCENTAGE").alias("DISCOUNT_PERCENTAGE"),

    # Date Columns
    F.coalesce(F.col("g.ORDER_DATE"), F.col("gen.ORDER_DATE")).alias("ORDER_DATE"),
    F.col("g.PAYMENT_DATE").alias("PAYMENT_DATE"),
    
    # Special Columns
    F.col("gen.TREATMENT_NUMBER").alias("TREATMENT_NUMBER"),
    F.col("gen.TREATMENT_DESCRIPTION").alias("TREATMENT_DESCRIPTION"),

    # System Columns
    F.greatest(F.coalesce(F.col("g.INSERT_TS"), F.col("gen.INSERT_TS")), 
               F.coalesce(F.col("gen.INSERT_TS"), F.col("g.INSERT_TS"))).alias("INSERT_TS"),
    F.when(F.col("g.ORDER_NUMBER").isNotNull() & F.col("gen.ORDER_NUMBER").isNotNull(), F.lit("Merged"))
     .when(F.col("g.ORDER_NUMBER").isNotNull(), F.lit("Gold"))
     .otherwise(F.lit("Generation")).alias("SOURCE")
)

# Data quality check
duplicate_count = final_df.groupBy("ORDER_NUMBER", "ORDER_LINE_NUMBER").count().filter(F.col("count") > 1).count()
if duplicate_count > 0:
    raise ValueError(f"Data quality issue: {duplicate_count} duplicate business keys found")

# Write to target
target_path = f"{SILVER_CATALOG}.{TARGET_SCHEMA}.{TARGET_TABLE}"
final_df.write.format("delta").mode(WRITE_MODE).option("mergeSchema", "true").saveAsTable(target_path)