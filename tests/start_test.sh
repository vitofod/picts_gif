#!/bin/bash

pytest --cov=picts_gif
coverage html -d ./cov_report_html