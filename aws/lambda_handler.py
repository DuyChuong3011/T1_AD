"""
AWS Lambda Handler for SCADA Fault Prediction API
Handles prediction requests and caches results in DynamoDB
"""

import json
import base64
import boto3
import logging
from datetime import datetime, timedelta
import os

# Initialize AWS clients
sagemaker_runtime = boto3.client("sagemaker-runtime")
dynamodb = boto3.resource("dynamodb")
cloudwatch = boto3.client("cloudwatch")

# Configuration from environment variables
ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "scada-fault-prediction-endpoint")
CACHE_TABLE_NAME = os.getenv("DYNAMODB_CACHE_TABLE", "scada-predictions-cache")
PROJECT = os.getenv("PROJECT_NAME", "T1_AD")

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get DynamoDB table
try:
    cache_table = dynamodb.Table(CACHE_TABLE_NAME)
except Exception as e:
    logger.warning(f"⚠️  Could not access DynamoDB table: {e}")
    cache_table = None


def get_cached_prediction(input_hash):
    """
    Lấy prediction từ cache nếu tồn tại và chưa hết TTL

    Args:
        input_hash (str): Hash của input features

    Returns:
        dict hoặc None: Cached prediction nếu tồn tại
    """
    if not cache_table:
        return None

    try:
        response = cache_table.get_item(Key={"InputHash": input_hash})
        if "Item" in response:
            item = response["Item"]
            expiry = datetime.fromisoformat(item["ExpiryTime"])

            if datetime.utcnow() < expiry:
                logger.info(f"✅ Cache hit for input hash: {input_hash}")
                return json.loads(item["Prediction"])
            else:
                # Cache expired, delete it
                cache_table.delete_item(Key={"InputHash": input_hash})
                logger.info(f"⏰ Cache expired for input hash: {input_hash}")
    except Exception as e:
        logger.error(f"❌ Error reading from cache: {e}")

    return None


def cache_prediction(input_hash, prediction, ttl_hours=1):
    """
    Lưu prediction vào DynamoDB cache với TTL

    Args:
        input_hash (str): Hash của input
        prediction (dict): Prediction result
        ttl_hours (int): Cache TTL in hours
    """
    if not cache_table:
        return

    try:
        expiry = datetime.utcnow() + timedelta(hours=ttl_hours)
        cache_table.put_item(
            Item={
                "InputHash": input_hash,
                "Prediction": json.dumps(prediction),
                "ExpiryTime": expiry.isoformat(),
                "Timestamp": datetime.utcnow().isoformat()
            }
        )
        logger.info(f"💾 Cached prediction for input hash: {input_hash}")
    except Exception as e:
        logger.error(f"❌ Error caching prediction: {e}")


def parse_request_body(event):
    """
    Parse request body từ API Gateway event

    Args:
        event (dict): Lambda event từ API Gateway

    Returns:
        dict: Parsed request body
    """
    try:
        # Handle both base64-encoded và plain JSON
        if event.get("isBase64Encoded"):
            body = base64.b64decode(event["body"])
            return json.loads(body)
        else:
            return json.loads(event.get("body", "{}"))
    except Exception as e:
        logger.error(f"❌ Error parsing request body: {e}")
        raise ValueError(f"Invalid request body: {e}")


def validate_features(features):
    """
    Validate input features có đúng format và đủ dữ liệu

    Args:
        features (dict): Input features

    Returns:
        bool: True if valid
    """
    required_features = [
        'Gearbox_Temp', 'Ambient_Temp', 'Wind_Speed', 'Wind_Dir_Sin', 'Wind_Dir_Cos',
        'Nacelle_Angle', 'Active_Power', 'Reactive_Power', 'Vibration',
        'Month', 'Hour', 'Lag_1'
    ]

    for feature in required_features:
        if feature not in features:
            raise ValueError(f"Missing required feature: {feature}")

    return True


def prepare_csv_for_inference(features):
    """
    Chuyển đổi features dict thành CSV format cho SageMaker XGBoost Endpoint

    Args:
        features (dict): Input features

    Returns:
        str: CSV string (không có header)
    """
    feature_order = [
        'Gearbox_Temp', 'Ambient_Temp', 'Wind_Speed', 'Wind_Dir_Sin', 'Wind_Dir_Cos',
        'Nacelle_Angle', 'Active_Power', 'Reactive_Power', 'Vibration',
        'Month', 'Hour', 'Lag_1'
    ]

    values = [str(features[f]) for f in feature_order]
    return ",".join(values)


def invoke_endpoint(csv_data):
    """
    Gọi SageMaker Endpoint để dự đoán

    Args:
        csv_data (str): CSV formatted input

    Returns:
        dict: Prediction result
    """
    try:
        logger.info(f"🔮 Invoking endpoint: {ENDPOINT_NAME}")

        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="text/csv",
            Body=csv_data
        )

        # Parse response
        result = json.loads(response["Body"].read().decode())
        logger.info(f"✅ Endpoint response: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error invoking endpoint: {e}")
        raise RuntimeError(f"Endpoint invocation failed: {e}")


def put_metric(metric_name, value, unit="Count"):
    """
    Push custom metric to CloudWatch

    Args:
        metric_name (str): Metric name
        value (float): Metric value
        unit (str): Metric unit
    """
    try:
        cloudwatch.put_metric_data(
            Namespace=f"SCADA/{PROJECT}",
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                    "Timestamp": datetime.utcnow()
                }
            ]
        )
    except Exception as e:
        logger.warning(f"⚠️  Could not put metric: {e}")


def create_response(status_code, body):
    """
    Create Lambda response cho API Gateway

    Args:
        status_code (int): HTTP status code
        body (dict): Response body

    Returns:
        dict: API Gateway response
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Main Lambda handler

    Event format:
    {
        "body": JSON string containing features
    }

    Response format:
    {
        "prediction": 0 or 1,
        "confidence": probability,
        "cached": true/false,
        "timestamp": ISO timestamp
    }
    """
    logger.info(f"📨 Received event: {json.dumps(event)}")

    try:
        # ─── Step 1: Parse request ───
        request_body = parse_request_body(event)
        features = request_body.get("features", {})

        logger.info(f"🔍 Input features: {features}")

        # ─── Step 2: Validate features ───
        validate_features(features)

        # ─── Step 3: Generate input hash for caching ───
        input_str = json.dumps(features, sort_keys=True)
        input_hash = hash(input_str) % (10 ** 8)  # Simple hash
        logger.info(f"📌 Input hash: {input_hash}")

        # ─── Step 4: Check cache ───
        cached_result = get_cached_prediction(str(input_hash))
        if cached_result:
            cached_result["cached"] = True
            put_metric("CacheHits", 1)
            return create_response(200, cached_result)

        # ─── Step 5: Prepare CSV ───
        csv_data = prepare_csv_for_inference(features)
        logger.info(f"📝 CSV data: {csv_data}")

        # ─── Step 6: Invoke endpoint ───
        endpoint_response = invoke_endpoint(csv_data)

        # ─── Step 7: Parse prediction ───
        # XGBoost returns: [[probability_class_0, probability_class_1]] hoặc [prediction]
        predictions = endpoint_response
        if isinstance(predictions, list):
            if isinstance(predictions[0], list):
                # Case: [[prob0, prob1]]
                prob_class_1 = predictions[0][1] if len(predictions[0]) > 1 else predictions[0][0]
                prediction = 1 if prob_class_1 > 0.5 else 0
            else:
                # Case: [prediction]
                prediction = int(predictions[0])
                prob_class_1 = predictions[0]
        else:
            prediction = int(predictions)
            prob_class_1 = predictions

        # ─── Step 8: Create response ───
        response = {
            "prediction": prediction,
            "confidence": float(prob_class_1),
            "fault_detected": prediction == 1,
            "cached": False,
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": ENDPOINT_NAME
        }

        # ─── Step 9: Cache result ───
        cache_prediction(str(input_hash), response, ttl_hours=1)

        # ─── Step 10: Put metrics ───
        put_metric("Predictions", 1)
        if prediction == 1:
            put_metric("FaultsDetected", 1)

        logger.info(f"✅ Prediction complete: {response}")
        return create_response(200, response)

    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        return create_response(400, {"error": str(e), "type": "ValidationError"})

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
        put_metric("Errors", 1)
        return create_response(500, {"error": str(e), "type": "InternalError"})
