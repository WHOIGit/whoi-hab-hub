FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.11

# ensure libs are up to date
RUN : \
    && yum -y update --security \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && yum install git -y \
    :

WORKDIR ${LAMBDA_TASK_ROOT}
COPY ./*.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN : \
    && python3.11 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" \
    &&:

CMD ["app.lambda_handler"]