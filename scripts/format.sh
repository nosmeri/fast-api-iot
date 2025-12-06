#!/bin/bash
isort .
black .
autoflake --remove-all-unused-imports --in-place -r .