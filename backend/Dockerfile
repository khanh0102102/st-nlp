FROM python:3.14.10-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install --no-cache-dir -r requirements.txt
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin stnlp
RUN mkdir -p /data/uploads /data/model-artifacts /data/audit && chown -R stnlp:stnlp /data /app

FROM base AS runtime

COPY --chown=stnlp:stnlp backend/app ./app

USER stnlp

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS test

COPY backend/requirements-dev.txt ./requirements-dev.txt
RUN python -m pip install --no-cache-dir -r requirements-dev.txt
COPY --chown=stnlp:stnlp backend/app ./app
COPY --chown=stnlp:stnlp backend/tests ./tests

USER stnlp

CMD ["pytest", "-q", "-p", "no:cacheprovider"]
