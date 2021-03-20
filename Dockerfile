FROM registry.gitlab.com/simpleagro-team/toolstacks/license_server:base
WORKDIR /app
COPY . /app/

ENV TZ=America/Sao_Paulo

ENTRYPOINT ["sh", "entrypoint.sh"]
