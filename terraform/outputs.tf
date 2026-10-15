output "public_ip" {
  value = aws_instance.app.public_ip
}
output "web_url" {
  value = "http://${aws_instance.app.public_ip}"
}
