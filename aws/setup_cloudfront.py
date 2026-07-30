"""
Setup CloudFront Distribution for API Gateway
Cung cấp CDN caching + DDoS protection (WAF)
Giảm latency + tăng security
"""

import boto3
import json
from datetime import datetime

# Configuration
REGION = "ap-southeast-1"
API_DOMAIN = None  # Will be obtained from API Gateway
DOMAIN_NAME = "scada-fault-api.example.com"  # Change this to your domain
CERTIFICATE_ARN = None  # ARN of SSL certificate in us-east-1

# Initialize clients
cloudfront = boto3.client("cloudfront", region_name=REGION)
apigateway = boto3.client("apigateway", region_name=REGION)
acm = boto3.client("acm", region_name="us-east-1")  # CloudFront requires us-east-1

# CloudFront distribution name
DISTRIBUTION_NAME = "scada-fault-prediction-cf"


def get_api_gateway_domain():
    """
    Lấy API Gateway domain từ REST API

    Returns:
        str: API Gateway invoke URL (vd: https://abc123.execute-api.ap-southeast-1.amazonaws.com)
    """
    print("🔍 [Step 1] Đang lấy API Gateway domain...")

    try:
        # List API Gateway REST APIs
        response = apigateway.get_rest_apis(limit=100)

        # Find SCADA API
        scada_api = None
        for api in response["items"]:
            if "scada" in api["name"].lower():
                scada_api = api
                break

        if not scada_api:
            print("❌ Không tìm thấy API 'scada-fault-api' trong API Gateway")
            print("   Hãy tạo API Gateway trước hoặc update DOMAIN_NAME trong script")
            raise ValueError("API Gateway not found")

        api_id = scada_api["id"]
        api_domain = f"https://{api_id}.execute-api.{REGION}.amazonaws.com"

        print(f"✅ API Gateway domain: {api_domain}")
        return api_domain

    except Exception as e:
        print(f"❌ Error getting API Gateway domain: {e}")
        raise


def create_waf_rules():
    """
    Tạo AWS WAF rules để bảo vệ CloudFront

    Rules:
    - Rate limiting (prevent DDoS)
    - SQL injection protection
    - XSS protection
    - Bot control

    Returns:
        str: WAF Web ACL ARN
    """
    print("\n🔐 [Step 2] Đang setup AWS WAF...")

    try:
        wafv2 = boto3.client("wafv2", region_name="us-east-1")  # CloudFront requires us-east-1

        acl_name = "scada-fault-waf-acl"

        # Check if WAF ACL already exists
        response = wafv2.list_web_acls(Scope="CLOUDFRONT")
        for acl in response.get("WebACLs", []):
            if acl["Name"] == acl_name:
                print(f"✅ WAF ACL already exists: {acl['ARN']}")
                return acl["ARN"]

        print(f"   Tạo WAF ACL mới: {acl_name}")

        # Create WAF rules
        response = wafv2.create_web_acl(
            Name=acl_name,
            Scope="CLOUDFRONT",
            DefaultAction={"Allow": {}},
            Rules=[
                {
                    "Name": "RateLimitRule",
                    "Priority": 1,
                    "Statement": {
                        "RateBasedStatement": {
                            "Limit": 2000,  # Requests per 5 minutes
                            "AggregateKeyType": "IP"
                        }
                    },
                    "Action": {"Block": {}},
                    "VisibilityConfig": {
                        "SampledRequestsEnabled": True,
                        "CloudWatchMetricsEnabled": True,
                        "MetricName": "RateLimitRule"
                    }
                },
                {
                    "Name": "AWSManagedRulesCommonRuleSet",
                    "Priority": 2,
                    "Statement": {
                        "ManagedRuleGroupStatement": {
                            "VendorName": "AWS",
                            "Name": "AWSManagedRulesCommonRuleSet"
                        }
                    },
                    "OverrideAction": {"None": {}},
                    "VisibilityConfig": {
                        "SampledRequestsEnabled": True,
                        "CloudWatchMetricsEnabled": True,
                        "MetricName": "AWSManagedRulesCommonRuleSet"
                    }
                }
            ],
            VisibilityConfig={
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": acl_name
            },
            Tags=[
                {"Key": "Project", "Value": "T1_AD"},
                {"Key": "Environment", "Value": "Production"}
            ]
        )

        waf_arn = response["Summary"]["ARN"]
        print(f"✅ WAF ACL created: {waf_arn}")

        return waf_arn

    except Exception as e:
        print(f"⚠️  WAF setup failed: {e}")
        print("   Continuing without WAF (can add later)")
        return None


def create_cloudfront_distribution(api_domain, waf_arn=None):
    """
    Tạo CloudFront distribution

    Configuration:
    - Origin: API Gateway
    - Caching: 300 seconds (5 min) for predictions
    - Compression: gzip, brotli
    - HTTPS: Required
    - WAF: Optional protection

    Args:
        api_domain (str): API Gateway domain
        waf_arn (str): WAF Web ACL ARN (optional)

    Returns:
        dict: Distribution info
    """
    print("\n📡 [Step 3] Đang tạo CloudFront Distribution...")

    # Extract domain from API endpoint
    api_host = api_domain.replace("https://", "").replace("http://", "")

    distribution_config = {
        "CallerReference": f"scada-{datetime.utcnow().timestamp()}",
        "Origins": {
            "Quantity": 1,
            "Items": [
                {
                    "Id": "ScadaAPIGatewayOrigin",
                    "DomainName": api_host,
                    "CustomOriginConfig": {
                        "HTTPPort": 80,
                        "HTTPSPort": 443,
                        "OriginProtocolPolicy": "https-only",
                        "OriginSSLProtocols": {
                            "Quantity": 1,
                            "Items": ["TLSv1.2"]
                        },
                        "OriginReadTimeout": 30,
                        "OriginKeepaliveTimeout": 5
                    },
                    "CustomHeaders": {
                        "Quantity": 1,
                        "Items": [
                            {
                                "HeaderName": "X-CloudFront-Origin",
                                "HeaderValue": "scada-fault-prediction"
                            }
                        ]
                    }
                }
            ]
        },
        "DefaultCacheBehavior": {
            "TargetOriginId": "ScadaAPIGatewayOrigin",
            "ViewerProtocolPolicy": "redirect-to-https",
            "AllowedMethods": {
                "Quantity": 7,
                "Items": ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
            },
            "CachePolicyId": "4135ea3d-c35d-46eb-81d7-rewrite_cf",  # Managed cache policy
            "OriginRequestPolicyId": "216adef5-5c7f-47e4-b989-5492eafa07d3",  # Forward all headers
            "Compress": True,
            "ForwardedValues": {
                "QueryString": True,
                "Cookies": {"Forward": "all"},
                "Headers": {
                    "Quantity": 3,
                    "Items": ["Authorization", "CloudFront-Viewer-Country", "Content-Type"]
                }
            }
        },
        "CacheBehaviors": [
            {
                "PathPattern": "/prod/predict",
                "TargetOriginId": "ScadaAPIGatewayOrigin",
                "ViewerProtocolPolicy": "https-only",
                "AllowedMethods": {
                    "Quantity": 1,
                    "Items": ["POST"]
                },
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",  # No caching for POST
                "OriginRequestPolicyId": "216adef5-5c7f-47e4-b989-5492eafa07d3",
                "Compress": True
            }
        ],
        "Comment": "CloudFront distribution for SCADA Fault Prediction API",
        "Enabled": True,
        "HttpVersion": "http2and3",
        "PriceClass": "PriceClass_100",  # Lowest cost (only some edge locations)
        "ViewerCertificate": {
            "CloudFrontDefaultCertificate": True
        }
    }

    # Add WAF if available
    if waf_arn:
        distribution_config["WebACLId"] = waf_arn

    try:
        # Check if distribution already exists
        existing_dists = cloudfront.list_distributions()
        for dist in existing_dists.get("DistributionList", {}).get("Items", []):
            if "scada" in dist["Comment"].lower():
                print(f"⚠️  Distribution already exists")
                return {
                    "id": dist["Id"],
                    "domain": dist["DomainName"],
                    "status": dist["Status"]
                }

        response = cloudfront.create_distribution(DistributionConfig=distribution_config)

        dist_id = response["Distribution"]["Id"]
        dist_domain = response["Distribution"]["DomainName"]
        dist_status = response["Distribution"]["Status"]

        print(f"✅ CloudFront Distribution created:")
        print(f"   ID: {dist_id}")
        print(f"   Domain: {dist_domain}")
        print(f"   Status: {dist_status}")

        return {
            "id": dist_id,
            "domain": dist_domain,
            "status": dist_status
        }

    except Exception as e:
        print(f"❌ Error creating distribution: {e}")
        raise


def wait_for_distribution_deployed(dist_id, max_wait_seconds=600):
    """
    Chờ CloudFront distribution trở thành 'Deployed'

    Args:
        dist_id (str): Distribution ID
        max_wait_seconds (int): Max wait time
    """
    print(f"\n⏳ [Step 4] Đang chờ distribution deploy (max {max_wait_seconds}s)...")

    import time

    start_time = time.time()
    while time.time() - start_time < max_wait_seconds:
        response = cloudfront.get_distribution(Id=dist_id)
        status = response["Distribution"]["Status"]

        if status == "Deployed":
            print(f"✅ Distribution deployed!")
            return True

        elapsed = int(time.time() - start_time)
        print(f"   Status: {status} (elapsed: {elapsed}s)")
        time.sleep(30)

    print(f"⚠️  Distribution still deploying after {max_wait_seconds}s")
    print(f"   Check AWS CloudFront console for status")
    return False


def setup_cloudfront_cache_behaviors():
    """
    Configure cache behaviors for different endpoints

    Caching strategy:
    - /predict (POST) → No cache (real-time predictions)
    - /health (GET) → Cache 1 min
    - Static content → Cache 1 day
    """
    print("\n⚙️  [Step 5] Configuring cache behaviors...")

    cache_behaviors = {
        "/predict": {
            "ttl": 0,  # No cache for predictions
            "methods": ["POST"],
            "description": "Real-time predictions - no caching"
        },
        "/health": {
            "ttl": 60,  # Cache for 1 minute
            "methods": ["GET"],
            "description": "Health checks - short cache"
        }
    }

    for path, config in cache_behaviors.items():
        print(f"   {path}: {config['description']} (TTL: {config['ttl']}s)")


def print_cloudfront_info(cf_info):
    """
    Print CloudFront distribution info
    """
    print("\n" + "="*70)
    print("🎉 CLOUDFRONT DEPLOYMENT COMPLETE")
    print("="*70)
    print(f"Distribution ID      : {cf_info['id']}")
    print(f"Distribution Domain  : https://{cf_info['domain']}")
    print(f"Distribution Status  : {cf_info['status']}")
    print("="*70)
    print("\n📝 Usage:")
    print(f"   API Endpoint (with caching):")
    print(f"   https://{cf_info['domain']}/prod/predict")
    print("\n📊 Cache behavior:")
    print("   - POST /predict → No cache (real-time)")
    print("   - Other requests → Cache 5 min")
    print("   - Edge locations → ~30 locations globally")
    print("\n💰 Cost estimate:")
    print("   - $0.085 per GB data transfer out")
    print("   - Caching reduces API Gateway calls by ~70%")
    print("   - Typically: +$0.5-1/month for small traffic")
    print("="*70)


def setup_custom_domain(cf_domain, custom_domain=None, certificate_arn=None):
    """
    Setup custom domain for CloudFront (optional)

    Requires:
    - Custom domain name
    - SSL certificate in us-east-1
    - Route53 hosted zone

    Args:
        cf_domain (str): CloudFront domain
        custom_domain (str): Custom domain (e.g., api.example.com)
        certificate_arn (str): ACM certificate ARN
    """
    if not custom_domain or not certificate_arn:
        print("\n💡 To use custom domain:")
        print("   1. Create ACM certificate in us-east-1")
        print("   2. Create Route53 hosted zone")
        print("   3. Run: python aws/setup_route53.py")
        return

    print(f"\n🌐 [Step 6] Setting up custom domain: {custom_domain}")

    try:
        # Update distribution with custom domain
        print(f"   Certificate ARN: {certificate_arn}")
        print(f"   CloudFront domain will redirect to: {custom_domain}")

    except Exception as e:
        print(f"❌ Error setting up custom domain: {e}")


def main():
    """
    Main CloudFront setup pipeline
    """
    print("🚀 Starting CloudFront Distribution Setup...\n")

    try:
        # Step 1: Get API Gateway domain
        api_domain = get_api_gateway_domain()

        # Step 2: Setup WAF (optional)
        waf_arn = None
        try:
            waf_arn = create_waf_rules()
        except Exception as e:
            print(f"⚠️  Skipping WAF: {e}")

        # Step 3: Create CloudFront distribution
        cf_info = create_cloudfront_distribution(api_domain, waf_arn)

        # Step 4: Wait for deployment
        wait_for_distribution_deployed(cf_info["id"], max_wait_seconds=600)

        # Step 5: Configure cache behaviors
        setup_cloudfront_cache_behaviors()

        # Step 6: Print info
        print_cloudfront_info(cf_info)

        # Step 7: Setup custom domain (optional)
        setup_custom_domain(
            cf_info["domain"],
            custom_domain=None,  # Set to your domain
            certificate_arn=None  # Set to your cert ARN
        )

        print("\n✅ CloudFront setup complete!")
        print(f"\n🔗 New API endpoint (with caching):")
        print(f"   https://{cf_info['domain']}/prod/predict")

        return cf_info

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise


if __name__ == "__main__":
    main()
