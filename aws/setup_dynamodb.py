"""
Setup DynamoDB table cho prediction caching
Giúp giảm latency + tiết kiệm chi phí endpoint invocation
"""

import boto3
from datetime import datetime

# Configuration
REGION = "ap-southeast-1"
TABLE_NAME = "scada-predictions-cache"
BILLING_MODE = "PAY_PER_REQUEST"  # On-demand pricing
TTL_ATTRIBUTE = "ExpiryTime"  # TTL attribute name

# Initialize clients
dynamodb = boto3.client("dynamodb", region_name=REGION)
cloudwatch = boto3.client("cloudwatch", region_name=REGION)


def create_cache_table():
    """
    Tạo DynamoDB table cho prediction caching

    Table schema:
    - Partition Key: InputHash (string)
    - Attribute: Prediction (JSON)
    - Attribute: ExpiryTime (ISO timestamp)
    - Attribute: Timestamp (Creation time)

    TTL: 1 hour (tự động delete expired items)
    """
    print(f"📊 [Step 1] Đang tạo DynamoDB table: {TABLE_NAME}...")

    try:
        # Check if table already exists
        existing_table = dynamodb.describe_table(TableName=TABLE_NAME)
        print(f"✅ Table {TABLE_NAME} đã tồn tại")
        print(f"   Status: {existing_table['Table']['TableStatus']}")
        return existing_table['Table']['TableArn']

    except dynamodb.exceptions.ResourceNotFoundException:
        # Table doesn't exist, create it
        print(f"   Tạo table mới...")

        response = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    "AttributeName": "InputHash",
                    "KeyType": "HASH"  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "InputHash",
                    "AttributeType": "S"  # String
                }
            ],
            BillingMode=BILLING_MODE,
            Tags=[
                {"Key": "Project", "Value": "T1_AD"},
                {"Key": "Purpose", "Value": "Prediction-Cache"},
                {"Key": "Environment", "Value": "Production"},
                {"Key": "CreatedAt", "Value": datetime.utcnow().isoformat()}
            ]
        )

        table_arn = response["TableDescription"]["TableArn"]
        print(f"✅ Table created: {table_arn}")

        # Wait for table to become active
        print(f"⏳ Đang chờ table trở thành ACTIVE...")
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=TABLE_NAME)
        print(f"✅ Table is now ACTIVE")

        return table_arn


def enable_ttl():
    """
    Enable Time-To-Live (TTL) trên table
    Items sẽ tự động xóa khi hết hạn

    TTL attribute: ExpiryTime (ISO timestamp format)
    """
    print(f"\n⏰ [Step 2] Đang setup TTL trên table...")

    try:
        # Check current TTL status
        response = dynamodb.describe_time_to_live(TableName=TABLE_NAME)
        ttl_status = response.get("TimeToLiveDescription", {})

        if ttl_status.get("TimeToLiveStatus") == "ENABLED":
            print(f"✅ TTL đã được enable với attribute: {ttl_status['AttributeName']}")
            return

        print(f"   Enabling TTL...")

        dynamodb.update_time_to_live(
            TableName=TABLE_NAME,
            TimeToLiveSpecification={
                "AttributeName": TTL_ATTRIBUTE,
                "Enabled": True
            }
        )

        print(f"✅ TTL enabled")
        print(f"   Attribute: {TTL_ATTRIBUTE}")
        print(f"   Items sẽ tự động xóa khi hết hạn")

    except Exception as e:
        print(f"❌ Error enabling TTL: {e}")
        raise


def setup_monitoring():
    """
    Setup CloudWatch monitoring cho DynamoDB table
    """
    print(f"\n📈 [Step 3] Đang setup CloudWatch monitoring...")

    try:
        # Create alarm for consumed read capacity
        cloudwatch.put_metric_alarm(
            AlarmName=f"{TABLE_NAME}-high-read-throttling",
            MetricName="ReadThrottleEvents",
            Namespace="AWS/DynamoDB",
            Statistic="Sum",
            Period=300,
            EvaluationPeriods=1,
            Threshold=5,
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            Dimensions=[
                {"Name": "TableName", "Value": TABLE_NAME}
            ],
            AlarmActions=[],  # Add SNS topic ARN if needed
            TreatMissingData="notBreaching"
        )

        print(f"✅ CloudWatch alarm created: {TABLE_NAME}-high-read-throttling")

        # Create dashboard widget
        print(f"✅ CloudWatch monitoring configured")
        print(f"   Check AWS CloudWatch Console for metrics")

    except Exception as e:
        print(f"⚠️  Warning setting up monitoring: {e}")


def print_table_info():
    """
    In ra thông tin table
    """
    table_info = dynamodb.describe_table(TableName=TABLE_NAME)["Table"]

    print("\n" + "="*70)
    print("🎉 DYNAMODB TABLE SETUP COMPLETE")
    print("="*70)
    print(f"Table Name         : {table_info['TableName']}")
    print(f"Table Status       : {table_info['TableStatus']}")
    print(f"Table ARN          : {table_info['TableArn']}")
    print(f"Billing Mode       : {table_info['BillingModeSummary']['BillingMode']}")
    print(f"Item Count         : {table_info.get('ItemCount', 'N/A')}")
    print(f"Size (bytes)       : {table_info.get('TableSizeBytes', 'N/A')}")
    print(f"Created Time       : {table_info['CreationDateTime']}")

    # Get TTL info
    try:
        ttl_response = dynamodb.describe_time_to_live(TableName=TABLE_NAME)
        ttl_status = ttl_response.get("TimeToLiveDescription", {})
        print(f"TTL Status         : {ttl_status.get('TimeToLiveStatus', 'N/A')}")
        if ttl_status.get("TimeToLiveStatus") == "ENABLED":
            print(f"TTL Attribute      : {ttl_status['AttributeName']}")
    except:
        pass

    print("="*70)
    print("\n📝 Usage in Lambda:")
    print("   import boto3")
    print("   dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')")
    print(f"   table = dynamodb.Table('{TABLE_NAME}')")
    print("   table.put_item(Item={'InputHash': '123456', 'Prediction': '...', 'ExpiryTime': '2024-07-31T...:00Z'})")
    print("="*70)


def get_table_stats():
    """
    Get current table statistics
    """
    print(f"\n📊 Fetching table statistics...")

    try:
        response = dynamodb.describe_table(TableName=TABLE_NAME)
        table = response["Table"]

        stats = {
            "item_count": table.get("ItemCount", 0),
            "size_bytes": table.get("TableSizeBytes", 0),
            "read_capacity": table.get("ProvisionedThroughput", {}).get("ReadCapacityUnits", "N/A"),
            "write_capacity": table.get("ProvisionedThroughput", {}).get("WriteCapacityUnits", "N/A"),
            "billing_mode": table.get("BillingModeSummary", {}).get("BillingMode", "N/A")
        }

        print(f"✅ Table Statistics:")
        print(f"   Items       : {stats['item_count']}")
        print(f"   Size        : {stats['size_bytes'] / 1024 / 1024:.2f} MB")
        print(f"   Billing Mode: {stats['billing_mode']}")

        return stats

    except Exception as e:
        print(f"⚠️  Could not fetch stats: {e}")
        return None


def main():
    """
    Main setup pipeline
    """
    print("🚀 Starting DynamoDB Cache Setup...\n")

    try:
        # Step 1: Create table
        table_arn = create_cache_table()

        # Step 2: Enable TTL
        enable_ttl()

        # Step 3: Setup monitoring
        setup_monitoring()

        # Step 4: Print info
        print_table_info()

        # Step 5: Get stats
        get_table_stats()

        print("\n✅ Setup hoàn tất! DynamoDB table sẵn sàng dùng cho prediction caching")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
