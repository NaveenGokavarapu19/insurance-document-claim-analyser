# insurance-document-claim-analyser
A poc for task 1.1 in skill builder course

## S3 path configuration

The project uses a simple S3 key builder based on the variables below.

- `project_name`: name of the project, such as `claim-analyser`
- `prefix`: team or environment prefix, such as `infra` or `dev`
- `object_path`: folder path before the file name, excluding both `project_name` and `prefix`; for this project the default is `resources/results`
- `object_name`: final file name, such as `file.txt`

Example:

```python
from src.utils import create_s3_prefix

object_path = "resources/results"
object_name = "Claim_Form.pdf"
create_s3_prefix(object_path=object_path, object_name=object_name)
# resources/results/Claim_Form.pdf
```

The helper joins the non-empty values in the order they are passed. For example:

```python
create_s3_prefix(
    project_name="claim-analyser",
    prefix="infra",
    object_path="resources/results",
    object_name="file.txt",
)
# claim-analyser/infra/resources/results/file.txt
```

where:

- `claim-analyser` = `project_name`
- `infra` = `prefix`
- `resources/results` = `object_path`
- `file.txt` = `object_name`

### Lambda environment variables

The Lambda app should read these values from environment variables with empty-string defaults:

- `PROJECT_NAME`
- `PREFIX`
- `OBJECT_PATH` (default: `resources/results`)
- `OBJECT_NAME`

The helper logic joins only the non-empty values in order:

```python
def create_s3_prefix(project_name="", prefix="", object_path="", object_name=""):
    total_values = (project_name, prefix, object_path, object_name)
    s3_parts_list = [value for value in total_values if value]
    return "/".join(s3_parts_list)
```
