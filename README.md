# Insurance Document Claim Analyzer

A proof of concept that reads an insurance claim PDF from Amazon S3, extracts
selected claim details, and uses an Amazon Bedrock foundation model to generate
a response.

## What the application currently does

1. Amazon S3 sends an object-created event to Amazon EventBridge for objects
   under the configured document prefix (`resources/documents/` by default).
2. EventBridge starts the AWS Step Functions state machine with the S3 bucket
   and object key.
3. The document-processing Lambda downloads the PDF, extracts its tables, and
   returns selected claim and policyholder details along with whether the PDF
   contains embedded image objects.
4. The state machine ends successfully when `contains_images` is `true`.
   Otherwise, it waits 30 seconds and invokes the summarizer Lambda.
5. The summarizer builds a prompt from the extracted policy details and calls
   the configured Amazon Bedrock model.

The current implementation is a prototype. It does not yet retrieve policy
documents for RAG, validate model output, or save generated summaries to S3.
Also, Step Functions wraps the summarizer input under `input`, while the
summarizer currently reads `policy_details` at the top level. That payload
shape needs to be aligned for the summarizer to receive the extracted details.

## Repository structure

```text
.
├── infra/
│   └── terraform/       AWS resources: S3 notifications, EventBridge,
│                        Step Functions, Lambda, IAM, and CloudWatch logs
├── layers/
│   └── requirements.txt Python dependencies packaged in the PDF Lambda layer
├── resources/           Sample claim PDF and project/design documents
├── src/
│   ├── document_handler.py   PDF download and claim-data extraction Lambda
│   ├── summarizer_handler.py Bedrock prompt and summarization Lambda
│   ├── resources/            Prompt template manager
│   └── utils/                PDF, S3, AWS session, and Bedrock helpers
├── Dockerfile           Container recipe for building the PDF dependency layer
└── create_layer.sh      Shell helper for building the PDF dependency layer
```

## Example use case

An insurance claims team uploads a claim-form PDF into the configured S3
document prefix. The workflow extracts claim number, dates, policyholder
details, and vehicle or incident details. For PDFs without detected image
objects, it passes the extracted information through a prompt to the configured
Bedrock model.

## Configuration

Terraform variables are defined in `infra/terraform/variables.tf`; example
values are in `infra/terraform/values.tfvars`. Review and replace environment-
specific values, especially `s3_bucket_name`, before deploying. Do not put AWS
credentials or other secrets in the Terraform variables file.

Important settings include:

| Setting | Purpose |
| --- | --- |
| `aws_region` | AWS region for the infrastructure (default: `us-east-1`) |
| `s3_bucket_name` | Existing S3 bucket used for input documents |
| `s3_documents_prefix` | Key prefix that starts the workflow (default: `resources/documents/`) |
| `bedrock_model_id` | Foundation model invoked by the summarizer |
| `lambda_execution_role_name` | IAM role name used by the Lambda functions |

The Lambda layer archive is expected at `layers/pdf_layer.zip` when Terraform
is run. The configured S3 bucket must exist and the AWS identity used by
Terraform must be authorized to create and update the listed resources.

## Deploying the infrastructure

After configuring Terraform values and preparing `layers/pdf_layer.zip`, run:

```sh
cd infra/terraform
terraform init
terraform validate
terraform plan -var-file=values.tfvars
terraform apply -var-file=values.tfvars
```

Review the plan before applying it. Terraform provisions AWS resources and may
incur charges.

## Uploading a document

Upload a PDF to the bucket and prefix configured for the deployment. For
example, with AWS CLI credentials and permissions configured:

```sh
aws s3 cp resources/insurance_claim_sample.pdf \
  s3://YOUR_BUCKET/resources/documents/insurance_claim_sample.pdf
```

Replace `YOUR_BUCKET` with the deployed bucket name. The S3 object-created
event starts the workflow; no separate application API is currently provided.

## Runtime and dependencies

- Lambda runtime: Python 3.12
- Infrastructure: Terraform (version 1.5 or later)
- PDF dependencies: listed in `layers/requirements.txt` and packaged as the
  `pdf_layer.zip` Lambda layer
- AI inference: Amazon Bedrock, using the configured model ID
