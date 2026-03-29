# Deployment Guide

## How to deploy to production
1. Run `npm run build` to create production build
2. Push to main branch to trigger CI/CD pipeline
3. Monitor deployment in Jenkins dashboard
4. Verify health check at /api/health

## Rollback procedure
- Go to Jenkins > Select build > Click "Rollback"
- Or run: `kubectl rollout undo deployment/app`

## Environment variables
- NODE_ENV=production
- API_URL=https://api.company.com
- DB_HOST=postgres.internal
