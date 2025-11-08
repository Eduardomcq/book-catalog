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

data "aws_eks_cluster" "emcq_v2" {
  name = module.emcq_eks_v2.cluster_name
}

data "aws_iam_openid_connect_provider" "emcq_v2" {
  arn = module.emcq_eks_v2.oidc_provider_arn
}


data "aws_iam_policy_document" "ebs_csi_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.emcq_v2.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${replace(data.aws_iam_openid_connect_provider.emcq_v2.url, "https://", "")}:sub"
      values   = ["system:serviceaccount:kube-system:ebs-csi-controller-sa"]
    }
  }
}

resource "aws_iam_role" "ebs_csi_driver" {
  name               = "AmazonEKS_EBS_CSI_DriverRole"
  assume_role_policy = data.aws_iam_policy_document.ebs_csi_assume_role.json
}


resource "aws_iam_role_policy_attachment" "ebs_csi_driver_attach" {
  role       = aws_iam_role.ebs_csi_driver.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}

resource "aws_eks_addon" "ebs_csi_driver" {
  cluster_name             = module.emcq_eks_v2.cluster_name
  addon_name               = "aws-ebs-csi-driver"
  service_account_role_arn = aws_iam_role.ebs_csi_driver.arn
  depends_on = [
    module.emcq_eks_v2,
    aws_iam_role_policy_attachment.ebs_csi_driver_attach
  ]
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

resource "kubernetes_manifest" "book_catalog_app_secret" {

  manifest = yamldecode(file("manifests/book_catalog_secret.yaml"))

}

resource "kubernetes_manifest" "book_catalog_app_volume" {

  manifest = yamldecode(file("manifests/book_catalog_volume.yaml"))

}

resource "kubernetes_manifest" "book_catalog_app_service" {

  manifest = yamldecode(file("manifests/book_catalog_app_service.yaml"))

}

resource "kubernetes_manifest" "book_catalog_app" {

  manifest = yamldecode(file("manifests/book_catalog_app.yaml"))
  depends_on = [ kubernetes_manifest.book_catalog_app_secret ]

}

resource "kubernetes_manifest" "book_catalog_app_db" {

  manifest = yamldecode(file("manifests/book_catalog_db_service.yaml"))

}

resource "kubernetes_manifest" "book_catalog_app_db_service" {

  manifest = yamldecode(file("manifests/book_catalog_db.yaml"))
  depends_on = [ kubernetes_manifest.book_catalog_app_secret ]

}

