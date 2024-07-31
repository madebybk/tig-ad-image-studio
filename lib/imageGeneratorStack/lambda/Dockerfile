FROM --platform=arm64 public.ecr.aws/lambda/python:3.8

# Install system dependencies
RUN yum install -y gcc zlib-devel libjpeg-devel

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy function code
COPY generate_image_lambda.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "generate_image_lambda.lambda_handler" ]