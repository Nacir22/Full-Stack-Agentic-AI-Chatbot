# Déploiement AWS (à détailler en Phase 11)

Stub de documentation. Couvrira : création du repository **ECR**, configuration
de l'instance **EC2**, secrets GitHub, workflow **GitHub Actions**
(build → push ECR → pull EC2 → restart container → healthcheck).

```mermaid
graph LR
    A[git push main] --> B[GitHub Actions]
    B --> C[docker build]
    C --> D[push image -> AWS ECR]
    D --> E[SSH EC2]
    E --> F[docker pull + restart]
    F --> G[healthcheck /health]
```
