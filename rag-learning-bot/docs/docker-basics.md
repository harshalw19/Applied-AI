# Docker Basics

Docker is a containerization platform that packages an application together with all
of its dependencies into a single portable unit called an image. This solves the classic
"it works on my machine" problem, because the image behaves identically everywhere.

A Dockerfile is the recipe. It is a plain text file listing the steps needed to build an
image: which base image to start from, which files to copy in, which commands to run,
and what should execute when the container starts.

An image is the packaged, read-only result of building a Dockerfile. It is frozen in time.
A container is a running instance of an image. One image can produce many containers,
in the same way one recipe can produce many meals.

Docker Hub is the public registry where prebuilt images live. When you write
FROM python:3.12-slim, Docker downloads that image from Docker Hub.

Layer caching is what makes Docker builds fast. Every instruction in a Dockerfile creates
a layer, and Docker reuses unchanged layers from cache. This is why you copy
requirements.txt and install dependencies BEFORE copying the rest of your source code:
dependencies change rarely, application code changes constantly.
