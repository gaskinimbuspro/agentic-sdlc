# Base images come from the internal registry, mirrored and pinned.
FROM forgejo-http.forgejo.svc.cluster.local:3000/OWNER/BASE@sha256:<mirrored base digest>
COPY app/app.py /app/app.py
USER 10001
EXPOSE 8080
CMD ["python3", "/app/app.py"]
