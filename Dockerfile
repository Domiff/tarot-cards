FROM python:3.14-slim-trixie AS builder

ENV PATH="/opt/uv/bin:$PATH"
RUN pip install --no-cache-dir --prefix=/opt/uv uv==0.12.5

ENV UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_NO_DEV=1

COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked


FROM python:3.14-slim-trixie

COPY --from=builder /usr/local /usr/local

WORKDIR /app

COPY . .

EXPOSE 8080
