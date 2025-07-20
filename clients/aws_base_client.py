import os
import aioboto3
from typing import Optional


class AWSBaseClient:
    def __init__(self) -> None:
        self.aws_access_key_id: Optional[str] = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key: Optional[str] = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region_name: str = os.environ.get('AWS_REGION', 'us-east-1')
        self.session = aioboto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )