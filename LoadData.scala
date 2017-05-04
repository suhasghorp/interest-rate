package com.suhasghorp.loanperf.core

import org.apache.spark.sql.SparkSession

import org.apache.spark.SparkContext

import org.apache.spark.rdd.RDD.rddToPairRDDFunctions

import org.apache.spark.sql.{ SQLContext, SaveMode }

import org.apache.spark.sql.types.{ StructType, DataTypes }

import com.suhasghorp.loanperf.structtypes._

import org.apache.spark.sql.functions.unix_timestamp

object LoadData {

  def main(args: Array[String]) = {
    
    val inputDir = args(0)
    val outputDir = args(1)
    val warehouseDir = args(2)
    

    val sparkSession = SparkSession
      .builder
      .master("local[*]")
      .appName("loanperf")
      .config("spark.sql.warehouse.dir", warehouseDir) //"file:///C:/loanperf")
      //.enableHiveSupport()
      .getOrCreate()

    import sparkSession.implicits._

    val fannieLoansSchemaStruct = StructTypeUtil.getFannieLoansStructType()

    val fannieLoansRawDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "dateFormat" -> "MM/yyyy",
        "inferSchema" -> "true",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .option("delimiter", "|")

      .schema(fannieLoansSchemaStruct)

      //.load("file:///C:/loanperf/fanniemae/loans/*")
      .load(inputDir +"/fanniemae/loans/*")
      .write.mode(SaveMode.Overwrite).parquet(outputDir + "/parquet/fanniemae/loans")

      //.cache
     val fannieLoansRawParquetDF = sparkSession.read.parquet(outputDir + "/parquet/fanniemae/loans")
    fannieLoansRawParquetDF.createOrReplaceTempView("fannie_loans_raw")

    val freddieLoansSchemaStruct = StructTypeUtil.getFreddieLoansStructType

    val freddieLoansRawDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "dateFormat" -> "yyyyMM",

        "inferSchema" -> "true",

        "delimiter" -> "|",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(freddieLoansSchemaStruct)

      .load(inputDir +"/freddiemac/loans/*")

     .write.mode(SaveMode.Overwrite).parquet(outputDir + "/parquet/freddiemac/loans")
     
 val freddieLoansRawParquetDF = sparkSession.read.parquet(outputDir + "/parquet/freddiemac/loans")
    freddieLoansRawParquetDF.createOrReplaceTempView("freddie_loans_raw")

    val fannieMonthlyObsSchemaStruct = StructTypeUtil.getFannieMonthlyObsStructType

    val matDate = unix_timestamp($"maturityDate", "MM/yyyy").cast("timestamp").cast(DataTypes.DateType).alias("zeroBalanceDate")

    val zbalDate = unix_timestamp($"zeroBalanceDate", "MM/yyyy").cast("timestamp").cast(DataTypes.DateType).alias("zeroBalanceDate")

    val fannieMonthlyObsRawDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "dateFormat" -> "MM/dd/yyyy",

        "inferSchema" -> "true",

        "delimiter" -> "|",

        "mode" -> "DROPMALFORMED"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(fannieMonthlyObsSchemaStruct)

      .load(inputDir +"/fanniemae/monthly/*")

      .toDF()

      .withColumn("maturityDate", matDate)

      .withColumn("zeroBalanceDate", zbalDate)

      .write.mode(SaveMode.Overwrite).parquet(outputDir + "/parquet/fanniemae/monthly")
     
     val fannieMonthlyObsRawParquetDF = sparkSession.read.parquet(outputDir + "/parquet/fanniemae/monthly")    

    fannieMonthlyObsRawParquetDF.createOrReplaceTempView("fannie_monthly_raw")
    

    val freddieMonthlyObsSchemaStruct = StructTypeUtil.getFreddieMonthlyObsStructType

    val freddieMonthlyObsRawDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "dateFormat" -> "yyyyMM",

        "inferSchema" -> "true",

        "delimiter" -> "|",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(freddieMonthlyObsSchemaStruct)

      .load(inputDir +"/freddiemac/monthly/*")
      .write.mode(SaveMode.Overwrite).parquet(outputDir + "/parquet/freddiemac/monthly")
     
     val freddieMonthlyObsRawParquetDF = sparkSession.read.parquet(outputDir + "/parquet/freddiemac/monthly")   

    freddieMonthlyObsRawParquetDF.createOrReplaceTempView("freddie_monthly_raw")

    val hpiIndexesDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "dateFormat" -> "yyyy-MM-dd",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "inferSchema" -> "true",

        "delimiter" -> "|",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(new StructType().add("id", DataTypes.IntegerType).add("name", DataTypes.StringType)

        .add("type", DataTypes.StringType).add("firstDate", DataTypes.DateType))

      .load(inputDir +"/static/hpi_index_codes.txt").cache

    hpiIndexesDF.createOrReplaceTempView("hpi_indexes")

    val hpiValuesDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "dateFormat" -> "yyyy-MM-dd",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "inferSchema" -> "true",

        "delimiter" -> "|",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(new StructType().add("hpiIndexId", DataTypes.IntegerType).add("obsDate", DataTypes.DateType).add("hpi", DataTypes.DoubleType))

      .load(inputDir +"/static/interpolated_hpi_values.txt").cache

    hpiValuesDF.createOrReplaceTempView("hpi_values")

    val mortgageRatesDF = sparkSession

      .read

      .options(Map(

        "header" -> "false",

        "dateFormat" -> "yyyy-MM-dd",

        "ignoreLeadingWhiteSpace" -> "true",

        "ignoreTrailingWhiteSpace" -> "true",

        "inferSchema" -> "true",

        "delimiter" -> ",",

        "mode" -> "PERMISSIVE"))

      .format("org.apache.spark.sql.execution.datasources.csv.CSVFileFormat")

      .schema(new StructType().add("month", DataTypes.DateType).add("rate", DataTypes.DoubleType).add("points", DataTypes.DoubleType).add("zeroPointRate", DataTypes.DoubleType))

      .load(inputDir +"/static/pmms.csv").cache

    mortgageRatesDF.createOrReplaceTempView("mortgage_rates")

    val servicersDF = sparkSession.sql(

      "select distinct servicerName from " +

        "(select sellerName as servicerName from fannie_loans_raw " +

        "union " +

        "select servicerName as servicerName from fannie_monthly_raw " +

        "union " +

        "select sellerName as servicerName from freddie_loans_raw " +

        "union " +

        " select servicerName as servicerName from freddie_loans_raw) t where servicerName is not null").toDF().cache

    servicersDF.take(5).foreach(println)

    servicersDF.createOrReplaceTempView("servicers")

    val fannieLoansDF = sparkSession.sql("SELECT " +

      "0 AS agency, " +

      "creditScore, " +

      "firstPaymentDate, " +

      "firstTimeHomebuyerIndicator, " +

      "add_months(firstPaymentDate, originalLoanTerm), " +

      "mf.msa, " +

      "mip, " +

      "numberOfUnits, " +

      "CASE occupancyStatus WHEN 'P' THEN 'O' WHEN 'S' THEN 'S' WHEN 'I' THEN 'I' END, " +

      "originalCLTV, " +

      "dti, " +

      "originalUPB, " +

      "originalLTV, " +

      "originalInterestRate, " +

      "channel, " +

      "'N', " +

      "productType, " +

      "propertyState, " +

      "propertyType, " +

      "concat(zipCode,'00'), " +

      "l.loanSequenceNumber, " +

      "CASE loanPurpose WHEN 'P' THEN 'P' WHEN 'C' THEN 'C' WHEN 'R' THEN 'N' WHEN 'U' THEN 'U' END, " +

      "originalLoanTerm, " +

      "numberOfBorrowers, " +

      "regexp_replace(sel.servicerName,'\\,', '') AS servicerName, " +

      "NULL, " +

      "COALESCE(COALESCE(hpi_msa.id, hpi_state.id), 0), " +

      "hpi.hpi, " +

      "COALESCE(mz.zeroBalanceCode, 0), " +

      "mz.zeroBalanceDate AS loansZeroBalanceDate, " +

      "md.firstSeriousDqDate, " +

      "originalInterestRate - rates.zeroPointRate, " +

      "NULL, " +

      "NULL, " +

      "NULL, " +

      "NULL, " +

      "coBorrowerCreditScore, " +

      "year(firstPaymentDate) " +

      "from fannie_loans_raw l " +

      "LEFT JOIN servicers sel " +

      "ON l.sellerName = sel.servicerName " +

      "LEFT JOIN (SELECT " +

      "          loanSequenceNumber, " +

      "          servicerName, " +

      "          case msa when null then 0 else msa end AS msa, " +

      "          ROW_NUMBER() OVER (PARTITION BY loanSequenceNumber " +

      "ORDER BY reportingPeriod ASC) " +

      "AS row_num " +

      "FROM fannie_monthly_raw) mf " +

      "ON l.loanSequenceNumber = mf.loanSequenceNumber " +

      "AND mf.row_num = 1 " +

      "LEFT JOIN (SELECT " +

      "           loanSequenceNumber, " +

      "           reportingPeriod, " +

      "           zeroBalanceCode, " +

      "           zeroBalanceDate, " +

      "           ROW_NUMBER() OVER (PARTITION BY loanSequenceNumber " +

      "     ORDER BY reportingPeriod ASC)  " +

      "     AS row_num " +

      "         FROM fannie_monthly_raw " +

      "         WHERE zeroBalanceCode IS NOT NULL) mz " +

      "ON l.loanSequenceNumber = mz.loanSequenceNumber " +

      "AND mz.row_num = 1 " +

      "LEFT JOIN (SELECT " +

      "           loanSequenceNumber, " +

      "           reportingPeriod AS firstSeriousDqDate, " +

      "           ROW_NUMBER() OVER (PARTITION BY loanSequenceNumber " +

      "     ORDER BY reportingPeriod ASC) " +

      "     AS row_num " +

      "         FROM fannie_monthly_raw " +

      "         WHERE dqStatus IN ('2','3','4','5','6')) md " +

      "ON l.loanSequenceNumber = md.loanSequenceNumber " +

      "AND md.row_num = 1 " +

      "LEFT JOIN hpi_indexes hpi_msa " +

      "ON mf.msa = hpi_msa.id " +

      "LEFT JOIN hpi_indexes hpi_state " +

      "ON l.propertyState = hpi_state.name " +

      "LEFT JOIN hpi_values hpi " +

      "ON hpi.hpiIndexId = COALESCE(COALESCE(hpi_msa.id, hpi_state.id), 0) " +

      "AND hpi.obsDate = add_months(firstPaymentDate, -2) " +

      "LEFT JOIN mortgage_rates rates " +

      "ON rates.month = add_months(firstPaymentDate, -2) " +

      "WHERE add_months(l.firstPaymentDate, -1) > COALESCE(hpi_msa.firstDate, to_date('1970-01-01')) ")

    fannieLoansDF.take(5).foreach(println)

    fannieLoansDF.createOrReplaceTempView("fannie_loans")

    val fannieMonthlyDF = sparkSession.sql("SELECT " +

      "l.servicerName, " +

      "m.reportingPeriod, " +

      "m.currentUPB, " +

      "m_prev.currentUPB, " +

      "COALESCE(m.dqStatus, -1), " +

      "COALESCE(m_prev.dqStatus, -1), " +

      "m.loanAge, " +

      "m.rmm, " +

      "CASE WHEN (m.zeroBalanceCode = '06' and m.zeroBalanceDate is not null) THEN 'Y' ELSE 'N' END, " +

      "m.modificationFlag, " +

      "m.zeroBalanceCode, " +

      "m.zeroBalanceDate, " +

      "m.currentInterestRate " +

      "FROM fannie_monthly_raw m " +

      "INNER JOIN fannie_loans l " +

      "ON m.loanSequenceNumber = l.loanSequenceNumber " +

      "AND l.agency = 0 " +

      "LEFT JOIN fannie_monthly_raw m_prev " +

      "ON m.loanSequenceNumber = m_prev.loanSequenceNumber " +

      "AND m.reportingPeriod = add_months(m_prev.reportingPeriod, 1)")

    fannieMonthlyDF.createOrReplaceTempView("fannie_monthly")

    fannieMonthlyDF.take(5).foreach(println)

    sparkSession.stop()

  }

}
