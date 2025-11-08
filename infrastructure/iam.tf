data "http" "ingress_controller_policy" {
  url = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.13.3/docs/install/iam_policy.json"
}

resource "aws_iam_policy" "ingress_controller_policy" {
  name        = "AWSLoadBalancerControllerIAMPolicy"
  description = "Politica para ingress controller do EKS"
  policy      = data.http.ingress_controller_policy.response_body
}

resource "aws_iam_role" "aws_load_balancer_controller" {
  name = "aws-load-balancer-controller"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = module.emcq_eks_v2.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${replace(module.emcq_eks_v2.cluster_oidc_issuer_url, "https://", "")}:sub" = "system:serviceaccount:kube-system:aws-load-balancer-controller"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "aws_load_balancer_controller_attach" {
  policy_arn = aws_iam_policy.ingress_controller_policy.arn
  role       = aws_iam_role.aws_load_balancer_controller.name
}