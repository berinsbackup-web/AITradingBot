#!/bin/bash
echo "Running pytest with coverage..."
pytest --cov=core --cov-report=term-missing -v tests/
ret=$?
if [ $ret -ne 0 ]; then
  echo "Tests failed"
  exit $ret
fi

echo "Generating HTML coverage report..."
coverage html -d coverage_html_report
echo "HTML report generated at coverage_html_report/index.html"
