provider "aws" {
  region = "us-east-1"

}

provider "kubernetes" {
  host                   = module.emcq_eks_v2.cluster_endpoint
  cluster_ca_certificate = base64decode(module.emcq_eks_v2.cluster_certificate_authority_data)
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", module.emcq_eks_v2.cluster_name]
    command     = "aws"
  }
}

provider "helm" {
  kubernetes = {
    host                   = module.emcq_eks_v2.cluster_endpoint
    cluster_ca_certificate = base64decode(module.emcq_eks_v2.cluster_certificate_authority_data)
    exec = {
      api_version = "client.authentication.k8s.io/v1beta1"
      args        = ["eks", "get-token", "--cluster-name", module.emcq_eks_v2.cluster_name]
      command     = "aws"
    }
  }
}
