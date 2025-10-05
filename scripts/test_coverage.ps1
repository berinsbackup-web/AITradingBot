Write-Output "Running pytest with coverage..."
pytest --cov=core --cov-report=term-missing -v tests/
if ($LASTEXITCODE -ne 0) {
    Write-Error "Tests failed"
    exit $LASTEXITCODE
}

Write-Output "Generating HTML coverage report..."
coverage html -d coverage_html_report
Write-Output "HTML report generated at coverage_html_report/index.html"
