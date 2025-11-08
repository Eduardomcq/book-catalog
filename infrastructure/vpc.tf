data "aws_availability_zones" "azs" {
  state = "available"
}

module "vpc_emcq_v2" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"

  name = "emcq-vpc-v2"
  cidr = "32.0.0.0/16"

  azs             = data.aws_availability_zones.azs.names
  private_subnets = ["32.0.32.0/19", "32.0.96.0/19", "32.0.160.0/19"]
  public_subnets  = ["32.0.0.0/19", "32.0.64.0/19", "32.0.128.0/19"]

  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false


}