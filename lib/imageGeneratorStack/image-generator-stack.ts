import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as targets from 'aws-cdk-lib/aws-elasticloadbalancingv2-targets';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class ImageGenerationStack extends Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Create S3 buckets
        const randomstr = Math.random().toString(36).substring(2,8);
        const imagesBucket = new s3.Bucket(this, 'ImagesBucket', {
            bucketName: `titan-ad-studio-bucket-${randomstr}`,
            encryption: s3.BucketEncryption.S3_MANAGED,
            removalPolicy: cdk.RemovalPolicy.DESTROY
        });
    
        // ImageGenerator Lambda
        const bedrockFullAccess = new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: ["bedrock:*"],
            resources: ["*"],
        }); 

        // VPC for Application Load Balancer (ALB)
        const vpc = new ec2.Vpc(this, "ImageGenerationVPC", {
            maxAzs: 2
        });

        // Dockerized Lambda function
        const generateImageLambda = new lambda.DockerImageFunction(this, 'GenerateImageLambda', {
            code: lambda.DockerImageCode.fromImageAsset("./lib/imageGeneratorStack/lambda"),
            timeout: cdk.Duration.minutes(3),
            memorySize: 10240,
            architecture: lambda.Architecture.ARM_64,
            initialPolicy: [bedrockFullAccess],
            vpc: vpc
        });

        imagesBucket.grantReadWrite(generateImageLambda)

        const alb = new elbv2.ApplicationLoadBalancer(this, "GenerateImageALB", {
            vpc,
            internetFacing: true,
       });

        const listener = alb.addListener("GenerateImageListener", {
            port: 80
        });

        const targetGroup = listener.addTargets("GenerateImageLambdaTarget", {
            targets: [new targets.LambdaTarget(generateImageLambda)],
            healthCheck: {
                enabled: true,
                path: "/health",
                interval: cdk.Duration.seconds(60),
                healthyHttpCodes: "200"
            }
        });

        generateImageLambda.grantInvoke(new iam.ServicePrincipal("elasticloadbalancing.amazonaws.com"));

        new cdk.CfnOutput(this, "GenerateImageApiUrl", {
            value: `http://${alb.loadBalancerDnsName}`,
            description: "Image Generator API - API Gateway Endpoint",
            exportName: "GenerateImageApiUrl"
        });

        new cdk.CfnOutput(this, "ImagesBucketName", {
            value: imagesBucket.bucketName,
            description: "Name of the S3 bucket that contains all images",
            exportName: "ImagesBucketName"
        })
    }
};