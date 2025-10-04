# Google Cloud Platform Tutorial

## Overview

Google Cloud Platform (GCP) is a comprehensive suite of cloud computing services offered by Google. This tutorial covers the essential concepts, services, and best practices for using GCP effectively.

## What is Google Cloud Platform?

### Core Concepts
- **Cloud Computing**: On-demand delivery of computing resources over the internet
- **Infrastructure as a Service (IaaS)**: Virtual machines, storage, and networking
- **Platform as a Service (PaaS)**: Application development and deployment platforms
- **Software as a Service (SaaS)**: Ready-to-use applications

### Key Benefits
- **Scalability**: Automatically scale resources based on demand
- **Cost-Effective**: Pay only for what you use
- **Global Infrastructure**: Data centers worldwide for low latency
- **Security**: Enterprise-grade security and compliance
- **Innovation**: Access to cutting-edge AI and ML services

## Core GCP Services

### 1. Compute Services

#### Google Compute Engine (GCE)
- **Purpose**: Virtual machines in the cloud
- **Use Cases**: Web servers, databases, batch processing
- **Features**: 
  - Custom machine types
  - Preemptible instances
  - Live migration
  - Automatic scaling

```bash
# Create a VM instance
gcloud compute instances create my-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud
```

#### Google Kubernetes Engine (GKE)
- **Purpose**: Managed Kubernetes service
- **Use Cases**: Container orchestration, microservices
- **Features**:
  - Auto-scaling
  - Auto-repair
  - Multi-cluster management
  - Istio service mesh

```yaml
# GKE cluster configuration
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  type: LoadBalancer
```

#### Google App Engine
- **Purpose**: Serverless application platform
- **Use Cases**: Web applications, APIs, mobile backends
- **Features**:
  - Automatic scaling
  - Built-in security
  - Multiple language support
  - Integrated services

```python
# App Engine Python application
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
```

### 2. Storage Services

#### Google Cloud Storage (GCS)
- **Purpose**: Object storage service
- **Use Cases**: Data backup, content delivery, data lakes
- **Storage Classes**:
  - Standard: Frequently accessed data
  - Nearline: Monthly access
  - Coldline: Quarterly access
  - Archive: Annual access

```python
# Upload file to GCS
from google.cloud import storage

def upload_file(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}")
```

#### Cloud SQL
- **Purpose**: Managed relational database service
- **Supported Databases**: MySQL, PostgreSQL, SQL Server
- **Features**:
  - Automated backups
  - High availability
  - Automatic failover
  - Read replicas

```python
# Connect to Cloud SQL
import sqlalchemy

def create_connection():
    connection_string = (
        "mysql+pymysql://user:password@/database"
        "?unix_socket=/cloudsql/project:region:instance"
    )
    engine = sqlalchemy.create_engine(connection_string)
    return engine
```

#### Cloud Firestore
- **Purpose**: NoSQL document database
- **Use Cases**: Real-time applications, mobile apps
- **Features**:
  - Real-time updates
  - Offline support
  - Automatic scaling
  - ACID transactions

```python
# Firestore operations
from google.cloud import firestore

def add_document():
    db = firestore.Client()
    doc_ref = db.collection('users').document('alovelace')
    doc_ref.set({
        'first': 'Ada',
        'last': 'Lovelace',
        'born': 1815
    })
```

### 3. Networking Services

#### Virtual Private Cloud (VPC)
- **Purpose**: Isolated network environment
- **Components**:
  - Subnets
  - Firewall rules
  - Routes
  - VPN connections

```bash
# Create VPC network
gcloud compute networks create my-vpc \
    --subnet-mode=custom

# Create subnet
gcloud compute networks subnets create my-subnet \
    --network=my-vpc \
    --range=10.0.0.0/24 \
    --region=us-central1
```

#### Cloud Load Balancing
- **Purpose**: Distribute traffic across instances
- **Types**:
  - HTTP(S) Load Balancing
  - TCP/UDP Load Balancing
  - Internal Load Balancing
  - SSL Proxy Load Balancing

```yaml
# Load balancer configuration
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8080
  selector:
    app: my-app
```

### 4. AI and Machine Learning Services

#### Vertex AI
- **Purpose**: Unified ML platform
- **Features**:
  - AutoML
  - Custom training
  - Model deployment
  - MLOps pipelines

```python
# Train model with Vertex AI
from google.cloud import aiplatform

def train_model():
    aiplatform.init(project="my-project", location="us-central1")
    
    job = aiplatform.CustomTrainingJob(
        display_name="my-training-job",
        script_path="train.py",
        container_uri="gcr.io/my-project/trainer:latest"
    )
    
    job.run(
        args=["--epochs", "10"],
        replica_count=1,
        machine_type="n1-standard-4"
    )
```

#### Cloud Vision API
- **Purpose**: Image analysis and recognition
- **Features**:
  - Object detection
  - Text extraction
  - Face detection
  - Label detection

```python
# Analyze image with Vision API
from google.cloud import vision

def analyze_image(image_path):
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.label_detection(image=image)
    
    labels = response.label_annotations
    for label in labels:
        print(f"Label: {label.description}, Score: {label.score}")
```

#### Cloud Natural Language API
- **Purpose**: Text analysis and understanding
- **Features**:
  - Sentiment analysis
  - Entity recognition
  - Syntax analysis
  - Content classification

```python
# Analyze text with Natural Language API
from google.cloud import language_v1

def analyze_sentiment(text):
    client = language_v1.LanguageServiceClient()
    
    document = language_v1.Document(
        content=text,
        type_=language_v1.Document.Type.PLAIN_TEXT
    )
    
    response = client.analyze_sentiment(
        request={'document': document}
    )
    
    sentiment = response.document_sentiment
    print(f"Sentiment: {sentiment.score}, Magnitude: {sentiment.magnitude}")
```

## Getting Started with GCP

### 1. Account Setup
1. **Create Google Cloud Account**
   - Visit [cloud.google.com](https://cloud.google.com)
   - Sign up with Google account
   - Provide billing information

2. **Create Project**
   ```bash
   gcloud projects create my-gcp-project \
       --name="My GCP Project"
   ```

3. **Enable Billing**
   - Link billing account to project
   - Set up budget alerts
   - Monitor usage

### 2. Install Google Cloud SDK
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Set default project
gcloud config set project my-gcp-project
```

### 3. Authentication
```bash
# Authenticate with service account
gcloud auth activate-service-account \
    --key-file=path/to/service-account-key.json

# Set application default credentials
gcloud auth application-default login
```

## Best Practices

### 1. Security
- **Identity and Access Management (IAM)**
  - Principle of least privilege
  - Regular access reviews
  - Service account management

```bash
# Grant IAM role
gcloud projects add-iam-policy-binding my-project \
    --member="user:user@example.com" \
    --role="roles/storage.objectViewer"
```

- **Network Security**
  - VPC firewall rules
  - Private Google Access
  - Cloud NAT for outbound traffic

### 2. Cost Optimization
- **Resource Management**
  - Use preemptible instances
  - Implement auto-scaling
  - Regular resource cleanup

```bash
# List unused resources
gcloud compute instances list --filter="status:TERMINATED"
gcloud compute disks list --filter="status:UNATTACHED"
```

- **Monitoring and Alerting**
  - Set up billing alerts
  - Use Cloud Monitoring
  - Implement cost allocation

### 3. Performance
- **Caching**
  - Use Cloud CDN
  - Implement application-level caching
  - Optimize database queries

- **Scaling**
  - Horizontal scaling with load balancers
  - Vertical scaling for compute-intensive tasks
  - Auto-scaling based on metrics

### 4. Monitoring and Logging
```python
# Cloud Logging
from google.cloud import logging

def setup_logging():
    client = logging.Client()
    client.setup_logging()
    
    import logging
    logging.info("Application started")
```

```python
# Cloud Monitoring
from google.cloud import monitoring_v3

def create_metric():
    client = monitoring_v3.MetricServiceClient()
    
    project_name = f"projects/my-project"
    
    descriptor = monitoring_v3.MetricDescriptor(
        type="custom.googleapis.com/my_metric",
        metric_kind=monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
        value_type=monitoring_v3.MetricDescriptor.ValueType.DOUBLE,
        description="My custom metric"
    )
    
    descriptor = client.create_metric_descriptor(
        name=project_name, descriptor=descriptor
    )
```

## Common Use Cases

### 1. Web Application Deployment
```yaml
# app.yaml for App Engine
runtime: python39

handlers:
- url: /.*
  script: auto

env_variables:
  DATABASE_URL: "mysql://user:pass@/database"
```

### 2. Data Pipeline
```python
# Cloud Functions for data processing
import functions_framework
from google.cloud import storage, bigquery

@functions_framework.cloud_event
def process_data(cloud_event):
    # Download file from Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket("my-bucket")
    blob = bucket.blob("data.csv")
    
    # Process data
    data = blob.download_as_text()
    processed_data = transform_data(data)
    
    # Load to BigQuery
    bq_client = bigquery.Client()
    table = bq_client.get_table("my-project.dataset.table")
    
    errors = bq_client.insert_rows_json(table, processed_data)
    if errors:
        print(f"Errors: {errors}")
```

### 3. Machine Learning Pipeline
```python
# ML pipeline with Vertex AI
from google.cloud import aiplatform

def create_ml_pipeline():
    pipeline = aiplatform.PipelineJob(
        display_name="my-ml-pipeline",
        template_path="pipeline.json",
        parameter_values={
            "project": "my-project",
            "region": "us-central1"
        }
    )
    
    pipeline.run()
```

## Troubleshooting

### Common Issues
1. **Authentication Errors**
   - Check service account permissions
   - Verify API enablement
   - Confirm project ID

2. **Quota Exceeded**
   - Request quota increases
   - Use different regions
   - Optimize resource usage

3. **Network Connectivity**
   - Check firewall rules
   - Verify VPC configuration
   - Test DNS resolution

### Debugging Tools
```bash
# Check project configuration
gcloud config list

# View logs
gcloud logging read "resource.type=gce_instance"

# Monitor resources
gcloud monitoring metrics list
```

## Conclusion

Google Cloud Platform provides a comprehensive set of services for building, deploying, and managing applications in the cloud. By understanding the core services and following best practices, you can leverage GCP to build scalable, secure, and cost-effective solutions.

Key takeaways:
- **Start with core services** like Compute Engine and Cloud Storage
- **Implement proper security** with IAM and VPC
- **Monitor costs and performance** regularly
- **Use managed services** when possible to reduce operational overhead
- **Follow GCP best practices** for optimal results
