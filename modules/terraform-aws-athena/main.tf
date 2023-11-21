variable "database_name" {
  type    = string
}

variable "table_name" {
  type    = string
}

variable "s3_location" {
  type    = string
}

data "aws_caller_identity" "current_caller" {}

resource "aws_s3_bucket" "athena_query_results" {
  bucket = "alcon-workshop-athena-output-${data.aws_caller_identity.current_caller.id}"
}

resource "aws_glue_catalog_database" "athena_database" {
  name = var.database_name
}

resource "aws_glue_catalog_table" "athena_table" {
  database_name = aws_glue_catalog_database.athena_database.name
  name    = var.table_name

  # Add more columns as needed
  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "parquet.compression" = "SNAPPY"
  }

  storage_descriptor {
    location      = var.s3_location
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }
    columns {
      name = "FIRST_NAME"
      type = "varchar(50)"
    }
    columns {
      name = "LAST_NAME"
      type = "varchar(50)"
    }
    columns {
      name = "SEX"
      type = "varchar(7)"
    }
    columns {
      name = "AGE"
      type = "smallint"
    }
    columns {
      name = "DATE_DIED"
      type = "varchar(20)"
    }
    columns {
      name = "INGESTION_DATETIME"
      type = "timestamp"
    }
    columns {
      name = "IS_DEAD"
      type = "boolean"
    }
    columns {
      name = "FULL_NAME"
      type = "varchar(100)"
    }
  }
}

resource "aws_athena_workgroup" "athena_alcon_workshop_workgroup" {
  name = "athena_alcon_workshop_workgroup"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_query_results.bucket}/athena-query-results/"
    }
  }
}

resource "aws_athena_named_query" "athena_named_query" {
  database          = var.database_name
  name              = "athena_alcon_workshop_named_query"
  query             = "SELECT * FROM ${var.table_name}"
  description       = "Example Named Query for Athena"
  workgroup         = aws_athena_workgroup.athena_alcon_workshop_workgroup.id
}

output "athena_table_name" {
  value = aws_glue_catalog_table.athena_table.name
}

output "athena_table_location" {
  value = aws_glue_catalog_table.athena_table.storage_descriptor.0.location
}

output "athena_named_query_id" {
  value = aws_athena_named_query.athena_named_query.id
}
