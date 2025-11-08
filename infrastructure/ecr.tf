resource "aws_ecr_repository" "book_catalog" {
  name                 = "book_catalog"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}