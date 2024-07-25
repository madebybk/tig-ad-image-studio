#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { WebAppStack } from '../lib/webAppStack/web-app-stack';

const STACK_PREFIX = "TIGAdImageStudio";
const DEFAULT_REGION = "us-west-2";

const app = new cdk.App();

new WebAppStack(app, `${STACK_PREFIX}-WebAppStack`, {
  env: {
    account: process.env.CDK_DEPLOY_ACCOUNT || process.env.CDK_DEFAULT_ACCOUNT,
    region: DEFAULT_REGION,
  },
})

app.synth();