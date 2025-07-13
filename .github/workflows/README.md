# GitHub Actions Workflows

This directory contains automated workflows for the Resume Analyzer project.

## 🔄 Available Workflows

### 1. **CI/CD Pipeline** (`ci-cd.yml`)
**Triggers**: Push to main/develop, Pull Requests to main
- ✅ Runs Django tests with PostgreSQL
- ✅ Builds and tests Docker image  
- ✅ Performs Django system checks
- ✅ Auto-deploys to Render on main branch

### 2. **Security Scan** (`security.yml`)
**Triggers**: Weekly schedule, Push to main, Manual trigger
- 🔒 Scans dependencies for vulnerabilities
- 🔒 Runs security linter (Bandit)
- 🔒 Django deployment security checks
- 🔒 Generates security reports

### 3. **Code Quality** (`code-quality.yml`)
**Triggers**: Push to main/develop, Pull Requests
- 📝 Checks code formatting (Black)
- 📝 Verifies import sorting (isort)
- 📝 Runs linting (flake8)
- 📝 Analyzes code complexity

## 🚀 What Happens When You Push Code

1. **Automatic Testing**: All tests run in isolated environment
2. **Code Quality Checks**: Formatting, linting, complexity analysis
3. **Security Scanning**: Vulnerability and security issue detection
4. **Docker Build**: Ensures your app builds correctly
5. **Auto-Deployment**: Deploys to Render if all checks pass

## 📊 Workflow Status

You can view workflow status at:
`https://github.com/yourusername/resume-analyzer/actions`

## 🔧 Customization

### Adding Environment Variables
Add secrets in GitHub: Settings → Secrets and Variables → Actions

### Modifying Triggers
Edit the `on:` section in each workflow file

### Adding Steps
Add new steps under `steps:` in any job

## 📝 Reports Generated

- **Security Report**: Vulnerability scan results
- **Quality Report**: Code quality metrics
- **Test Results**: Django test outcomes
- **Build Logs**: Docker build information

## 🎯 Benefits

- **Early Bug Detection**: Catch issues before deployment
- **Consistent Quality**: Enforced code standards
- **Automated Security**: Regular vulnerability scanning
- **Zero-Downtime Deploys**: Tested code only reaches production
- **Documentation**: Automated reports and logs
