from pathlib import Path
import shutil
import boto3

SIM_S3 = Path("s3_sim")
SIM_S3.mkdir(parents=True, exist_ok=True)

def upload_sim(local_path, bucket_path="bucket/"):
    local = Path(local_path)
    target = SIM_S3 / bucket_path
    target.mkdir(parents=True, exist_ok=True)
    dest = target / local.name
    shutil.copy(local, dest)
    print(f"Copied {local} -> {dest}")

def upload_s3_real(local_path, bucket_name, key_prefix=""):
    s3 = boto3.client("s3")
    fname = Path(local_path).name
    key = f"{key_prefix.rstrip('/')}/{fname}".lstrip('/')
    s3.upload_file(str(local_path), bucket_name, key)
    print(f"Uploaded to s3://{bucket_name}/{key}")

if __name__ == "__main__":
    import glob
    files = glob.glob("outputs/*")
    for f in files:
        upload_sim(f, bucket_path="raw/outputs")
