# Temporary simple deployment without Load Balancer
# This creates a publicly accessible ECS service for immediate testing

# Update security group to allow port 8000 from anywhere
resource "aws_security_group" "simple_app" {
  name_prefix = "${var.app_name}-simple-"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Application port"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.app_name}-simple-sg"
  }
}

# Simple ECS Service without Load Balancer
resource "aws_ecs_service" "simple_app" {
  name            = "${var.app_name}-simple-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1
  
  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.simple_app.id]
    assign_public_ip = true
  }
  
  tags = {
    Name = "${var.app_name}-simple-service"
  }
}