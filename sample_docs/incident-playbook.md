# Incident Response Playbook

## Severity Levels
- **P0**: Complete outage - page on-call immediately
- **P1**: Major feature broken - respond within 30 min
- **P2**: Minor issue - respond within 4 hours

## On-Call Rotation
- Week 1: Backend team
- Week 2: Frontend team  
- Week 3: DevOps team

## Steps during an incident
1. Acknowledge alert in PagerDuty
2. Create incident channel in Slack: #incident-YYYY-MM-DD
3. Identify root cause using Datadog/Grafana
4. Apply fix or rollback
5. Write post-mortem within 48 hours

## Useful Commands
- Check logs: `kubectl logs -f deployment/app`
- Restart pod: `kubectl rollout restart deployment/app`
- Scale up: `kubectl scale deployment/app --replicas=5`
