# Docker Build

## Overview

Docker Build is a command that builds Docker images from a Dockerfile and a "context". A build's context is the set of files located in the specified PATH or URL. The build process can refer to any of the files in the context.

The Docker build command builds Docker images from a Dockerfile. The docker build command builds an image from a Dockerfile and a context. The build's context is the files at a specified location PATH or URL. PATH is a directory on your local filesystem. URL is a Git repository location.

## Dockerfile

A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. Using docker build users can create an automated build that executes several command-line instructions in succession.

## Dockerfile Instructions

### FROM
The FROM instruction initializes a new build stage and sets the Base Image for subsequent instructions. As such, a valid Dockerfile must start with a FROM instruction. The image can be any valid image – it is especially easy to start by pulling an image from the Public Repositories.

### RUN
The RUN instruction will execute any commands in a new layer on top of the current image and commit the results. The resulting committed image will be used for the next step in the Dockerfile.

### CMD
The CMD instruction provides defaults for an executing container. These defaults can include an executable, or they can omit the executable, in which case you must specify an ENTRYPOINT instruction as well.

### LABEL
The LABEL instruction adds metadata to an image. A LABEL is a key-value pair. To include spaces within a LABEL value, use quotes and backslashes as you would in command-line parsing.

### EXPOSE
The EXPOSE instruction informs Docker that the container listens on the specified network ports at runtime. You can specify whether the port listens on TCP or UDP, and the default is TCP if the protocol is not specified.

### ENV
The ENV instruction sets the environment variable `<key>` to the value `<value>`. This value will be in the environment for all subsequent instructions in the build stage and can be replaced inline in many as well.

### ADD
The ADD instruction copies new files, directories or remote file URLs from `<src>` and adds them to the filesystem of the image at the path `<dest>`.

### COPY
The COPY instruction copies new files or directories from `<src>` and adds them to the filesystem of the container at the path `<dest>`.

### ENTRYPOINT
An ENTRYPOINT allows you to configure a container that will run as an executable.

### VOLUME
The VOLUME instruction creates a mount point with the specified name and marks it as holding externally mounted volumes from native host or other containers.

### USER
The USER instruction sets the user name (or UID) and optionally the user group (or GID) to use when running the image and for any RUN, CMD and ENTRYPOINT instructions that follow it in the Dockerfile.

### WORKDIR
The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile.

### ARG
The ARG instruction defines a variable that users can pass at build-time to the builder with the docker build command using the `--build-arg <varname>=<value>` flag.

### ONBUILD
The ONBUILD instruction adds to the image a trigger instruction to be executed at a later time, when the image is used as the base for another build.

### STOPSIGNAL
The STOPSIGNAL instruction sets the system call signal that will be sent to the container to exit.

### HEALTHCHECK
The HEALTHCHECK instruction tells Docker how to test a container to check that it is still working.

### SHELL
The SHELL instruction allows the default shell used for the shell form of commands to be overridden.

## Best Practices for Dockerfile

1. **Use .dockerignore** - Create a .dockerignore file to exclude files and directories that are not needed in the build context
2. **Use multi-stage builds** - Multi-stage builds allow you to use multiple FROM statements in your Dockerfile. Each FROM instruction can use a different base, and each of them begins a new stage of the build
3. **Minimize the number of layers** - Each instruction in a Dockerfile creates a new layer. To minimize the number of layers, combine RUN instructions where possible
4. **Use specific base images** - Instead of using generic base images, use specific versions to ensure reproducibility
5. **Use COPY instead of ADD** - Use COPY for simple file copying and ADD only when you need the additional features like URL downloading or tar extraction
6. **Use non-root users** - For security reasons, avoid running containers as root users
7. **Use health checks** - Implement health checks to monitor the status of your containers
8. **Use labels** - Add labels to your images for better organization and metadata

## Docker Build Context

The build context is the set of files located in the specified PATH or URL. The build process can refer to any of the files in the context. For example, your build can use a COPY instruction to reference a file in the context.

The build context is processed recursively. So, a PATH includes any subdirectories. The URL includes the repository and its submodules.

## Docker Build Cache

Docker uses a cache to speed up the build process. If a layer hasn't changed, Docker reuses the cached layer. This can significantly speed up builds, especially for large applications.

To take advantage of the cache, order your Dockerfile instructions from the least frequently changed to the most frequently changed. This way, the cache can be reused for the layers that don't change often.

## Docker Build Arguments

Build arguments are variables that can be passed to the build process. They are defined using the ARG instruction and can be used to customize the build process.

Build arguments are only available during the build process and are not available in the final image. They are useful for passing configuration values or version numbers to the build process.

## Docker Build Secrets

Docker Build supports build secrets, which allow you to securely pass sensitive information to the build process without storing it in the final image.

Build secrets are useful for passing API keys, passwords, or other sensitive information that is needed during the build process but should not be stored in the final image.

## Docker Build Performance

To improve Docker build performance:

1. Use .dockerignore to exclude unnecessary files
2. Use multi-stage builds to reduce image size
3. Use build cache effectively
4. Use specific base images
5. Minimize the number of layers
6. Use COPY instead of ADD when possible
7. Use build arguments for customization
8. Use build secrets for sensitive information

## Docker Build Examples

### Simple Node.js Application
```dockerfile
FROM node:14-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Multi-stage Build Example
```dockerfile
# Build stage
FROM node:14-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Python Application
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```
