module "emcq_eks_v2" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.37.2"

  cluster_name    = "emcq-v2"
  cluster_version = "1.33"

  cluster_endpoint_public_access           = true
  cluster_endpoint_private_access          = true
  enable_cluster_creator_admin_permissions = true

  vpc_id     = module.vpc_emcq_v2.vpc_id
  subnet_ids = module.vpc_emcq_v2.private_subnets

  self_managed_node_groups = {
    emcq_nodes = {
      ami_type      = "AL2023_x86_64_STANDARD"
      instance_type = "t3.medium"


      min_size     = 1
      max_size     = 2
      desired_size = 1
    }
  }


}

resource "kubernetes_service_account" "aws_load_balancer_controller" {
  metadata {
    name      = "aws-load-balancer-controller"
    namespace = "kube-system"
    annotations = {
      "eks.amazonaws.com/role-arn" = aws_iam_role.aws_load_balancer_controller.arn
    }
  }

}

resource "helm_release" "aws_load_balancer_controller" {

  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  namespace  = "kube-system"
  version    = "1.13.0"

  set = [{
    name  = "serviceAccount.create"
    value = "false"
    },
    {
      name  = "clusterName"
      value = module.emcq_eks_v2.cluster_name
    },
    {
      name  = "serviceAccount.name"
      value = kubernetes_service_account.aws_load_balancer_controller.metadata[0].name
    }
  ]

}

# resource "kubernetes_namespace" "argocd" {
#   metadata {
#     name = "argocd"
#   }
# }

# resource "helm_release" "argocd" {
#   name = "argo-cd"
#   repository = "https://argoproj.github.io/argo-helm"
#   chart = "argo-cd"
#   namespace = kubernetes_namespace.argocd.metadata[0].name
#   version = "6.7.14"

#   values = [
#     file("values/argocd/values.yaml")
#   ]

# }
