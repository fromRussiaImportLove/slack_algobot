#!/bin/bash
cd /code
exec celery -A algobot worker -B -l INFO