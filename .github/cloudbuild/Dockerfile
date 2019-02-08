ARG DEV_ENV_IMAGE

FROM ${DEV_ENV_IMAGE} AS db_builder
ARG NUM_PARALLEL_JOBS=1

COPY . /source
RUN cd /source && make -j${NUM_PARALLEL_JOBS} --output-sync=target --warn-undefined-variables build && make env
RUN bash -c ". /source/database/artix7/settings.sh; cd /source/fuzzers && make --output-sync=target --warn-undefined-variables ${BUILD_TYPE}"
#RUN find /source/database -mindepth 1 -maxdepth 1 -type d -exec /source/htmlgen/htmlgen.py --settings={}/settings.sh --output=/output/html \;
RUN mkdir -p /output/raw && find /source/database -mindepth 1 -maxdepth 1 -type d -exec cp -R {} /output/raw \;

FROM amd64/nginx:alpine
COPY --from=db_builder /output /usr/share/nginx/html
