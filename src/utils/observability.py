"""Simple logging setup using AWS Powertools."""
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.metrics import MetricUnit

logger = Logger(service="claim-analyser")
tracer = Tracer(service="claim-analyser")
metrics = Metrics(namespace="Claims", service="Analyser")

__all__ = ["logger", "tracer", "metrics", "MetricUnit"]