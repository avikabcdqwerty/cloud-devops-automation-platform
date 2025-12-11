# Cloud DevOps Automation Platform

A modular platform to provision cloud resources using Infrastructure as Code (IaC), automate CI/CD pipelines, and implement monitoring and alerting for cloud resources. Includes a sample FastAPI CRUD API for managing products.

---

## Features

- **Infrastructure as Code**: Provision AWS resources (VPC, PostgreSQL, ECS Fargate, security groups) using Terraform.
- **CI/CD Automation**: GitHub Actions pipeline for linting, security scanning, testing, Docker build/push, Terraform validation, and deployment.
- **Monitoring & Alerting**: Cloud-native monitoring with AWS CloudWatch alarms for API and database health, performance, and security anomalies.
- **Product CRUD API**: FastAPI application with RESTful endpoints for product management, backed by PostgreSQL.
- **Security & Compliance**: Automated validation, access controls, audit logging, and documentation for all components.

---

## Architecture

- **API**: Python FastAPI app (`src/api/`) exposes CRUD endpoints for products.
- **Database**: PostgreSQL provisioned via Terraform, accessed via SQLAlchemy ORM.
- **IaC**: Terraform templates (`iac/terraform/`) for cloud resource provisioning.
- **CI/CD**: GitHub Actions workflow (`.github/workflows/ci-cd-pipeline.yml`) automates build, test, deploy, and audit logging.
- **Monitoring**: CloudWatch alarms (`monitoring/cloudwatch-alarms.yml`) for real-time metrics and alerts.
- **Containerization**: Dockerfile for API app; deployable to ECS Fargate.

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/)
- [Terraform](https://www.terraform.io/)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Python 3.11+](https://www.python.org/)
- [Git](https://git-scm.com/)

### 1. Clone the Repository

```sh
git clone https://github.com/your-org/cloud-devops-automation-platform.git
cd cloud-devops-automation-platform
```

### 2. Set Up Environment Variables

Create a `.env` file or set environment variables for database credentials:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=cloud_devops_db
```

### 3. Install Python Dependencies

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize Database

```sh
python -c "from src.api.database import init_db; init_db()"
```

### 5. Run Locally with Docker

```sh
docker build -t cloud-devops-api .
docker run --env-file .env -p 8000:8000 cloud-devops-api
```

Or with Uvicorn:

```sh
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### 6. API Usage

- **Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: `GET /health`
- **Products CRUD**:
  - `POST /products/` - Create product
  - `GET /products/` - List products
  - `GET /products/{id}` - Get product by ID
  - `PUT /products/{id}` - Update product
  - `DELETE /products/{id}` - Delete product

### 7. Testing

```sh
pytest --cov=src/api
```

### 8. Infrastructure Provisioning

```sh
cd iac/terraform
terraform init
terraform plan
terraform apply
```

### 9. CI/CD Pipeline

- All pushes and PRs trigger lint, security scan, tests, and build.
- Production deploys require manual approval.
- See `.github/workflows/ci-cd-pipeline.yml` for details.

### 10. Monitoring & Alerting

- CloudWatch alarms are defined in `monitoring/cloudwatch-alarms.yml`.
- Alerts are sent to SNS topics for notification.

---

## Directory Structure

```
src/api/              # FastAPI app, models, schemas, CRUD, DB
tests/                # Pytest unit/integration tests
iac/terraform/        # Terraform IaC templates
monitoring/           # Monitoring & alerting configs
.github/workflows/    # CI/CD pipeline
Dockerfile            # Containerization
requirements.txt      # Python dependencies
SECURITY.md           # Security & compliance guidelines
README.md             # Project documentation
```

---

## Security & Compliance

- See [SECURITY.md](SECURITY.md) for full guidelines.
- All secrets managed via environment variables or AWS Secrets Manager.
- All changes, deployments, and alerts are logged for audit.

---

## Contributing

1. Fork the repo and create a feature branch.
2. Run pre-commit hooks and tests before PR.
3. Submit PR for review.

---

## License

[MIT License](LICENSE)

---

## Maintainers & Contact

- Security: [security@yourdomain.com]
- Issues: [GitHub Issues](https://github.com/your-org/cloud-devops-automation-platform/issues)

---

_Last updated: 2024-06-01_