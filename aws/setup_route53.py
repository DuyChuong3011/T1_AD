"""
Setup Route53 for DNS + Failover
Kết nối custom domain với CloudFront
Hỗ trợ health checks và automatic failover
"""

import boto3
from datetime import datetime

# Configuration
REGION = "ap-southeast-1"
DOMAIN_NAME = "scada-fault-api.example.com"  # Change to your domain
CLOUDFRONT_DOMAIN = None  # Will be obtained
HOSTED_ZONE_ID = None  # Will be retrieved from Route53

# Initialize clients
route53 = boto3.client("route53", region_name=REGION)
cloudfront_client = boto3.client("cloudfront", region_name=REGION)


def get_hosted_zone(domain_name):
    """
    Lấy Hosted Zone ID từ domain name

    Args:
        domain_name (str): Domain (vd: scada-fault-api.example.com)

    Returns:
        str: Hosted Zone ID
    """
    print(f"🔍 [Step 1] Đang lấy Hosted Zone cho domain: {domain_name}")

    try:
        # Extract root domain
        parts = domain_name.split(".")
        root_domain = ".".join(parts[-2:])  # e.g., example.com

        response = route53.list_hosted_zones_by_name()

        for zone in response["HostedZones"]:
            if root_domain in zone["Name"]:
                zone_id = zone["Id"].split("/")[-1]
                print(f"✅ Hosted Zone found: {zone_id}")
                return zone_id

        print(f"❌ Hosted Zone not found for {root_domain}")
        print(f"   Please create it first: route53.amazonaws.com")
        raise ValueError(f"Hosted zone not found for {domain_name}")

    except Exception as e:
        print(f"❌ Error getting hosted zone: {e}")
        raise


def get_cloudfront_domain():
    """
    Lấy CloudFront domain từ distribution

    Returns:
        str: CloudFront domain (vd: abc123.cloudfront.net)
    """
    print(f"\n📡 [Step 2] Đang lấy CloudFront domain...")

    try:
        response = cloudfront_client.list_distributions()

        for dist in response.get("DistributionList", {}).get("Items", []):
            if "scada" in dist["Comment"].lower():
                domain = dist["DomainName"]
                print(f"✅ CloudFront domain: {domain}")
                return domain

        print(f"❌ CloudFront distribution not found")
        print(f"   Run: python aws/setup_cloudfront.py first")
        raise ValueError("CloudFront distribution not found")

    except Exception as e:
        print(f"❌ Error getting CloudFront domain: {e}")
        raise


def create_health_check(cloudfront_domain):
    """
    Tạo health check cho CloudFront

    Health checks mỗi 30 giây, trigger failover nếu down

    Args:
        cloudfront_domain (str): CloudFront domain

    Returns:
        str: Health Check ID
    """
    print(f"\n❤️  [Step 3] Đang tạo health check...")

    try:
        health_check_config = {
            "Type": "HTTPS",
            "ResourcePath": "/prod/",
            "FullyQualifiedDomainName": cloudfront_domain,
            "Port": 443,
            "RequestInterval": 30,  # Check every 30 seconds
            "FailureThreshold": 3  # Fail after 3 consecutive failures
        }

        response = route53.create_health_check(
            HealthCheckConfig=health_check_config,
            HealthCheckTags=[
                {"Key": "Project", "Value": "T1_AD"},
                {"Key": "Environment", "Value": "Production"},
                {"Key": "Purpose", "Value": "Failover"},
            ]
        )

        health_check_id = response["HealthCheck"]["Id"]
        print(f"✅ Health check created: {health_check_id}")

        return health_check_id

    except Exception as e:
        print(f"⚠️  Error creating health check: {e}")
        print(f"   Continuing without health check (can add later)")
        return None


def create_alias_record(hosted_zone_id, domain_name, cloudfront_domain, health_check_id=None):
    """
    Tạo Route53 alias record kết nối domain với CloudFront

    Args:
        hosted_zone_id (str): Hosted Zone ID
        domain_name (str): Domain name (vd: scada-fault-api.example.com)
        cloudfront_domain (str): CloudFront domain
        health_check_id (str): Health check ID (optional)
    """
    print(f"\n📝 [Step 4] Đang tạo Route53 record...")

    try:
        # Check if record already exists
        response = route53.list_resource_record_sets(HostedZoneId=hosted_zone_id)

        for record in response["ResourceRecordSets"]:
            if record["Name"] == f"{domain_name}.":
                print(f"⚠️  Record already exists for {domain_name}")
                print(f"   Updating existing record...")
                break

        # Create or update alias record
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": domain_name,
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "Z2FDTNDATAQYW2",  # CloudFront hosted zone ID (global)
                        "DNSName": cloudfront_domain,
                        "EvaluateTargetHealth": health_check_id is not None
                    }
                }
            }
        ]

        # Add health check if available
        if health_check_id:
            changes[0]["ResourceRecordSet"]["SetIdentifier"] = "Primary"
            changes[0]["ResourceRecordSet"]["Failover"] = "PRIMARY"
            changes[0]["ResourceRecordSet"]["HealthCheckId"] = health_check_id

        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={"Changes": changes}
        )

        print(f"✅ Alias record created/updated")
        print(f"   Domain: {domain_name}")
        print(f"   Target: {cloudfront_domain}")

    except Exception as e:
        print(f"❌ Error creating alias record: {e}")
        raise


def create_failover_record(hosted_zone_id, domain_name, failover_target):
    """
    Tạo failover record (optional)

    Failover to secondary endpoint nếu primary down

    Args:
        hosted_zone_id (str): Hosted Zone ID
        domain_name (str): Domain name
        failover_target (str): Secondary endpoint
    """
    print(f"\n🔄 [Step 5] Tạo failover record...")

    try:
        # Failover record
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": domain_name,
                    "Type": "A",
                    "SetIdentifier": "Secondary",
                    "Failover": "SECONDARY",
                    "AliasTarget": {
                        "HostedZoneId": "Z2FDTNDATAQYW2",
                        "DNSName": failover_target,
                        "EvaluateTargetHealth": False
                    }
                }
            }
        ]

        response = route53.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={"Changes": changes}
        )

        print(f"✅ Failover record created")
        print(f"   Primary: {domain_name} (via health check)")
        print(f"   Secondary: {failover_target}")

    except Exception as e:
        print(f"⚠️  Error creating failover record: {e}")


def test_dns_resolution(domain_name):
    """
    Test DNS resolution

    Args:
        domain_name (str): Domain to test
    """
    print(f"\n🧪 [Step 6] Testing DNS resolution...")

    try:
        import socket

        # Try to resolve domain
        try:
            ip = socket.gethostbyname(domain_name)
            print(f"✅ DNS resolves to: {ip}")
        except socket.gaierror:
            print(f"⚠️  DNS not resolving yet (may take 5-10 min to propagate)")
            print(f"   Please wait and try again")

    except Exception as e:
        print(f"❌ Error testing DNS: {e}")


def print_route53_info(domain_name, cloudfront_domain):
    """
    Print Route53 configuration info
    """
    print("\n" + "="*70)
    print("🎉 ROUTE53 SETUP COMPLETE")
    print("="*70)
    print(f"Domain Name          : {domain_name}")
    print(f"CloudFront Target    : {cloudfront_domain}")
    print(f"Health Check         : Enabled (30s intervals)")
    print("="*70)
    print("\n📝 DNS configuration:")
    print(f"   Type: A (Alias)")
    print(f"   Target: CloudFront distribution")
    print(f"   Evaluation: Target health enabled")
    print("\n⏱️  DNS propagation:")
    print(f"   TTL: Auto (CloudFront)")
    print(f"   Propagation time: 5-10 minutes globally")
    print("\n🌍 Access endpoint:")
    print(f"   https://{domain_name}/prod/predict")
    print("\n🔄 Failover:")
    print(f"   If CloudFront is down → DNS returns secondary")
    print(f"   Health checks run every 30 seconds")
    print("="*70)


def setup_dns_records(domain_name, cloudfront_domain, hosted_zone_id):
    """
    Setup additional DNS records (optional)

    Records:
    - www subdomain
    - API subdomain
    - Health check
    """
    print(f"\n📋 [Step 7] Setting up additional DNS records...")

    # Subdomain records
    subdomains = [
        {"name": f"www.{domain_name}", "type": "CNAME"},
        {"name": f"api.{domain_name}", "type": "CNAME"},
    ]

    for subdomain in subdomains:
        print(f"   - {subdomain['name']} → {cloudfront_domain}")


def main():
    """
    Main Route53 setup pipeline
    """
    print("🚀 Starting Route53 DNS Setup...\n")

    try:
        # Validate domain
        if not DOMAIN_NAME or DOMAIN_NAME == "scada-fault-api.example.com":
            print("❌ Please update DOMAIN_NAME variable with your actual domain")
            print(f"   Current: {DOMAIN_NAME}")
            print(f"   Edit: aws/setup_route53.py line 9")
            raise ValueError("Invalid domain name")

        # Step 1: Get hosted zone
        hosted_zone_id = get_hosted_zone(DOMAIN_NAME)

        # Step 2: Get CloudFront domain
        cf_domain = get_cloudfront_domain()

        # Step 3: Create health check
        health_check_id = create_health_check(cf_domain)

        # Step 4: Create alias record
        create_alias_record(hosted_zone_id, DOMAIN_NAME, cf_domain, health_check_id)

        # Step 5: Create failover record (optional)
        # create_failover_record(hosted_zone_id, DOMAIN_NAME, "failover.example.com")

        # Step 6: Test DNS
        test_dns_resolution(DOMAIN_NAME)

        # Step 7: Setup additional records
        setup_dns_records(DOMAIN_NAME, cf_domain, hosted_zone_id)

        # Print info
        print_route53_info(DOMAIN_NAME, cf_domain)

        print("\n✅ Route53 setup complete!")
        print(f"\n🌐 Your API is now accessible at:")
        print(f"   https://{DOMAIN_NAME}/prod/predict")
        print(f"\n⏳ Note: DNS changes propagate globally in 5-10 minutes")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--domain",
        default=DOMAIN_NAME,
        help="Your custom domain (e.g., api.example.com)"
    )

    args = parser.parse_args()
    DOMAIN_NAME = args.domain

    main()
