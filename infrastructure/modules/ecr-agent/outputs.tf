output "repository_url" {
  description = "The URL of the repository (in the form aws_account_id.dkr.ecr.region.amazonaws.com/repositoryName)"
  value       = aws_ecr_repository.agent_repo.repository_url
}

output "repository_name" {
  description = "The name of the repository"
  value       = aws_ecr_repository.agent_repo.name
}

output "repository_arn" {
  description = "Full ARN of the repository"
  value       = aws_ecr_repository.agent_repo.arn
}

output "registry_id" {
  description = "The registry ID where the repository was created"
  value       = aws_ecr_repository.agent_repo.registry_id
}

output "image_uri_latest" {
  description = "The URI of the image with latest tag"
  value       = "${aws_ecr_repository.agent_repo.repository_url}:latest"
}
