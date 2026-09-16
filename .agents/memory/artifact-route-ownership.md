---
name: Artifact route ownership
description: Routing rule for workspaces with multiple runnable Replit artifacts.
---

When multiple runnable artifacts are published together, a more-specific path
owned by another artifact can receive requests before a root web artifact does.
Each application must have unique service paths, and the intended frontend
artifact should explicitly own its API prefix when another service exists.

**Why:** A generic scaffold API service claiming `/api` caused public requests
to bypass the FastAPI application even though the FastAPI preview was healthy.

**How to apply:** Before publishing a multi-artifact workspace, inspect every
artifact manifest for overlapping or competing paths. Isolate unrelated
services under distinct prefixes and explicitly assign the product's API path
to the service that implements it.