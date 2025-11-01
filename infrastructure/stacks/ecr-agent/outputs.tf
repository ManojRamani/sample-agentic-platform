output "repository_url" {
  description = "The URL of the ECR repository"
  value       = module.ecr_agent.repository_url
}

output "repository_name" {
  description = "The name of the ECR repository"
  value       = module.ecr_agent.repository_name
}

output "image_uri_latest" {
  description = "The URI of the image with latest tag"
  value       = module.ecr_agent.image_uri_latest
}
