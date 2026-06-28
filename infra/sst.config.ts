/// <reference path="./.sst/platform/config.d.ts" />

const stage = $app.stage;
const isProduction = stage === "production";

const config = isProduction
  ? {
      domain: "nexushr.com",
      tenantBaseDomain: "nexushr.com",
      minTasks: 2,
      maxTasks: 16,
      cpu: "1 vCPU" as const,
      memory: "2 GB" as const,
      capacity: "on-demand" as const,
      dbInstance: "t4g.small" as const,
      dbMultiAz: true,
    }
  : {
      domain: "staging.nexushr.com",
      tenantBaseDomain: "staging.nexushr.com",
      minTasks: 1,
      maxTasks: 4,
      cpu: "0.25 vCPU" as const,
      memory: "0.5 GB" as const,
      capacity: "spot" as const,
      dbInstance: "t4g.micro" as const,
      dbMultiAz: false,
    };

const allowedHosts = [
  config.domain,
  `*.${config.domain}`,
  `.${config.domain}`,
].join(",");

const csrfOrigins = [
  `https://${config.domain}`,
  `https://*.${config.domain}`,
].join(",");

export default $config({
  app(input) {
    return {
      name: "nexushr",
      removal: isProduction ? "retain" : "remove",
      protect: isProduction,
      home: "aws",
    };
  },
  async run() {
    const vpc = new sst.aws.Vpc("Vpc", { nat: "managed" });

    const mediaBucket = new sst.aws.Bucket("Media");

    const database = new sst.aws.Postgres("Database", {
      vpc,
      instance: config.dbInstance,
      multiAz: config.dbMultiAz,
      database: "nexushr",
    });

    const cluster = new sst.aws.Cluster("Cluster", { vpc });

    const djangoSecretKey = new sst.Secret("DjangoSecretKey");
    const stripeSecretKey = new sst.Secret("StripeSecretKey");
    const stripePublishableKey = new sst.Secret("StripePublishableKey");
    const stripeWebhookSecret = new sst.Secret("StripeWebhookSecret");

    const service = new sst.aws.Service("Web", {
      cluster,
      cpu: config.cpu,
      memory: config.memory,
      capacity: config.capacity,
      image: {
        context: "..",
        dockerfile: "../Dockerfile",
      },
      link: [database, mediaBucket],
      environment: {
        DJANGO_SETTINGS_MODULE: "hrms.settings.production",
        DJANGO_SECRET_KEY: djangoSecretKey.value,
        DJANGO_DEBUG: "false",
        DJANGO_ALLOWED_HOSTS: allowedHosts,
        TENANT_BASE_DOMAIN: config.tenantBaseDomain,
        TENANT_URL_SCHEME: "https",
        TENANT_PORT: "",
        CSRF_TRUSTED_ORIGINS: csrfOrigins,
        SESSION_COOKIE_DOMAIN: `.${config.tenantBaseDomain}`,
        SECURE_SSL_REDIRECT: "true",
        DB_HOST: database.host,
        DB_NAME: database.database,
        DB_USER: database.username,
        DB_PASSWORD: database.password,
        DB_PORT: $interpolate`${database.port}`,
        AWS_STORAGE_BUCKET_NAME: mediaBucket.name,
        AWS_S3_REGION_NAME: aws.getRegionOutput().name,
        STRIPE_SECRET_KEY: stripeSecretKey.value,
        STRIPE_PUBLISHABLE_KEY: stripePublishableKey.value,
        STRIPE_WEBHOOK_SECRET: stripeWebhookSecret.value,
        GUNICORN_WORKERS: isProduction ? "3" : "2",
        EMAIL_BACKEND: "django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST: $interpolate`email-smtp.${aws.getRegionOutput().name}.amazonaws.com`,
        EMAIL_PORT: "587",
        EMAIL_USE_TLS: "true",
      },
      loadBalancer: {
        domain: {
          name: config.domain,
          aliases: [`*.${config.domain}`],
          dns: sst.aws.dns(),
        },
        rules: [{ listen: "443/https", forward: "8000/http" }],
        health: {
          "8000/http": {
            path: "/healthz/",
            interval: "30 seconds",
            timeout: "5 seconds",
            healthyThreshold: 2,
            unhealthyThreshold: 3,
          },
        },
      },
      scaling: {
        min: config.minTasks,
        max: config.maxTasks,
        cpuUtilization: 60,
        memoryUtilization: 70,
      },
    });

    const albArnSuffix = service.nodes.loadBalancer.arnSuffix;

    new aws.cloudwatch.MetricAlarm("Alb5xx", {
      name: `${$app.name}-${stage}-alb-5xx`,
      alarmDescription: "ALB 5xx error rate is elevated",
      comparisonOperator: "GreaterThanThreshold",
      evaluationPeriods: 2,
      metricName: "HTTPCode_Target_5XX_Count",
      namespace: "AWS/ApplicationELB",
      period: 300,
      statistic: "Sum",
      threshold: 10,
      treatMissingData: "notBreaching",
      dimensions: {
        LoadBalancer: albArnSuffix,
      },
    });

    return {
      url: service.url,
      databaseHost: database.host,
      mediaBucket: mediaBucket.name,
    };
  },
});
