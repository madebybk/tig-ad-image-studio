import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as fs from 'fs';
import * as path from 'path';

interface WebAppStackProps extends cdk.StackProps {
  api_url: string;
  s3_bucket_name: string;
}

export class WebAppStack extends Stack {
  constructor(scope: Construct, id: string, props: WebAppStackProps) {
    super(scope, id, props);

    const api_url = props.api_url;
    const s3_bucket_name = props.s3_bucket_name;

    // IAM Role to access EC2
    const instanceRole = new iam.Role(this, 'InstanceRole', {
      assumedBy: new iam.ServicePrincipal('ec2.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'),
      ],
    });

    // Network setting for EC2
    const defaultVpc = ec2.Vpc.fromLookup(this, 'VPC', {
      isDefault: true,
    });

    const webAppSecurityGroup = new ec2.SecurityGroup(this, 'webAppSecurityGroup', {
      vpc: defaultVpc,
    });
    webAppSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(80),
      'httpIpv4',
    );
    webAppSecurityGroup.addIngressRule(
      ec2.Peer.anyIpv4(),
      ec2.Port.tcp(22),
      'sshIpv4',
    );

    // set AMI
    const machineImage = ec2.MachineImage.fromSsmParameter(
      '/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id'
    );
    
    // set User Data
    const userData = ec2.UserData.forLinux();
    const userDataScript = fs.readFileSync(path.join(__dirname, 'userdata.sh'), 'utf8');
    userData.addCommands(userDataScript);
    userData.addCommands(`
      sudo sed -i '/Environment=/d' /etc/systemd/system/streamlit.service
      sudo sed -i '/ExecStart=/i Environment=API_URL=${api_url}' /etc/systemd/system/streamlit.service
      sudo sed -i '/ExecStart=/i Environment=S3_BUCKET_NAME=${s3_bucket_name}' /etc/systemd/system/streamlit.service
      sudo systemctl daemon-reload
      sudo systemctl restart streamlit
    `);

    // EC2 instance
    const webAppInstance = new ec2.Instance(this, 'webAppInstance', {
      instanceType: new ec2.InstanceType('m5.large'),
      machineImage: machineImage,
      vpc: defaultVpc,
      securityGroup: webAppSecurityGroup,
      role: instanceRole,
      userData: userData,
    });

    new cdk.CfnOutput(this, 'webAppUrl', {
      value: `http://${webAppInstance.instancePublicIp}/`,
      description: 'The URL of the web application of TIG Ad Image Studio',
      exportName: 'webAppUrl',
    });
  }
}