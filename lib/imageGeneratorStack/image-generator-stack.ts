import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigw from 'aws-cdk-lib/aws-apigateway';

export class ImageGenerationStack extends Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // ImageGenerator Lambda
        const bedrockFullAccess = new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: ["bedrock:*"],
            resources: ["*"],
        }); 

        const generateImageLambda = new lambda.Function(this, "Query", {
            runtime: lambda.Runtime.PYTHON_3_8,
            handler: "generateImageLambda.handler",
            code: lambda.Code.fromAsset("./lib/imageGeneratorStack"),
            timeout: cdk.Duration.minutes(3),
            initialPolicy: [bedrockFullAccess]
        });

        // API Gateway for the Lambda function
        const generateImageApi = new apigw.RestApi(this, "GenerateImageApi", {
            restApiName: "GenerateImageApi",
            description: "Image Generator API that generates images with Amazon Bedrock",
            defaultCorsPreflightOptions: {
                allowOrigins: apigw.Cors.ALL_ORIGINS,
                allowMethods: apigw.Cors.ALL_METHODS,
                allowHeaders: apigw.Cors.DEFAULT_HEADERS
            },
            endpointTypes: [apigw.EndpointType.REGIONAL]
        });

        // Define API responses
        const integrationResponse = {
            proxy: false,
            integrationResponses: [{
                statusCode: "200",
                responseParameters: {
                  "method.response.header.Access-Control-Allow-Origin": "'*'",
                },
                responseTemplates: {
                  "application/json": ""
                }}
            ]
        };
      
        const methodResponse = {
            methodResponses: [{
                statusCode: "200",
                responseParameters: {
                  "method.response.header.Access-Control-Allow-Origin": true, 
                },
                responseModels: {
                  "application/json": apigw.Model.EMPTY_MODEL,
                }}
            ],
        };

        const generateImageLambdaIntegration = new apigw.LambdaIntegration(
            generateImageLambda,
            integrationResponse
        );
          
        generateImageApi.root.addResource("default").addMethod(
            "POST",
            generateImageLambdaIntegration, 
            methodResponse
        );

        new cdk.CfnOutput(this, "GenerateImageApi_ApiGatewayUrl", {
            value: `${generateImageApi.url}`,
            description: "Image Generator API - API Gateway Endpoint",
            exportName: "GenerateImageApiGateway"
        });
    }
};