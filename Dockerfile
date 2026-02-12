FROM ubuntu:latest
LABEL authors="rodolphe"

ENTRYPOINT ["top", "-b"]
