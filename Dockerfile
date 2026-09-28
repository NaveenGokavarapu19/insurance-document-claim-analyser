# Use --platform=linux/amd64 if your Lambda is x86_64 (default in AWS)
# Change to --platform=linux/arm64 ONLY if your Lambda is set to arm64
FROM --platform=linux/amd64 public.ecr.aws/sam/build-python3.12:latest

WORKDIR /app
COPY requirements.txt .

# Upgrade pip and install dependencies into /opt/python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    --prefer-binary \
    -r requirements.txt -t /opt/python/

# Zip the /opt/python directory into the mounted /app directory
CMD ["sh", "-c", "cd /opt && zip -r9 /app/pdf_layer.zip python"]